import json

# required suffix
SUFFIX = ('.json',)

# entity categories
ENTITY_CATEGORY = ('Gene', 'Disease', 'Mutation', 'Species', 'Chemical')

# relation categories
RELATION_CATEGORY = None


def process(filepath):
    json_file = filepath + '.json'

    # loop through all json lines
    with open(json_file, 'r') as handle:
        for i, line in enumerate(handle):
            line = line.strip()
            annotation = json.loads(line)

            # the json file may be big, use generator
            yield annotation

    # return annotations