import urllib.parse, urllib.request
import config
import json
from align.align import AnnotationAligner

class Corpus(object):
    
    api_doc_text = config.API_BASE + 'document'
    api_annotation = config.API_BASE + 'annotation'

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
    
    def post_annotation(self, annotations):
        packed = {}
        for doc_id, annotation in annotations.items():
            packed[doc_id] = annotation.dumps(annotation)
        
        entity_categories = json.dumps(config.ENTITY_CATEGORY)
        relation_categories = json.dumps(config.RELATION_CATEGORY)
        
        result = self.api(self.api_annotation, {'annotation_set':packed,
                                                'username': config.USERNAME,
                                                'password': config.PASSWORD, 
                                                'version': config.VERSION,
                                                'entity_category_set': entity_categories,
                                                'relation_category_set': relation_categories}
        )
        return result
    
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
            
        # return annotations