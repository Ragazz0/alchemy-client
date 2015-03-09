import config
import sys
from client.dispatcher import CorpusProcessor

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('alchemy.py corpus_path')
        sys.exit(0)
        
    corpus_path = sys.argv[1]
    processor = CorpusProcessor()
    processor.process(corpus_path)