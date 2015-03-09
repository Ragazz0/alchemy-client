import json


def process(filepath):
    annotations = {}
    json_file = filepath + '.json'

    # loop through all json lines
    with open(filepath, 'r') as handle:
        for i, line in enumerate(handle):
            line = line.strip()
            annotation = json.loads(line)

            # get doc_id
            doc_id = annotation.get('doc_id')
            if doc_id is None:
                print('doc_id not found at line ' + str(i))
                continue

            annotations[doc_id] = annotation

    return annotations