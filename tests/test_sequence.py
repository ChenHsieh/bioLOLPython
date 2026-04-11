import pytest
from bioLOLPython.bio.sequence import BioSeq

def test_gc_content_empty():
    seq = BioSeq("")
    assert seq.gc_content().startswith("💥 GC content: 0.00%")

