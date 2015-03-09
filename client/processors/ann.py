import os
from submodules.annotation.readers import AnnParser
from submodules.annotation.utils import FileProcessor


def process(filepath):
    parser = AnnParser()
    annotations = {}

    # read annotation
    ann_file = filepath + '.ann'
    annotation = parser.parse_file(ann_file)

    # read text
    text_file = filepath + '.txt'
    text = FileProcessor.read_file(text_file)

    # store text with annotation
    annotation.text = text

    # get doc_id
    doc_id = os.path.basename(filepath)
    annotations[doc_id] = annotation.pack()

    return annotations