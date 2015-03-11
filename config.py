# central database url, ending with /
API_BASE = 'http://127.0.0.1:8080/alchemy/'

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
WORKER = 4

# submit to server at each 1 file
# If a file contains less than DOC_STEP 
# docs, you can increase the number.
FILE_STEP = 2

# recommended range is 100-500 docs
# after each DOC_STEP docs are aligned, 
# they are sent to the server as a batch.
DOC_STEP = 150

# the collection name of the imported data
COLLECTION = 'Gennorm'

