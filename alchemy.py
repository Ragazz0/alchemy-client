import config
import sys
from client.corpus import Corpus

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('alchemy.py corpus_path')
        sys.exit(0)
        
    corpus_path = sys.argv[1]
    corpus = Corpus()
    corpus.process(corpus_path)