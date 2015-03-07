import json


def process(files):
    # loop through all the files

    annotations = {}
    for doc_id, f in files.items():
        json_file = f + '.json'
        with open(json_file) as handle:
            annotation = json.load(handle)
            annotations[doc_id] = annotation

    return annotations