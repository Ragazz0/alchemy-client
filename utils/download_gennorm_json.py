import urllib.parse, urllib.request
from submodules.annotation.annotate import Annotation
import json
import time


curr = 59151
step = 50
base_url = 'http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/abstract_ann.cgi?Disease=1&Gene=1&Chemical=1&Mutation=1&Species=1&pmid='

with open('data/Rlims/all_pmid_list.txt') as handle:
    text = handle.read().strip().replace('\r', '')
    pmids = text.split('\n')
    categories = set()

    while True:
        slice = pmids[curr:curr + step]
        if len(slice) == 0:
            break

        annotations = {}
        pmid_request = ','.join(slice)

        url = base_url + pmid_request
        request = urllib.request.Request(url)
        resource = urllib.request.urlopen(request)
        results = resource.read().decode('utf-8')

        blocks = results.strip().replace('\r', '').split('\n\n')

        for block in blocks:
            annotation = Annotation()

            lines = block.strip().split('\n')

            title = ''
            abs = ''

            try:
                title_line = lines[0].split('|')
                abs_line = lines[1].split('|')
    
                doc_id = title_line[0]
                if len(title_line) > 2:
                    title = title_line[2]
    
                if len(title_line) > 2:
                    abs = abs_line[2]
    
                if len(doc_id) == 0:
                    continue
    
                annotation.text = (title + ' ' + abs).strip()
    
                for line in lines[2:]:
                    fields = line.split('\t')
                    start = int(fields[1])
                    end = int(fields[2])
                    text = fields[3]
                    category = fields[4]
                    categories.add(category)
                    norm_ids = []
    
                    if end - start == len(text) - 1:
                        start -= 1
    
                    if annotation.text[start - 1:end - 1].lower() == text.lower():
                        start -= 1
                        end -= 1
    
                    if len(fields) > 5:
                        norm_ids = fields[5].split(',')
                    try:
                        entity = annotation.add_entity(category, start, end, text)
                        if len(norm_ids) > 0:
                            entity.property['norm_id'] = norm_ids
                    except Exception as e:
                        print(doc_id, e)
            except Exception as e:
                print(e)
                continue

            if len(annotation.entities) > 0:
                annotations[doc_id] = annotation

        with open('data/Gennorm/jsonlines.json', 'a') as handle:
            for doc_id, annotation in annotations.items():
                packed = annotation.pack()
                packed['doc_id'] = doc_id
                handle.write(json.dumps(packed))
                handle.write('\n')

        print(curr)
        curr += step
        time.sleep(2)
        # break

    print(categories)
    # TODO: there are errors in downloading gennorm results