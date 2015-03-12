# -*- coding: utf-8 -*-
import traceback
from submodules.alignment.alignment import SegmentAlignment


class AnnotationAligner(object):
    aligner = SegmentAlignment()

    @classmethod
    def align(cls, annotation, original_text):
        """ align annotation with original text
        :param annotation: a {doc_id, text, entity_set, relation_set, property} object
        :type annotation: dict
        :param original_text: the original text
        :type original_text: str
        :return: None
        :rtype: None
        """
        altered_text = annotation.get('text')
        
        # base_alginment = Hirschberg, segment_half = True, segment = 50, diff = 50
        aligned_gold, aligned_altered = cls.aligner.align(original_text, altered_text,
                                                          segment_half=True, base_alignment='Hirschberg')

        alter2gold = cls.aligner.map_alignment(''.join(aligned_gold), ''.join(aligned_altered))
        
        for entity in annotation.get('entity_set'):
            start = int(entity.get('start'))
            end = int(entity.get('end'))

            entity['start'] = alter2gold[start]
            try:
                if end >= len(alter2gold):
                    # end is an index in a range, so it could
                    # equal to the length of length of the altered string
                    entity['end'] = alter2gold[-1]
                elif end > 0 and alter2gold[end] - alter2gold[end - 1] > 1:
                    entity['end'] = alter2gold[end - 1] + 1
                else:
                    entity['end'] = alter2gold[end]
            except IndexError:
                traceback.print_exc()
                print(annotation.get('doc_id'), len(alter2gold),start,end, sep="\t")
            entity['text'] = original_text[entity.get('start'):entity.get('end')]
        
        annotation['text'] = original_text