import os
import sys
import json
import urllib.parse, urllib.request
import config
from align.align import AnnotationAligner


class Corpus(object):
    api_doc_text = config.API_BASE + 'document'
    api_annotation = config.API_BASE + 'annotation'
    api_user = config.API_BASE + 'user'
    api_version = config.API_BASE + 'version'
    api_entity_category = config.API_BASE + 'entity_category'
    api_relation_category = config.API_BASE + 'relation_category'

    def __init__(self):
        self.parser = None

    def parse_corpus(self, corpus_path, step=100):
        raise NotImplementedError

    def api(self, url, data):
        data = urllib.parse.urlencode(data)
        data = data.encode('utf-8')
        request = urllib.request.Request(url, data)
        resource = urllib.request.urlopen(request)
        json_text = resource.read().decode('utf-8')
        json_data = json.loads(json_text)
        return json_data

    def get_original_text(self, doc_ids):
        doc_ids_json = json.dumps(doc_ids)
        text = self.api(self.api_doc_text, {'document_set': doc_ids_json})
        return text

    def post_user(self, username, password):
        response = self.api(self.api_user, {'username': username, 'password': password})
        return response

    def post_version(self, version, username, password):
        response = self.api(self.api_version, {'username': username,
                                               'password': password,
                                               'version': version})
        return response

    def post_entity_category(self, entity_categories, username, password, version):
        response = self.api(self.api_entity_category,
                            {'username': username,
                             'password': password,
                             'version': version,
                             'entity_category_set': json.dumps(entity_categories)})
        return response

    def post_relation_category(self, relation_categories, username, password, version):
        response = self.api(self.api_relation_category,
                            {'username': username,
                             'password': password,
                             'version': version,
                             'relation_category_set': json.dumps(relation_categories)})
        return response

    def post_annotation(self, annotations):
        response = self.api(self.api_annotation, {'annotation_set': json.dumps(annotations),
                                                  'username': config.USERNAME,
                                                  'password': config.PASSWORD,
                                                  'version': config.VERSION,
                                                  'relation_category_set': json.dumps(config.RELATION_CATEGORY),
                                                  'entity_category_set': json.dumps(config.ENTITY_CATEGORY)}
        )
        return response

    def align(self, annotations):
        # dict_keys is not serializable
        doc_ids = list(annotations.keys())
        original_texts = self.get_original_text(doc_ids)

        for doc_id, annotation in annotations.items():
            original_text = original_texts.get(doc_id)
            if original_text is None:
                raise IOError('original text not found')
            text = annotation.text
            AnnotationAligner.align(annotation, text, original_text)
            annotation.text = original_text

    def process(self, corpus_path):
        # add/verify user
        print('Add or verify user ' + config.USERNAME)
        response = self.post_user(config.USERNAME, config.PASSWORD)
        print(response)
        if not response.get('success'):
            print('Add or verify user failed', file=sys.stderr)
            return

        # add version
        print('Add version ' + config.VERSION)
        response = self.post_version(config.VERSION, config.USERNAME, config.PASSWORD)
        print(response)
        if not response.get('success'):
            print('Add version failed', file=sys.stderr)
            return

        # add entity category
        print('Add entity category')
        response = self.post_entity_category(config.ENTITY_CATEGORY, config.USERNAME, config.PASSWORD, config.VERSION)
        print(response)
        if not response.get('success'):
            print('Add entity category failed', file=sys.stderr)
            return

        # add relation category and argument roles
        print('Add relation category or argument role')
        response = self.post_relation_category(config.RELATION_CATEGORY, config.USERNAME, config.PASSWORD,
                                               config.VERSION)
        print(response)
        if not response.get('success'):
            print('Add relation category or argument role failed', file=sys.stderr)
            return

        print('Start importing...')
        pivot = config.SUFFIX[0]
        step = config.STEP
        curr_slice = {}
        curr_count = 0
        total_count = 0
        for root, _, files in os.walk(corpus_path):
            for f in files:
                # if f != '1347968.ann':
                # continue
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

                curr_slice[doc_id] = root_path
                curr_count += 1
                total_count += 1

                if curr_count >= step:
                    annotations = config.PROCESSOR(curr_slice)
                    self.align(annotations)
                    packed = {}
                    for doc_id, annotation in annotations.items():
                        annotation.text = ''
                        packed[doc_id] = annotation.pack()

                    print("%s-%s docs" % (total_count - step + 1, total_count))
                    response = self.post_annotation(packed)
                    print(response)
                    curr_slice = {}
                    curr_count = 0

        # import left documents
        if len(curr_slice) > 0:
            annotations = config.PROCESSOR(curr_slice)
            self.align(annotations)
            packed = {}
            for doc_id, annotation in annotations.items():
                annotation.text = ''
                packed[doc_id] = annotation.pack()

            print("%s-%s docs" % (total_count - step, total_count))
            response = self.post_annotation(packed)
            print(response)