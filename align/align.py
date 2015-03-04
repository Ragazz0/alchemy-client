# -*- coding: utf-8 -*-

from submodules.alignment.alignment import SegmentAlignment


class AnnotationAligner(object):
    aligner = SegmentAlignment()

    @classmethod
    def align(cls, annotation, altered_text, original_text):

        aligned_gold, aligned_altered = cls.aligner.align(original_text, altered_text,
                                                          segment_half=True, base_alignment='Hirschberg')
        alter2gold = cls.aligner.map_alignment(''.join(aligned_gold), ''.join(aligned_altered))

        for entity in annotation.entities:
            start = int(entity.start)
            end = int(entity.end)

            entity.start = alter2gold[start]
            if alter2gold[end] - alter2gold[end - 1] > 1:
                entity.end = alter2gold[end - 1] + 1
            else:
                entity.end = alter2gold[end]
            entity.text = original_text[entity.start:entity.end]
        
        return annotation

# for root, _, files in os.walk('input'):
#     for f in files:
#         if not f.endswith('.txt'):
#             continue
#         pmid = f[:-4]
#         print(pmid)
#         alter = os.path.join(root, pmid + '.txt')
#         alterFile = codecs.open(alter, 'r', 'utf-8')
#         alterText = alterFile.read().strip()
#         alterFile.close()
#
#         reader = AnnReader(root, pmid + '.ann')
#         annotation = reader.parse()
#
#         if len(annotation['T']) == 0:
#             writer.write('output', pmid + '.ann', annotation)
#             continue
#
#         gold = os.path.join('output', pmid + '.txt')
#         goldFile = codecs.open(gold, 'r', 'utf-8')
#         goldText = goldFile.read().strip()
#         goldFile.close()
#
#         entities = annotation['T']
#
#         goldPhrases = get_phrase(goldText)
#         alterPhrases = get_phrase(alterText)
#         h = Hirschberg(goldPhrases, alterPhrases)
#         # h = Hirschberg(list(goldText),list(alterText))
#         alignGold, alignAlter = h.align()
#         #print ''.join(alignGold)
#         #print ''.join(alignAlter)
#         alter2gold = h.map_alignment(''.join(alignGold), ''.join(alignAlter))
#
#         for k, e in entities.iteritems():
#             start = int(e.start)
#             end = int(e.end)
#
#             e.start = alter2gold[start]
#             if alter2gold[end] - alter2gold[end - 1] > 1:
#                 e.end = alter2gold[end - 1] + 1
#             else:
#                 e.end = alter2gold[end]
#             e.text = goldText[e.start:e.end]
#
#         writer.write('output', pmid + '.ann', annotation)

        # writer = AnnWriter()
        #
        # def get_phrase(text):
        #     p = re.compile(r'[a-zA-Z]+|[0-9]+|\s+|[.,;!\(\)]+')
        #     lista = []
        #     pre = 0
        #     for m in p.finditer(text):
        #         start = m.start()
        #         end = m.end()
        #         if pre < start:
        #             lista.append(text[pre:start])
        #         lista.append(text[start:end])
        #         pre = end
        #     return lista