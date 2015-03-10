import os
from submodules.annotation.readers import AnnParser
from submodules.annotation.utils import FileProcessor

# required suffix
SUFFIX = ('.ann', '.txt')

# entity categories
ENTITY_CATEGORY = ('SpecificDisease', 'Modifier', 'DiseaseClass', 'CompositeMention')

# relation categories
RELATION_CATEGORY = None


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