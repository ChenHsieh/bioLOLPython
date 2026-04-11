import re
from Bio.Seq import Seq

IUPAC_DNA_RNA = set("ACGTUNRYSWKMBDHVacgtunryswkmbdhv")


class BioSeq:
    def __init__(self, sequence, validate=True):
        if validate and sequence:
            invalid = set(sequence) - IUPAC_DNA_RNA
            if invalid:
                raise ValueError(
                    f"Invalid characters in sequence: {''.join(sorted(invalid))}. "
                    f"Only IUPAC nucleotide codes are allowed (ACGTUNRYSWKMBDHV)."
                )
        self.seq = Seq(sequence)

    def reverse_complement(self):
        return str(self.seq.reverse_complement())

    def complement(self):
        return str(self.seq.complement())

    def gc_content(self):
        length = len(self.seq)
        if length == 0:
            gc = 0.0
        else:
            g = self.seq.upper().count('G')
            c = self.seq.upper().count('C')
            gc = (g + c) / length * 100
        return gc

    def length(self):
        return len(self.seq)

    def find_orf(self):
        """Find the first open reading frame (ATG to stop codon)."""
        seq_str = str(self.seq).upper()
        start = seq_str.find("ATG")
        if start == -1:
            return None
        stop_codons = ("TAA", "TAG", "TGA")
        for i in range(start, len(seq_str) - 2, 3):
            codon = seq_str[i:i+3]
            if codon in stop_codons and i > start:
                return seq_str[start:i+3]
        # No stop codon found — return from ATG to end
        return seq_str[start:]

    def find_motif(self, pattern):
        """Find all occurrences of a motif pattern in the sequence."""
        matches = []
        for m in re.finditer(pattern, str(self.seq), re.IGNORECASE):
            matches.append((m.start() + 1, m.end()))  # 1-indexed
        return matches

    def __str__(self):
        return str(self.seq)
