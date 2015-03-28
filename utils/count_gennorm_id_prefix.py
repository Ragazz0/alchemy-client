import sys
import json
from submodules.annotation.annotate import Annotation

numbers = tuple([str(i) for i in range(10)])
id_prefix = set()

json_file = sys.argv[1]
with open(json_file, 'r') as handle:
    for line in handle:
        line = line.strip()
        annotation = Annotation.loads(line, 'json')
        
        genes = [e for e in annotation.entities if e.category == 'Gene']
        for gene in genes:
            norm_id = gene.property.get('norm_id')
            if norm_id is not None:
                for nid in norm_id:
                    if not nid.startswith(numbers):
                        prefix = nid.split(':')[0]
                        id_prefix.add(prefix)

print(id_prefix)
