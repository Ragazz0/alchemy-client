from submodules.annotation.readers import AnnParser
from submodules.annotation.utils import FileProcessor


def process(files):
    parser = AnnParser()
    # loop through all the files
    
    annotations = {}
    for doc_id, f in files.items():
        ann_file = f + '.ann'
        annotation = parser.parse_file(ann_file)
        text_file = f + '.txt'
        text = FileProcessor.read_file(text_file)
        annotation.text = text
        annotations[doc_id] = annotation
    
    return annotations