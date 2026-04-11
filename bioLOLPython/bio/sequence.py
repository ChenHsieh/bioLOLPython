from Bio.Seq import Seq

class BioSeq:
    def __init__(self, sequence):
        self.seq = Seq(sequence)

    def reverse_complement(self):
        return str(self.seq.reverse_complement())

    def gc_content(self):
        length = len(self.seq)
        if length == 0:
            gc = 0.0
        else:
            g = self.seq.count('G')
            c = self.seq.count('C')
            gc = (g + c) / length * 100
        return f"💥 GC content: {gc:.2f}% 🧬"

    def __str__(self):
        return str(self.seq)
