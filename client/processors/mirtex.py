import os
from submodules.annotation.readers import AnnParser
from submodules.annotation.utils import FileProcessor
import json

# required suffix
SUFFIX = ('.ann', '.txt')

# entity categories
ENTITY_CATEGORY = ('Gene', 'MiRNA', 'Trigger')

# relation categories
RELATION_CATEGORY = (('MiRNA2Gene', ('Trigger', 'Agent', 'Theme')),
                     ('Gene2MiRNA', ('Trigger', 'Agent', 'Theme')))

remove_needle = {'luciferase reporter', 'luciferase reporters', 'luciferase'}


def handler(relation, fields):
    if len(fields) == 0:
        return
    json_str = fields[0]
    json_obj = json.loads(json_str)
    for key, value in json_obj.items():
        if isinstance(value, list):
            relation.property[key] = value[0]
        else:
            relation.property[key] = value


def process(filepath):
    parser = AnnParser(event_handler=handler, relation_handler=handler)
    annotations = []

    # read annotation
    ann_file = filepath + '.ann'
    annotation = parser.parse_file(ann_file)

    # get doc_id
    doc_id = os.path.basename(filepath)
    annotation.doc_id = doc_id
    annotation.filepath = filepath

    # remove sentence and certain entities
    annotation.entities = [e for e in annotation.entities if e.category != 'Sentence']
    to_remove_entity = [e for e in annotation.entities if e.text.lower() in remove_needle]
    annotation.entities = [e for e in annotation.entities if e not in to_remove_entity]
    to_remove_relation = []

    for relation in annotation.relations:
        relation.category = 'MiRNA2Gene'
        if 'direction' in relation.property:
            if relation.property.get('direction') == 'G2M':
                relation.category = 'Gene2MiRNA'
            del relation.property['direction']

        for arg in relation.arguments:
            if arg.role == 'Arg1':
                arg.role = 'Agent'
            elif arg.role == 'Arg2':
                arg.role = 'Theme'

            if arg.value in to_remove_entity:
                to_remove_relation.append(relation)
    
    # remove relations and trigger words
    annotation.relations = [r for r in annotation.relations if r not in to_remove_relation]
    to_remove_trigger = [a.value for r in to_remove_relation for a in r.arguments if a.role == 'Trigger']
    annotation.entities = [e for e in annotation.entities if e not in to_remove_trigger]

    if len(annotation.relations) == 0:
        return annotations

    # read text
    text_file = filepath + '.txt'
    text = FileProcessor.read_file(text_file)

    # store text with annotation
    annotation.text = text

    annotations.append(annotation.pack())
    return annotations