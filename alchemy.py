"""Alchemy.

Usage:
  alchemy.py <collection_path>...
  alchemy.py --import <collection_path>
  alchemy.py (-h | --help)

Options:
  -h --help     Show this screen.
  --import      align and send annotations back to server

"""

from client.dispatcher import CorpusProcessor
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
    collection = arguments.get('<collection_path>')[0]
    is_test = not arguments.get('--import')
    processor = CorpusProcessor()
    processor.process(collection, is_test=is_test)