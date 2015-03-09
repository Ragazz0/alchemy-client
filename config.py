# central database url, ending with /
API_BASE = 'http://127.0.0.1:8000/alchemy/'

# username and password
USERNAME = 'ligang'
PASSWORD = '123456'

# the processor for the files
# from client.processors import ann
# processor = ann.process

from client.processors import rlims
processor = rlims.process

# parallel workers number
# recommended number is 4
WORKER = 4

# submit to server at each 100 PMIDs
# recommended range is 100-500
STEP = 100

# the version of the imported data
VERSION = 'test'

# required suffix
# SUFFIX = ('.ann', '.txt')
SUFFIX = ('.verbose',)

# entity categories
# ENTITY_CATEGORY = ('SpecificDisease', 'Modifier', 'DiseaseClass', 'CompositeMention')
ENTITY_CATEGORY = ('Protein', 'Site', 'Trigger')

# relation categories
RELATION_CATEGORY = (
    ('Phosphorylation', ('Substrate',
                         'Kinase', 
                         'Site', 
                         'Trigger'))
    ,)