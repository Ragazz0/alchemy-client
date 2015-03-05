# central database url, ending with /
API_BASE = 'http://127.0.0.1:8000/alchemy/'

# username and password
USERNAME = 'ligang'
PASSWORD = '123456'

# the reader used to read the files
# available readers: AnnReader, JsonReader, RlimsReader, SGMLReader
from client.ann_corpus import AnnCorpus

READER = AnnCorpus()

# submit to server at each 100 PMIDs
STEP = 100

# the version of the imported data
VERSION = 'test'

# entity categories
ENTITY_CATEGORY = ('SpecificDisease', 'Modifier', 'DiseaseClass', 'CompositeMention')

# relation categories
RELATION_CATEGORY = (
    ('Phosphorylation', (('Substrate', 'Gene'),
                         ('Kinase', 'Gene'),
                         ('Site', 'Site'),
                         ('Trigger', 'Trigger')))
    ,)