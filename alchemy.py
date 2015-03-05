import config
import sys
from submodules.annotation.readers import *

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('alchemy.py corpus_path')
        sys.exit(0)
        
    corpus_path = sys.argv[1]
    corpus_reader = config.READER
    corpus_reader.parse_corpus(corpus_path, step=config.STEP)