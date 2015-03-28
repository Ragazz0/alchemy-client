import json
import sys
from submodules.annotation.annotate import Annotation

gene_norms = {}
fixed_docs = set()
added_genes = 0

print('loading gennorm GN results from CSV')
with open('data/Gennorm/gennorm.csv', encoding='utf-8') as gn:
    for line in gn:
        fields = line.strip('\n\r').split('\t')
        doc_id = fields[1]
        text = fields[2]
        category = fields[3]
        norm_id = fields[4]
        start = int(fields[5])
        end = int(fields[6])

        if '' in [doc_id, text, norm_id, start, end, category]:
            continue

        if category != 'Gene':
            continue

        if doc_id in gene_norms:
            gene_norms[doc_id].append((start, end, text, norm_id))
        else:
            gene_norms[doc_id] = [(start, end, text, norm_id)]

print('load', len(gene_norms), 'documents')
print('fixing downloaded gennorm GN results')

with open('data/Gennorm/jsonlines_2.json', 'r') as handle, \
        open('data/Gennorm/jsonlines_fixed.json', 'w') as handle_fixed:
    for line in handle:
        line = line.strip()
        annotation = Annotation.loads(line, 'json')

        # fix entity property split problem
        '''
        for entity in annotation.entities:
            norm_ids = entity.property.get('norm_id')
            if norm_ids is not None:
                original_text = ','.join(norm_ids)
                entity.property['norm_id'] = original_text.split('/')
        '''

        genes = [e for e in annotation.entities if e.category == 'Gene']
        existed_genes = set()
        if len(genes) > 0:
            for gene in genes:
                existed_genes.add((gene.start, gene.end))
            # continue if there are already genes
            #handle_fixed.write(line + '\n')
            #continue
            
        doc_id = annotation.doc_id
        candidates = gene_norms.get(doc_id)
        if candidates is None:
            handle_fixed.write(annotation.dumps() + '\n')
            continue
            
        for c in candidates:
            start, end, text, norm_id = c

            if annotation.text[start:end].lower() != text.lower():
                for i in range(1, 5):
                    if annotation.text[start - i:end].lower() == text.lower():
                        start -= i
                        break
                    elif annotation.text[start:end - i].lower() == text.lower():
                        end -= i
                        break
                    elif annotation.text[start - i:end - i].lower() == text.lower():
                        start -= i
                        end -= i
                        break
                    elif annotation.text[start + i:end + i].lower() == text.lower():
                        start += i
                        end += i
                        break

                if start < 0:
                    start = 0
                elif start >= len(annotation.text):
                    # print(doc_id, "start > len(text)", line)
                    continue
                if end < 0:
                    # print(doc_id, "end < 0", line)
                    continue
                elif end > len(annotation.text):
                    end = len(annotation.text)
            
            if annotation.text[start:end].lower() != text.lower():
                print(doc_id, "can not match entity text with abstract text", 
                      start, end, text,
                      annotation.text[start:end], file=sys.stderr)
                continue

            # the gene is already normalized
            if (start, end) in existed_genes:
                continue
                
            # in case gennorm changes cases
            text = annotation.text[start:end]
            
            entity = annotation.has_entity_annotation('Gene', start, end, text)
            if entity is not None:
                db_norm_id = entity.property.get('norm_id')
                if isinstance(db_norm_id, list):
                    db_norm_id.append(norm_id)
                elif isinstance(db_norm_id, str):
                    entity.property['norm_id'] = [db_norm_id, norm_id]
                else:
                    entity.property['norm_id'] = [norm_id]
            else:
                entity = annotation.add_entity('Gene', start, end, text)
                entity.property['norm_id'] = [norm_id]
                added_genes += 1
                
            fixed_docs.add(doc_id)
        handle_fixed.write(annotation.dumps()+'\n')
            
print('fixed', len(fixed_docs), 'documents')
print('added', added_genes, 'genes')
