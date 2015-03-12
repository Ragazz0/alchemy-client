# Alchemy


### Motivation
There are various NLP tools that we can use to perform text-mining tasks, such as 
named entity recognition and relation extraction. However, many NLP tools modify the 
original text and make it very difficult to combine their results with other's.
For example, a gene mention recognition (GMR) tool may tokenize the text while a species 
recognition (SR) tool doesn't. 

The annotations on these two sentences can't be merged directly. We can't find the 
exact mention of the gene name from sentence 1 in sentence 2 because the text are 
different. What to do? Maybe we can first run the SR tool on the text before we apply 
the GMR tool. But what if the results we want to combine are from elsewhere? For example, 
another text-mining team releases a full-scale gene normalization result of PubMed, and we 
want to combine it with our protein-protein interacation text-mining results so that 
the protein names can be normalized. In this situation, we probably don't want to re-run the
PPI task using the gene normalization results. Moreover, making one task dependent on another 
task is a waste of time. We should be able to run two tasks in parallel and combine the results.

Alchemy is developed for solving this problem. It aligns altered text with the original text 
so that all the annotations can be mapped back to the original text.

### What is it?
alchemy does 3 things:
  1. align altered text back to original text, e.g., ""
  2. map annotation on altered text back to original text
  3. store fixed annotation into database

### Input format
The most convinient format is json. Put your document and annotation in a json object and put one json 
object per line in a file. The file should be with the suffix `.json`.
