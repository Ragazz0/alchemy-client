# alchemy-client
merge text annotations from different NLP tools

### What is it?
alchemy does 3 things:
  1. align altered text back to original text
  2. adjust annotation on altered text back to original text
  3. store fixed annotation into database

### Input format
The most convinient format is json. Put your document and annotation in a json object and put one json 
object per line in a file. The file should be with the suffix `.json`.
