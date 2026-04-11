# bioLOLPython

*A LOLCODE-inspired scripting language for biological sequence analysis — now with multiple internet slang dialects.*

![demo](demo.gif)

## Background

[LOLCODE](https://en.wikipedia.org/wiki/LOLCODE) is an esoteric programming language created in 2007 by Adam Lindsay, based on **lolspeak** — the broken-English caption style from the [lolcat](https://en.wikipedia.org/wiki/Lolcat) meme era.

[LOLPython](https://github.com/KartikTalwar/LOLPython), by Andrew Dalke, adapted the concept into a transpiler that converts lolspeak-style syntax into executable Python.

**bioLOLPython** extends LOLPython with bioinformatics commands and a **dialect system** that maps internet slang from different eras to the same DNA analysis operations. It's part scripting tool, part time capsule of internet culture.

Try the web interface at [bioLOL.streamlit.app](https://bioLOL.streamlit.app).

## Dialects

Each dialect represents a different era of internet slang. The biology stays the same — only the syntax changes.

| Dialect | Era | Vibe |
|---|---|---|
| `lolcat` | ~2005-2012 | I CAN HAS BIOINFORMATICS? |
| `gen_z` | ~2018-2023 | no cap this DNA is bussin fr fr |
| `brainrot` | ~2023-2026 | skibidi DNA sigma rizz |

### Side-by-side comparison

| Operation | lolcat | gen_z | brainrot |
|---|---|---|---|
| Start | `HAI GENZOME` | `YO ITS GIVING GENOME` | `SKIBIDI GENOME` |
| Declare DNA | `DNA GO X ITZ "ATGC"` | `NO CAP X IS "ATGC"` | `SIGMA X RIZZ "ATGC"` |
| GC content | `GC BOMB X` | `VIBE CHECK X` | `AURA CHECK X` |
| Reverse complement | `REVERSE THAT X` | `UNO REVERSE X` | `FANUM TAX X` |
| Transcribe | `TRANSCRIBE X` | `MAIN CHARACTER X` | `EDGING X` |
| Translate | `TRANSLATE X` | `GLOW UP X` | `LOOKSMAX X` |
| Mutate | `I CRAVE VIOLENCE X` | `CAUGHT IN 4K X` | `ONLY IN OHIO X` |
| Align | `ALIGN A WIT B` | `RIZZ CHECK A AND B` | `MEWING CONTEST A VS B` |
| Print | `VISIBLE "..." + X` | `SPILL "..." + X` | `HAWK TUAH "..." + X` |
| End | `KTHXBYE` | `PERIODT` | `MOGGER OUT` |

## Commands

| Command | Description |
|---|---|
| Declare | Define a DNA sequence |
| Reverse | Reverse complement |
| GC content | Calculate GC content |
| Transcribe | DNA to RNA |
| Translate | DNA to protein |
| Complement | Complement without reversing |
| Length | Sequence length |
| Find ORF | Find first open reading frame |
| Motif search | Find pattern occurrences |
| Mutate | Random point mutation |
| Align | Global pairwise alignment |
| Print | Print variables with string concatenation |

## Example (lolcat)

```
HAI GENZOME 1.0
DNA GO X ITZ "ATGCGTAC"
GC BOMB X
TRANSLATE X
VISIBLE "protein: " + X
KTHXBYE
```

## Example (brainrot)

```
SKIBIDI GENOME
SIGMA X RIZZ "ATGCGTAC"
AURA CHECK X
LOOKSMAX X
HAWK TUAH "protein: " + X
MOGGER OUT
```

## Installation

Install with [pipx](https://pypa.github.io/pipx/) (recommended):

```
pipx install git+https://github.com/ChenHsieh/bioLOLPython.git
```

Or install locally for development:

```
git clone https://github.com/ChenHsieh/bioLOLPython.git
cd bioLOLPython
pip install -e .
```

## Usage

Run a script:
```
bioLOL script.lolz                       # default (lolcat)
bioLOL --dialect gen_z script.lolz       # gen z mode
bioLOL --dialect brainrot script.lolz    # brainrot mode
```

Interactive REPL:
```
bioLOL                                   # lolcat REPL
bioLOL --dialect brainrot                # brainrot REPL
```

List available dialects:
```
bioLOL --list-dialects
```

Fetch latest dialects from the remote registry:
```
bioLOL --update                          # uses 24h cache
bioLOL --update --force                  # bypass cache
```

## Creating a New Dialect

Dialects are YAML files. Create one in `bioLOLPython/dialects/definitions/` or drop it into `~/.bioLOL/dialects/` for personal use.

### YAML format

```yaml
name: mydialect
era: "~2025-2026"
description: "One-line description of the vibe."

commands:
  init:
    pattern: "MY START COMMAND"
    greeting: "Welcome message with emoji"
  end:
    pattern: "MY END COMMAND"
  declare:
    pattern: 'MY DECLARE {name} WITH {seq}'
  reverse:
    pattern: "MY REVERSE {name}"
  gc_content:
    pattern: "MY GC {name}"
    response: "GC content: {value:.2f}%"
  print:
    pattern: "MY PRINT"
  transcribe:
    pattern: "MY TRANSCRIBE {name}"
  translate:
    pattern: "MY TRANSLATE {name}"
  align:
    pattern: "MY ALIGN {a} WITH {b}"
    response: "Score: {score:.2f} {rating}"
  mutate:
    pattern: "MY MUTATE {name}"
    response: "Mutated {name} at pos {pos}: {old} -> {new}"
  length:
    pattern: "MY LENGTH {name}"
    response: "{name} is {value} bases"
  complement:
    pattern: "MY COMPLEMENT {name}"
  find_orf:
    pattern: "MY ORF {name}"
    orf_found: "ORF: {orf} ({length} bp)"
    orf_missing: "No ORF in {name}"
  motif:
    pattern: 'MY MOTIF {name} FOR {pattern}'
    found: "Found {count} match(es) for '{pattern}' in {name}:"
    position: "   pos {start}-{end}"
    not_found: "No matches for '{pattern}' in {name}"

examples:
  GC Content: |
    MY START COMMAND
    MY DECLARE X WITH "ATGCATGC"
    MY GC X
    MY END COMMAND
```

### Pattern placeholders

| Placeholder | Captures |
|---|---|
| `{name}` | A variable name (word characters) |
| `{a}`, `{b}` | Variable names for two-sequence commands |
| `{seq}` | A quoted DNA sequence (e.g., `"ATGC"`) |
| `{pattern}` | A quoted search pattern |

All 14 commands are required. The dialect is validated on load.

### Generate with AI

Use the generator script to create a dialect with Claude:

```bash
# Specify name, era, and description
python scripts/generate_dialect.py "cottagecore" "~2020-2022" \
    "gentle pastoral internet aesthetic meets DNA" \
    --validate \
    -o bioLOLPython/dialects/definitions/cottagecore.yaml

# Or let Claude pick the name and era from a theme
python scripts/generate_dialect.py \
    --auto "what's trending on TikTok right now" \
    --validate \
    -o bioLOLPython/dialects/definitions/new.yaml
```

Requires `ANTHROPIC_API_KEY` environment variable and `pip install anthropic`.

### Auto-generation via GitHub Actions

A [GitHub Action](.github/workflows/generate-dialect.yml) runs monthly to generate a new dialect based on current internet trends. It:

1. Calls Claude API to generate a dialect YAML
2. Validates the output against the schema
3. Runs the test suite
4. Opens a PR for human review

To trigger manually: go to Actions > "Generate New Dialect" > Run workflow, and optionally provide a custom theme.

Requires the `ANTHROPIC_API_KEY` repository secret.

## Running Tests

```
pip install pytest
pytest
```

Requires Python >= 3.8. Dependencies: `biopython`, `ply`, `pyyaml`.

## License

MIT License.

## Contributing

Contributions welcome — especially new dialects. The easiest way to contribute is to write a YAML dialect file and open a PR. See the format above.

## Acknowledgments

- LOLPython by Andrew Dalke (public domain)
- Bioinformatics extensions and dialect system by Chen Hsieh (2025)
- Development assisted by AI tools (ChatGPT, Claude)
