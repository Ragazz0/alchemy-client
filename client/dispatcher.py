import os
import sys
import json
import urllib.parse
import urllib.request
import config
from align.align import AnnotationAligner
from multiprocessing import Pool
from multiprocessing import current_process
import types
import traceback
from submodules.annotation.annotate import Annotation
from submodules.annotation.writers import AnnWriter
from submodules.annotation.utils import FileProcessor


def post_annotation_slice(info):
    # parallel part
    # python multiprocessing pool only supports module-level function
    try:
        annotations, countfile, mode, args = info

        is_read = (mode == 0)
        is_align = (mode == 1)
        is_import = (mode == 2)

        # get annotations
        read_count = 0
        imported_count = 0
        current = current_process()
        read_count += len(annotations)
        if is_import or is_align:
            # get original text
            # dict_keys is not serializable
            doc_ids = [a.get('doc_id') for a in annotations if a.get('doc_id') is not None]
            original_texts = CorpusProcessor.get_original_text(doc_ids)

            # align
            CorpusProcessor.align(annotations, original_texts)

            if is_import:
                # post annotations
                response = CorpusProcessor.post_annotation(annotations)
                # print(response)
                imported_count = response.get('imported_doc')

            elif is_align:
                aligned_corpus_path = args.get('aligned_corpus_path')
                CorpusProcessor.save_annotation(annotations, aligned_corpus_path)                

        # print("%s: read %s docs / imported %s docs / processed %s file" %
        #       (current.name, read_count, imported_count, countfile))
        return read_count, imported_count, countfile
    except Exception:
        traceback.print_exc()
        return None, None, None


class CorpusProcessor(object):
    API_DOCUMENT = config.API_BASE + 'document'
    API_ANNOTATION = config.API_BASE + 'annotation'
    API_USER = config.API_BASE + 'user'
    API_COLLECTION = config.API_BASE + 'collection'
    API_ENTITY_CATEGORY = config.API_BASE + 'entity_category'
    API_RELATION_CATEGORY = config.API_BASE + 'relation_category'

    def __init__(self):
        self.parser = None

    def parse_corpus(self, corpus_path, step=100):
        raise NotImplementedError

    @staticmethod
    def api(url, data):
        data = urllib.parse.urlencode(data)
        data = data.encode('utf-8')
        request = urllib.request.Request(url, data)
        resource = urllib.request.urlopen(request)
        json_text = resource.read().decode('utf-8')
        json_data = json.loads(json_text)
        return json_data

    @staticmethod
    def get_original_text(doc_ids):
        doc_ids_json = json.dumps(doc_ids)
        text = CorpusProcessor.api(CorpusProcessor.API_DOCUMENT, {'document_set': doc_ids_json})
        return text

    def post_user(self, username, password):
        response = self.api(self.API_USER, {'username': username, 'password': password})
        return response

    def post_collection(self, collection, username, password):
        response = self.api(self.API_COLLECTION, {'username': username,
                                                  'password': password,
                                                  'collection': collection})
        return response

    def post_entity_category(self, entity_categories, username, password, collection):
        response = self.api(self.API_ENTITY_CATEGORY,
                            {'username': username,
                             'password': password,
                             'collection': collection,
                             'entity_category_set': json.dumps(entity_categories)})
        return response

    def post_relation_category(self, relation_categories, username, password, collection):
        response = self.api(self.API_RELATION_CATEGORY,
                            {'username': username,
                             'password': password,
                             'collection': collection,
                             'relation_category_set': json.dumps(relation_categories)})
        return response

    @staticmethod
    def post_annotation(annotations):
        response = CorpusProcessor.api(CorpusProcessor.API_ANNOTATION,
                                       {'annotation_set': json.dumps(annotations),
                                        'username': config.USERNAME,
                                        'password': config.PASSWORD,
                                        'collection': config.COLLECTION,
                                        'relation_category_set': json.dumps(config.processor.RELATION_CATEGORY),
                                        'entity_category_set': json.dumps(config.processor.ENTITY_CATEGORY)}
        )
        return response

    @staticmethod
    def save_annotation(annotations, aligned_corpus_path):
        writer = AnnWriter()
        for packed in annotations:
            annotation = Annotation.loads(packed, 'dict')
            doc_id = annotation.doc_id
            file_path = os.path.join(aligned_corpus_path, doc_id+'.txt')
            FileProcessor.write_file(file_path, annotation.text)
            file_path = os.path.join(aligned_corpus_path, doc_id+'.ann')
            writer.write(file_path, annotation)

    @staticmethod
    def align(annotations, original_texts):
        for annotation in annotations:
            doc_id = annotation.get('doc_id')
            original_text = original_texts.get(doc_id)
            if original_text is None:
                print('original text not found: ' + doc_id)
                continue
            AnnotationAligner.align(annotation, original_text)

    @staticmethod
    def process_files_slice(files):
        annotations = {}
        for f in files:
            slice_annotations = config.processor.process(f)
            annotations.update(slice_annotations)
        return annotations

    @staticmethod
    def get_files_all(corpus_path):
        pivot = config.processor.SUFFIX[0]
        for root, _, files in os.walk(corpus_path):
            for f in files:
                if not f.endswith(pivot):
                    continue

                doc_id = f[:-len(pivot)]
                root_path = os.path.join(root, doc_id)

                all_exists = True
                for suffix in config.processor.SUFFIX[1:]:
                    if not os.path.isfile(root_path + suffix):
                        all_exists = False
                        break

                if not all_exists:
                    continue

                yield root_path

    @staticmethod
    def get_files_slice(corpus_path, is_test):
        # get file stream
        # not used if use annotation stream
        pivot = config.processor.SUFFIX[0]
        step = config.FILE_STEP
        curr_slice = []
        curr_count = 0
        total_count = 0
        for root, _, files in os.walk(corpus_path):
            for f in files:
                if not f.endswith(pivot):
                    continue

                doc_id = f[:-len(pivot)]
                root_path = os.path.join(root, doc_id)

                all_exists = True
                for suffix in config.processor.SUFFIX[1:]:
                    if not os.path.isfile(root_path + suffix):
                        all_exists = False
                        break

                if not all_exists:
                    continue

                curr_slice.append(root_path)
                curr_count += 1
                total_count += 1

                if curr_count >= step:
                    yield curr_slice, curr_count, total_count, is_test
                    curr_slice = []
                    curr_count = 0

        if len(curr_slice) > 0:
            yield curr_slice, curr_count, total_count, is_test

    @staticmethod
    def get_annotations_slice(files_slice, mode, args):
        """ a generator for annotations stream
        :param files_slice: a list of file ids
        :type files_slice: list | generator
        :return: list of annotations
        :rtype: list
        """

        need_stream = []
        count = 0
        for f in files_slice:
            slice_annotations = config.processor.process(f)
            need_length = config.DOC_STEP - len(need_stream)
            count += 1
            if isinstance(slice_annotations, types.GeneratorType):
                while True:
                    try:
                        for _ in range(need_length):
                            need_stream.append(next(slice_annotations))
                        yield need_stream, count, mode, args
                        need_stream = []
                        need_length = config.DOC_STEP
                    except StopIteration:
                        break
            elif isinstance(slice_annotations, list):
                while True:
                    need_stream += slice_annotations[:need_length]
                    if len(need_stream) < config.DOC_STEP:
                        break
                    else:
                        yield need_stream, count, mode, args
                        need_stream = []
                        # shrink list
                        slice_annotations = slice_annotations[need_length:]
                        # reset need_length
                        need_length = config.DOC_STEP
            else:
                raise TypeError('process() should return list or generator.')

        yield need_stream, count, mode, args

    def process(self, corpus_path, mode=0, aligned_corpus_path=None):
        """ read corpus, get original text from server, align, and send
        annotations back to server, using multiprocessing
        :param corpus_path: corpus folder path
        :type corpus_path: str
        :param is_test: 0: read corpus; 1: align corpus; 2: import corpus
        :type is_test: int
        """
        is_read, is_align, is_import = False, False, False
        if mode == 0:
            is_read = True
        elif mode == 1:
            is_align = True
        elif mode == 2:
            is_import = True

        if is_import:
            # add/verify user
            print('Add or verify user ' + config.USERNAME)
            response = self.post_user(config.USERNAME, config.PASSWORD)
            print(response)
            if not response.get('success'):
                print('Add or verify user failed', file=sys.stderr)
                return

            # add version
            print('Add collection ' + config.COLLECTION)
            response = self.post_collection(config.COLLECTION, config.USERNAME, config.PASSWORD)
            print(response)
            if not response.get('success'):
                print('Add collection failed', file=sys.stderr)
                return

            # add entity category
            print('Add entity category')
            response = self.post_entity_category(config.processor.ENTITY_CATEGORY,
                                                 config.USERNAME, config.PASSWORD,
                                                 config.COLLECTION)
            print(response)
            if not response.get('success'):
                print('Add entity category failed', file=sys.stderr)
                return

            # add relation category and argument roles
            print('Add relation category or argument role')
            response = self.post_relation_category(config.processor.RELATION_CATEGORY,
                                                   config.USERNAME, config.PASSWORD,
                                                   config.COLLECTION)
            print(response)
            if not response.get('success'):
                print('Add relation category or argument role failed', file=sys.stderr)
                return

        # start importing
        print('Start importing...')

        pool = Pool(processes=config.WORKER)

        # import in parallel
        # use file stream
        # file_slices = self.get_files_slice(corpus_path, is_test)

        # use docs stream
        files_all = self.get_files_all(corpus_path)
        annotations_stream = self.get_annotations_slice(files_all, mode, 
                                                        {"aligned_corpus_path":aligned_corpus_path})
        results = pool.imap(post_annotation_slice, annotations_stream)

        imported_total_count = 0
        read_total_count = 0
        for read_count, imported_count, total_count in results:
            if imported_count is None:
                print('Exception happens')
            else:
                read_total_count += read_count
                imported_total_count += imported_count
                print("read %s docs / imported %s docs / processed %s files" % (
                    read_total_count, imported_total_count, total_count))
                # print("read %s docs / imported %s docs" % (
                #     read_total_count, imported_total_count))

