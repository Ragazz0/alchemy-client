import json
from submodules.annotation.annotate import Annotation

docs = {}

with open('data/Gennorm/Gennorm_TIAB.csv', encoding='utf-8') as tiab:
    for line in tiab:
        fields = line.strip('\n\r').split('\t')
        doc_id = fields[1]
        title = fields[2]
        abstract = fields[3]

        if doc_id == '' or (title == '' and abstract == ''):
            continue

        docs[doc_id] = Annotation()

        docs[doc_id].text = (title.strip() + ' ' + abstract.strip()).strip()

    categories = set()
    with open('data/Gennorm/Gennorm_GN.csv', encoding='utf-8') as gn:
        for line in gn:
            fields = line.strip('\n\r').split('\t')
            doc_id = fields[1]
            text = fields[2]
            nid = fields[4]
            start = int(fields[5])
            end = int(fields[6])
            category = fields[3]

            if '' in [doc_id, text, nid, start, end, category]:
                continue
            
            if end - start == len(text) - 1:
                start -= 1
            if category != 'Gene':
                continue
            categories.add(category)
            try:
                entity = docs[doc_id].add_entity(category, start, end, text)
                if 'norm_id' in entity.property:
                    entity.property['norm_id'].append(nid)
                else:
                    entity.property['norm_id'] = [nid]
            except Exception as e:
                print(doc_id, e)
                
    print(categories)
    with open('data/Gennorm/jsonlines.json', 'w') as handle:
        for doc_id, annotation in docs.items():
            packed = annotation.pack()
            packed['doc_id'] = doc_id
            handle.write(json.dumps(packed))
            handle.write('\n')