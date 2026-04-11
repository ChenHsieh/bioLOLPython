DIALECT = {
    "name": "brainrot",
    "era": "~2023-2026",
    "description": "skibidi DNA sigma rizz. Gen Alpha brainrot meets bioinformatics.",
    "commands": {
        "init": {
            "pattern": "SKIBIDI GENOME",
            "greeting": "🚽 SKIBIDI BIOLAB ACTIVATED sigma grindset 🧬",
        },
        "end": {
            "pattern": "MOGGER OUT",
        },
        "declare": {
            "pattern": "SIGMA {name} RIZZ {seq}",
        },
        "reverse": {
            "pattern": "FANUM TAX {name}",
        },
        "gc_content": {
            "pattern": "AURA CHECK {name}",
            "response": "✨ GC aura: {value:.2f}% {rating} 🧬",
        },
        "print": {
            "pattern": "HAWK TUAH",
        },
        "transcribe": {
            "pattern": "EDGING {name}",
        },
        "translate": {
            "pattern": "LOOKSMAX {name}",
        },
        "align": {
            "pattern": "MEWING CONTEST {a} VS {b}",
            "response": "🗿 MEWING SCOREZ: {score:.2f} {rating}",
        },
        "mutate": {
            "pattern": "ONLY IN OHIO {name}",
            "response": "💀 ohio moment for {name} at pos {pos}: {old} ➜ {new}",
        },
        "length": {
            "pattern": "GYATT HOW LONG {name}",
            "response": "📏 {name} is {value} bases long gyatt",
        },
        "complement": {
            "pattern": "REVERSE UNO {name}",
        },
        "find_orf": {
            "pattern": "SIGMA GRIND {name}",
            "orf_found": "💪 sigma ORF found: {orf} ({length} bp) W",
            "orf_missing": "💀 {name} is not sigma (no ATG start codon) L",
        },
        "motif": {
            "pattern": "SUSSY SEARCH {name} FOR {pattern}",
            "found": "🔍 '{pattern}' is sus in {name} {count} time(s):",
            "position": "   pos {start}-{end}",
            "not_found": "🔍 '{pattern}' is not sus in {name}",
        },
    },
    "examples": {
        "GC Content": 'SKIBIDI GENOME\nSIGMA X RIZZ "ATGCATGC"\nAURA CHECK X\nMOGGER OUT',
        "Protein Translation": 'SKIBIDI GENOME\nSIGMA Y RIZZ "ATGGAGGAGCC"\nLOOKSMAX Y\nHAWK TUAH "Protein: " + Y\nMOGGER OUT',
        "Alignment": 'SKIBIDI GENOME\nSIGMA A RIZZ "ATGCGTAGG"\nSIGMA B RIZZ "ATGCGTACG"\nMEWING CONTEST A VS B\nMOGGER OUT',
    },
}
