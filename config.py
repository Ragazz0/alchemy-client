# central database url, ending with /
API_BASE = 'http://127.0.0.1:8080/alchemy/'

# username and password
USERNAME = 'ligang'
PASSWORD = '123456'

# the processor for the files
# from client.processors import ann
# processor = ann.process

from client.processors import rlims
processor = rlims

# parallel workers number
# recommended number is 4
WORKER = 4

# submit to server at each 100 PMIDs
# recommended range is 100-500
STEP = 1

# the collection name of the imported data
COLLECTION = 'test'

