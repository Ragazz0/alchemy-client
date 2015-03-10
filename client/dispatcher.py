import os
import sys
import json
import urllib.parse
import urllib.request
import config
from align.align import AnnotationAligner
from multiprocessing import Pool


# parallel part
# python multiprocessing pool only supports module-level function
def post_annotation_slice(info):
    try:
        file_slice, curr_count, total_count, is_test = info

        # get annotations
        annotations = CorpusProcessor.process_files_slice(file_slice)
        read_count = len(annotations)
        imported_count = 0

        if not is_test:
            # get original text
            # dict_keys is not serializable
            doc_ids = list(annotations.keys())
            original_texts = CorpusProcessor.get_original_text(doc_ids)

            # align
            CorpusProcessor.align(annotations, original_texts)

            # post annotations
            response = CorpusProcessor.post_annotation(annotations)
            # print(response)
            imported_count = response.get('imported_doc')

        return read_count, imported_count, total_count
    except Exception as e:
        print(e)
        print(info)
        return None, None


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
                                        'relation_category_set': json.dumps(config.RELATION_CATEGORY),
                                        'entity_category_set': json.dumps(config.ENTITY_CATEGORY)}
        )
        return response

    @staticmethod
    def align(annotations, original_texts):
        for doc_id, annotation in annotations.items():
            original_text = original_texts.get(doc_id)
            if original_text is None:
                print('original text not found: ' + doc_id)
                continue
            AnnotationAligner.align(annotation, original_text)

    @staticmethod
    def process_files_slice(files):
        annotations = {}
        for f in files:
            slice_annotations = config.processor(f)
            annotations.update(slice_annotations)
        return annotations

    @staticmethod
    def get_files_slice(corpus_path, is_test):
        pivot = config.SUFFIX[0]
        step = config.STEP
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
                for suffix in config.SUFFIX[1:]:
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

    def process(self, corpus_path, is_test=True):
        """ read corpus, get original text from server, align, and send
        annotations back to server, using multiprocessing
        :param corpus_path: corpus folder path
        :type corpus_path: str
        :param is_test: if True, only read corpus without any server-side operation
        :type is_test: bool
        """

        if not is_test:
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
            response = self.post_entity_category(config.ENTITY_CATEGORY, config.USERNAME, config.PASSWORD,
                                                 config.COLLECTION)
            print(response)
            if not response.get('success'):
                print('Add entity category failed', file=sys.stderr)
                return

            # add relation category and argument roles
            print('Add relation category or argument role')
            response = self.post_relation_category(config.RELATION_CATEGORY, config.USERNAME, config.PASSWORD,
                                                   config.COLLECTION)
            print(response)
            if not response.get('success'):
                print('Add relation category or argument role failed', file=sys.stderr)
                return

        # start importing
        print('Start importing...')

        # import in parallel
        file_slices = self.get_files_slice(corpus_path, is_test)
        pool = Pool(processes=config.WORKER)

        results = pool.imap(post_annotation_slice, file_slices)

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

