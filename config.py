# central database url, ending with /
API_BASE = 'http://127.0.0.1:8000/alchemy/'

# username and password
USERNAME = 'ligang'
PASSWORD = '123456'

# the processor for the files
# from client.processors import ann
# processor = ann.process
# from client.processors import rlims
# processor = rlims
from client.processors import jsonlines
processor = jsonlines

# parallel workers number
# recommended number is 4
WORKER = 6

# submit to server at each 1 file
# If a file contains less than DOC_STEP
# docs, you can increase the number.
# FILE_STEP = 1

# recommended range is 100-500 docs
# after each DOC_STEP docs are aligned, 
# they are sent to the server as a batch.
DOC_STEP = 500

# the collection name of the imported data
COLLECTION = 'Gennorm'

