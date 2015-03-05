import os
from .corpus import Corpus
from submodules.annotation.readers import AnnParser
from submodules.annotation.utils import FileProcessor


class AnnCorpus(Corpus):
    def __init__(self):
        super(AnnCorpus, self).__init__()
        self.parser = AnnParser()

    def parse_corpus(self, corpus_path, step=100):
        # loop through all the files
        annotations = {}
        count = 0
        for root, _, files in os.walk(corpus_path):
            for f in files:
                if not f.endswith('.ann'):
                    continue
                
                count += 1
                doc_id = f[:-4]
                ann_file = os.path.join(root, f)
                annotation = self.parser.parse_file(ann_file)
                text_file = os.path.join(root, doc_id + '.txt')
                text = FileProcessor.read_file(text_file)
                annotation.text = text
                annotations[doc_id] = annotation

                if count % 100 == 0:
                    print(count)
                    self.align(annotations)
                    result = self.post_annotation(annotations)
                    print(result)
                    annotations = {}