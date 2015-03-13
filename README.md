# Alchemy


### Motivation
There are various NLP tools that we can use to perform text-mining tasks, such as named entity recognition and relation extraction. However, many NLP tools modify the original text and make it very difficult to combine their results with other's. For example, a gene mention recognition (GMR) tool may tokenize the text by inserting extra space around the parentheses, while a disease recognition (DR) tool does not change the text.

1. **Microtubule associated protein ( MAP ) tau** is abnormally hyperphosphorylated in Alzheimers disease ( AD ) and related tauopathies .
2. Microtubule associated protein (MAP) tau is abnormally hyperphosphorylated in **Alzheimers disease (AD)** and related tauopathies.

The annotations on these two sentences can't be merged directly. We can't find the exact mention of the gene name from sentence 1 in sentence 2 because the text are different, nor can we find the disease name in sentence 1. What to do? Maybe we can first run the DR tool on the text before we apply the GMR tool. But what if the results we want to combine are from elsewhere? For example, another text-mining team releases a full-scale gene normalization result of PubMed, and we want to combine it with our protein-protein interacation text-mining results so that the protein names can be normalized. In this situation, we probably don't want to re-run the PPI task using the gene normalization results. Moreover, making one task dependent on another for this reason is a waste of time. We should be able to run two tasks in parallel and combine the results.

Alchemy is developed for solving this problem. It aligns altered text with the original so that all the annotations can be mapped back to the original. The text modification pattern in the above example is simple. However, in reality we saw many more complicated modifications. To name a few, two words' order were switched, marker or bug charaters were inserted in the text, a whole sentence was deleted, etc. Alchemy is designed to handle all these situations.

### What it does?
1. align altered text with the original text
2. map annotation on altered text back to original text
3. store the aligned annotation into database or local files

### Input format
JSON format is very easy to use for storing and exchanging data between programs, and is human-readable to some extent. Here I use JSON for input text and annotation. Put your document and annotation in a json object and put one json object per line in a file. The file should be with the suffix `.json`.

The attributes in the json object are listed below. More details can be found in wiki.
```json
{  
   "doc_id":"19020281",
   "property":{  
      "date":"2008 Dec"
   },
   "entity_set":[
      {
         "id":"Tk4254jybdi",
         "start":883,
         "end":898,
         "text":"phosphorylation",
         "category":"Trigger",
         "property":{
            "pos":"NN"
         }
      },
      {
         "id":"Tbz20gh1f3w",
         "start":911,
         "end":914,
         "text":"AKT",
         "category":"Protein",
         "property":{
            "entrez_id":"5594"
         }
      }
   ],
   "relation_set":[
      {
         "id":"Rosmhgt81t1",
         "category":"Phosphorylation",
         "argument_set":[
            [
               "Trigger",
               "Tk4254jybdi"
            ],
            [
               "Substrate",
               "Tbz20gh1f3w"
            ]
         ],
         "property":{
            "rule":"NP-of-NP"
         }
      }
   ],
   "text":"TI - Complement C5a receptors in the pituitary gland : expression and function . AB - Communication between the immune and endocrine system is important for the control of inflammation that is primarily mediated through the hypothalamic-pituitary-adrenal axis . The innate immune system rapidly responds to pathogens by releasing complement proteins that include the anaphylatoxins C3a and C5a . We previously reported the existence of C3a receptors in the anterior pituitary gland and now describe the presence of C5a receptors in the gland . C5a and its less active derivative ( C5adR ) can bind to its own receptor and to another receptor called C5L2 . Using RT-PCR and immunocytochemistry , C5a receptors and C5L2 were demonstrated in the rat anterior pituitary gland and in several rodent anterior pituitary cell lines . Western blotting analysis showed that C5a stimulated the phosphorylation of MAPK and AKT but not p38 ."
}
```

### When to use?
When you want to merge text annotations from different sources. Note that you don't need to use Alchemy during the text-mining task. Only the final results are necessary to be aligned back to the original text.
