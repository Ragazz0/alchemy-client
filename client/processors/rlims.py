from submodules.annotation.readers import RlimsVerboseReader

# required suffix
SUFFIX = ('.verbose',)

# entity categories
ENTITY_CATEGORY = ('Protein', 'Site', 'Trigger', 'SiteOther')

# relation categories
RELATION_CATEGORY = (
    ('Phosphorylation', ('Substrate',
                         'Kinase',
                         'Site',
                         'SiteOther',
                         'Trigger'))
    ,)

# 7085

def process(filepath):
    parser = RlimsVerboseReader()
    annotations_packed = []

    # read annotation and text
    verbose_file = filepath + '.verbose'
    tuples = parser.parse_file(verbose_file)
    annotations = parser.to_ann(tuples)

    for annotation in annotations:
        annotations_packed.append(annotation.pack())

    return annotations_packed
    # TODO: there are errors importing Rlims results from lysine
    # they should be fixed by iss-1, since they are IndexError