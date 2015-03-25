import urllib.parse, urllib.request
from submodules.annotation.annotate import Annotation
import json
import time

import sys

import codecs

# replace utf-8 char with space, since in gennorm results,
# the abstracts seems encoded with utf-8, the entities are
# encoded with ascii, with utf-8 chars repalced with spaces
def replace_with_space(e):
    return ' ', e.start + 1


codecs.register_error('replace_space', replace_with_space)

pmid_file = sys.argv[1]
gennorm_file = sys.argv[2]

curr = 0
step = 50
base_url = 'http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/abstract_ann.cgi?Disease=1&Gene=1&Chemical=1&Mutation=1&Species=1&pmid='

with open(pmid_file) as handle:
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
        results = resource.read().decode('ascii', errors="replace_space")

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

                    if annotation.text[start:end].lower() != text.lower():
                        for i in range(1, 5):
                            if annotation.text[start - i:end].lower() == text.lower():
                                start -= i
                                break
                            elif annotation.text[start:end - i].lower() == text.lower():
                                end -= i
                                break
                            elif annotation.text[start - i:end - i].lower() == text.lower():
                                start -= i
                                end -= i
                                break
                            elif annotation.text[start + i:end + i].lower() == text.lower():
                                start += i
                                end += i
                                break

                        if start < 0:
                            start = 0
                        elif start >= len(annotation.text):
                            print(doc_id, "start > len(text)", line)
                            continue
                        if end < 0:
                            print(doc_id, "end < 0", line)
                            continue
                        elif end > len(annotation.text):
                            end = len(annotation.text)

                    # in case gennorm changes cases
                    text = annotation.text[start:end]

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

        with open(gennorm_file, 'a') as handle:
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
