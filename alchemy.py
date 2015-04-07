"""Alchemy.

Usage:
  alchemy.py <collection_path>
  alchemy.py --import <collection_path>
  alchemy.py --align <collection_path> <aligned_collection_path>
  alchemy.py (-h | --help)

Options:
  -h --help     Show this screen.
  --import      align and send annotations back to server

"""

from client.dispatcher import CorpusProcessor
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
    collection = arguments.get('<collection_path>')
    aligned_collection = arguments.get('<aligned_collection_path>')
    mode = 0
    if arguments.get('--align'):
        mode = 1
    elif arguments.get('--import'):
        mode = 2
    processor = CorpusProcessor()
    processor.process(collection, mode, aligned_collection)
