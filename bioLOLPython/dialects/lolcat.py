DIALECT = {
    "name": "lolcat",
    "era": "~2005-2012",
    "description": "I CAN HAS BIOINFORMATICS? Classic lolspeak from the cheezburger era.",
    "commands": {
        "init": {
            "pattern": "HAI GENZOME",
            "greeting": "🐾 LOADING bioLOLCODE V1... LETZ GOOOO 💥",
        },
        "end": {
            "pattern": "KTHXBYE",
        },
        "declare": {
            "pattern": "DNA GO {name} ITZ {seq}",
        },
        "reverse": {
            "pattern": "REVERSE THAT {name}",
        },
        "gc_content": {
            "pattern": "GC BOMB {name}",
            "response": "💥 GC content: {value:.2f}% 🧬",
        },
        "print": {
            "pattern": "VISIBLE",
        },
        "transcribe": {
            "pattern": "TRANSCRIBE {name}",
        },
        "translate": {
            "pattern": "TRANSLATE {name}",
        },
        "align": {
            "pattern": "ALIGN {a} WIT {b}",
            "response": "🌈 ALINE SCOREZ: {score:.2f} 🔥 itz {rating}!!",
        },
        "mutate": {
            "pattern": "I CRAVE VIOLENCE {name}",
            "response": "💣 mutated {name} at pos {pos}: {old} ➜ {new}",
        },
        "length": {
            "pattern": "HOW LONG {name}",
            "response": "📏 {name} iz {value} bases long",
        },
        "complement": {
            "pattern": "COMPLEMENT {name}",
        },
        "find_orf": {
            "pattern": "FIND ORF {name}",
            "orf_found": "🔍 ORF found: {orf} ({length} bp)",
            "orf_missing": "🔍 No ORF found in {name} (no ATG start codon)",
        },
        "motif": {
            "pattern": "MOTIF HUNT {name} FOR {pattern}",
            "found": "🎯 Found {count} match(es) for '{pattern}' in {name}:",
            "position": "   pos {start}-{end}",
            "not_found": "🎯 No matches for '{pattern}' in {name}",
        },
    },
    "examples": {
        "GC Content": 'HAI GENZOME 1.0\nDNA GO X ITZ "ATGCATGC"\nGC BOMB X\nKTHXBYE',
        "Protein Translation": 'HAI GENZOME 1.0\nDNA GO Y ITZ "ATGGAGGAGCC"\nTRANSLATE Y\nVISIBLE "Protein: " + Y\nKTHXBYE',
        "Alignment": 'HAI GENZOME 1.0\nDNA GO A ITZ "ATGCGTAGG"\nDNA GO B ITZ "ATGCGTACG"\nALIGN A WIT B\nKTHXBYE',
    },
}
