import pytest
from bioLOLPython.bio.sequence import BioSeq


class TestGCContent:
    def test_empty_sequence(self):
        seq = BioSeq("")
        assert seq.gc_content() == 0.0

    def test_all_gc(self):
        seq = BioSeq("GGCC")
        assert seq.gc_content() == pytest.approx(100.0)

    def test_no_gc(self):
        seq = BioSeq("AATT")
        assert seq.gc_content() == pytest.approx(0.0)

    def test_mixed(self):
        seq = BioSeq("ATGC")
        assert seq.gc_content() == pytest.approx(50.0)

    def test_single_g(self):
        seq = BioSeq("G")
        assert seq.gc_content() == pytest.approx(100.0)

    def test_lowercase(self):
        seq = BioSeq("atgc")
        assert seq.gc_content() == pytest.approx(50.0)


class TestReverseComplement:
    def test_basic(self):
        seq = BioSeq("ATGC")
        assert seq.reverse_complement() == "GCAT"

    def test_palindrome(self):
        seq = BioSeq("AATT")
        assert seq.reverse_complement() == "AATT"

    def test_single_base(self):
        seq = BioSeq("A")
        assert seq.reverse_complement() == "T"


class TestComplement:
    def test_basic(self):
        seq = BioSeq("ATGC")
        assert seq.complement() == "TACG"


class TestLength:
    def test_basic(self):
        assert BioSeq("ATGC").length() == 4

    def test_empty(self):
        assert BioSeq("").length() == 0


class TestFindORF:
    def test_with_stop(self):
        seq = BioSeq("AAATGCCCCCCTAAGG")
        orf = seq.find_orf()
        assert orf is not None
        assert orf.startswith("ATG")
        assert orf.endswith("TAA")

    def test_no_start(self):
        seq = BioSeq("CCCCCC")
        assert seq.find_orf() is None

    def test_no_stop(self):
        seq = BioSeq("ATGCCC")
        orf = seq.find_orf()
        assert orf == "ATGCCC"


class TestFindMotif:
    def test_single_match(self):
        seq = BioSeq("ATGCATGC")
        matches = seq.find_motif("ATG")
        assert len(matches) == 2

    def test_no_match(self):
        seq = BioSeq("AAAA")
        assert seq.find_motif("GGG") == []


class TestValidation:
    def test_valid_dna(self):
        BioSeq("ATGC")  # should not raise

    def test_valid_iupac(self):
        BioSeq("ATGCNRYSWKMBDHV")  # should not raise

    def test_invalid_chars(self):
        with pytest.raises(ValueError, match="Invalid characters"):
            BioSeq("ATGXYZ")

    def test_skip_validation(self):
        BioSeq("MEE", validate=False)  # protein, should not raise

    def test_empty_valid(self):
        BioSeq("")  # should not raise


class TestStr:
    def test_str(self):
        seq = BioSeq("ATGC")
        assert str(seq) == "ATGC"

    def test_empty(self):
        seq = BioSeq("")
        assert str(seq) == ""
