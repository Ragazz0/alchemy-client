# -*- coding: utf-8 -*-

from submodules.alignment.alignment import SegmentAlignment


class AnnotationAligner(object):
    aligner = SegmentAlignment()

    @classmethod
    def align(cls, annotation, altered_text, original_text):

        # base_alginment = Hirschberg, segment_half = True, segment = 50, diff = 50
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