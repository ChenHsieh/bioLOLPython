# bioLOLPython

[![PyPI version](https://img.shields.io/pypi/v/bioLOLPython)](https://pypi.org/project/bioLOLPython/)
[![Python](https://img.shields.io/pypi/pyversions/bioLOLPython)](https://pypi.org/project/bioLOLPython/)
[![Tests](https://github.com/ChenHsieh/bioLOLPython/actions/workflows/publish.yml/badge.svg)](https://github.com/ChenHsieh/bioLOLPython/actions/workflows/publish.yml)
[![License: MIT](https://img.shields.io/github/license/ChenHsieh/bioLOLPython)](LICENSE)
[![Streamlit](https://img.shields.io/badge/demo-Streamlit-FF4B4B?logo=streamlit)](https://bioLOL.streamlit.app)

*A LOLCODE-inspired scripting language for biological sequence analysis — now with multiple internet slang dialects.*

![demo](demo.gif)

## Table of Contents

- [Background](#background)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Dialects](#dialects)
  - [Side-by-side comparison](#side-by-side-comparison)
- [Commands](#commands)
- [Usage](#usage)
  - [Run a script](#run-a-script)
  - [Interactive REPL](#interactive-repl)
  - [Web interface](#web-interface)
  - [Fetch community dialects](#fetch-community-dialects)
- [Creating a New Dialect](#creating-a-new-dialect)
  - [YAML format](#yaml-format)
  - [Pattern placeholders](#pattern-placeholders)
  - [Generate with AI](#generate-with-ai)
  - [Auto-generation via GitHub Actions](#auto-generation-via-github-actions)
- [Examples](#examples)
- [Running Tests](#running-tests)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)

## Background

[LOLCODE](https://en.wikipedia.org/wiki/LOLCODE) is an esoteric programming language created in 2007 by Adam Lindsay, based on **lolspeak** — the broken-English caption style from the [lolcat](https://en.wikipedia.org/wiki/Lolcat) meme era.

[LOLPython](https://github.com/KartikTalwar/LOLPython), by Andrew Dalke, adapted the concept into a transpiler that converts lolspeak-style syntax into executable Python.

**bioLOLPython** extends LOLPython with bioinformatics commands and a **dialect system** that maps internet slang from different eras to the same DNA analysis operations. It's part scripting tool, part time capsule of internet culture.

## Installation

From PyPI:

```
pip install bioLOLPython
```

Or install with [pipx](https://pypa.github.io/pipx/) for an isolated CLI tool:

```
pipx install bioLOLPython
```

For development:

```
git clone https://github.com/ChenHsieh/bioLOLPython.git
cd bioLOLPython
pip install -e .
```

## Quick Start

```
HAI GENZOME 1.0
DNA GO X ITZ "ATGCGTAC"
GC BOMB X
TRANSLATE X
VISIBLE "protein: " + X
KTHXBYE
```

Save as `hello.lolz` and run:

```
bioLOL hello.lolz
```

Or use brainrot dialect:

```
SKIBIDI GENOME
SIGMA X RIZZ "ATGCGTAC"
AURA CHECK X
LOOKSMAX X
HAWK TUAH "protein: " + X
MOGGER OUT
```

```
bioLOL --dialect brainrot hello_brainrot.lolz
```

## Dialects

Each dialect represents a different era of internet slang. The biology stays the same — only the syntax changes.

| Dialect | Era | Vibe |
|---|---|---|
| `lolcat` | ~2005-2012 | I CAN HAS BIOINFORMATICS? |
| `gen_z` | ~2018-2023 | no cap this DNA is bussin fr fr |
| `brainrot` | ~2023-2026 | skibidi DNA sigma rizz |

New dialects are [generated quarterly](#auto-generation-via-github-actions) by AI based on current internet trends.

### Side-by-side comparison

| Operation | lolcat | gen_z | brainrot |
|---|---|---|---|
| Start | `HAI GENZOME` | `YO ITS GIVING GENOME` | `SKIBIDI GENOME` |
| Declare DNA | `DNA GO X ITZ "ATGC"` | `NO CAP X IS "ATGC"` | `SIGMA X RIZZ "ATGC"` |
| GC content | `GC BOMB X` | `VIBE CHECK X` | `AURA CHECK X` |
| Reverse complement | `REVERSE THAT X` | `UNO REVERSE X` | `FANUM TAX X` |
| Transcribe | `TRANSCRIBE X` | `MAIN CHARACTER X` | `EDGING X` |
| Translate | `TRANSLATE X` | `GLOW UP X` | `LOOKSMAX X` |
| Complement | `COMPLEMENT X` | `MIRROR CHECK X` | `REVERSE UNO X` |
| Length | `HOW LONG X` | `BESTIE HOW LONG X` | `GYATT HOW LONG X` |
| Find ORF | `FIND ORF X` | `UNDERSTOOD THE ASSIGNMENT X` | `SIGMA GRIND X` |
| Motif search | `MOTIF HUNT X FOR "CCC"` | `LIVING RENT FREE X FOR "CCC"` | `SUSSY SEARCH X FOR "CCC"` |
| Mutate | `I CRAVE VIOLENCE X` | `CAUGHT IN 4K X` | `ONLY IN OHIO X` |
| Align | `ALIGN A WIT B` | `RIZZ CHECK A AND B` | `MEWING CONTEST A VS B` |
| Print | `VISIBLE "..." + X` | `SPILL "..." + X` | `HAWK TUAH "..." + X` |
| End | `KTHXBYE` | `PERIODT` | `MOGGER OUT` |

## Commands

bioLOLPython supports 14 biological operations, each mapped to dialect-specific syntax:

| Command | Description | Output |
|---|---|---|
| **Declare** | Define a named DNA sequence | — |
| **GC content** | Calculate GC percentage | `GC content: 50.00%` |
| **Reverse complement** | Reverse complement a sequence | Modifies variable in place |
| **Transcribe** | DNA → RNA (T→U) | Modifies variable in place |
| **Translate** | DNA → protein (codon table) | Modifies variable in place |
| **Complement** | Complement without reversing | Modifies variable in place |
| **Length** | Sequence length in bases | `X is 8 bases long` |
| **Find ORF** | Find first open reading frame (ATG…stop) | ORF sequence and length |
| **Motif search** | Find all occurrences of a pattern | Positions of each match |
| **Mutate** | Random single-base substitution | Reports position and change |
| **Align** | Global pairwise alignment (Biopython) | Similarity score and rating |
| **Print** | Print strings and/or variables | Supports `+` concatenation |
| **Start / End** | Program delimiters | Greeting message on start |

DNA sequences are validated against [IUPAC nucleotide codes](https://www.bioinformatics.org/sms/iupac.html) (ACGTUNRYSWKMBDHV) on declaration.

## Usage

### Run a script

```
bioLOL script.lolz                       # default (lolcat)
bioLOL --dialect gen_z script.lolz       # Gen Z mode
bioLOL --dialect brainrot script.lolz    # brainrot mode
```

### Interactive REPL

```
bioLOL                                   # lolcat REPL
bioLOL --dialect brainrot                # brainrot REPL
```

### Web interface

Try it at [bioLOL.streamlit.app](https://bioLOL.streamlit.app) — includes a dialect selector and example scripts for each era.

To run locally:

```
pip install streamlit
streamlit run streamlit_app.py
```

### Fetch community dialects

```
bioLOL --list-dialects                   # show available dialects
bioLOL --update                          # fetch latest from registry (24h cache)
bioLOL --update --force                  # bypass cache
```

User dialects are stored in `~/.bioLOL/dialects/`.

## Creating a New Dialect

Dialects are YAML files. Drop one into `~/.bioLOL/dialects/` for personal use, or add it to `bioLOLPython/dialects/definitions/` and open a PR.

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

All 14 commands are required. The dialect is validated on load.

### Pattern placeholders

| Placeholder | Captures |
|---|---|
| `{name}` | A variable name (word characters) |
| `{a}`, `{b}` | Variable names for two-sequence commands |
| `{seq}` | A quoted DNA sequence (e.g., `"ATGC"`) |
| `{pattern}` | A quoted search pattern |

### Generate with AI

Use the generator script to create a dialect with the Claude API:

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

A [GitHub Action](.github/workflows/generate-dialect.yml) runs quarterly to generate a new dialect based on current internet trends. It:

1. Calls the Claude API to generate a dialect YAML
2. Validates the output against the required schema
3. Runs the full test suite
4. Opens a PR for human review

To trigger manually: Actions > "Generate New Dialect" > Run workflow. You can optionally provide a custom theme.

Requires the `ANTHROPIC_API_KEY` repository secret (Settings > Secrets > Actions).

## Examples

Example scripts are in the [`examples/`](examples/) directory:

| File | Dialect | What it does |
|---|---|---|
| `test_bio.lolz` | lolcat | GC content, transcription, translation |
| `test_alignment.lolz` | lolcat | Pairwise sequence alignment |
| `test_violence.lolz` | lolcat | Random mutation |
| `test_transcribe.lolz` | lolcat | DNA → RNA |
| `test_translate.lolz` | lolcat | DNA → protein |
| `gen_z_demo.lolz` | gen_z | Full sequence analysis workflow |
| `brainrot_demo.lolz` | brainrot | Full sequence analysis workflow |

Run any example:

```
bioLOL examples/test_bio.lolz
bioLOL --dialect gen_z examples/gen_z_demo.lolz
bioLOL --dialect brainrot examples/brainrot_demo.lolz
```

## Running Tests

```
pip install pytest
pytest
```

96 tests covering the BioSeq class, interpreter commands across all dialects, and dialect loading/validation.

Requires Python >= 3.8. Dependencies: `biopython`, `ply`, `pyyaml`.

## License

[MIT](LICENSE)

## Contributing

Contributions welcome — especially new dialects. The easiest way to contribute:

1. Write a YAML dialect file following the [format above](#yaml-format)
2. Add your dialect name to `bioLOLPython/dialects/definitions/index.txt`
3. Add example scripts to `examples/`
4. Run `pytest` to verify
5. Open a PR

Or use the [AI generator](#generate-with-ai) as a starting point and customize from there.

## Acknowledgments

- LOLPython by Andrew Dalke (public domain)
- Bioinformatics extensions and dialect system by Chen Hsieh
- Development assisted by AI tools (ChatGPT, Claude)
