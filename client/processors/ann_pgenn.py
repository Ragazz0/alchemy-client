import os
from submodules.annotation.readers import AnnParser
from submodules.annotation.utils import FileProcessor

# required suffix
SUFFIX = ('.ann', '.txt')

# entity categories
ENTITY_CATEGORY = ('Gene', 'Species')

# relation categories
RELATION_CATEGORY = None


def handler(entity, fields):
    if len(fields) == 0:
        return
    try:
        uniprot_id = fields[0]
        entrez_id = fields[2]
        entity.property['uniprot_id'] = uniprot_id
        entity.property['entrez_id'] = entrez_id
    except Exception:
        print("entity extra fields error:" + str(fields))


def process(filepath):
    parser = AnnParser(entity_handler=handler)
    annotations = []

    # read annotation
    ann_file = filepath + '.ann'
    annotation = parser.parse_file(ann_file)

    # get doc_id
    doc_id = os.path.basename(filepath)
    annotation.doc_id = doc_id
    annotation.filepath = filepath

    # read text
    text_file = filepath + '.txt'
    text = FileProcessor.read_file(text_file)

    # store text with annotation
    annotation.text = text

    annotations.append(annotation.pack())
    return annotations