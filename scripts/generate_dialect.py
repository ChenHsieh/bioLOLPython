#!/usr/bin/env python3
"""
Generate a new bioLOLPython dialect using Claude API.

Usage:
    python scripts/generate_dialect.py "cottagecore" "~2020-2022" \
        "gentle pastoral internet aesthetic meets DNA analysis"

    # Or let the LLM decide based on a theme:
    python scripts/generate_dialect.py --auto "what's trending right now"

Requires: ANTHROPIC_API_KEY environment variable.
Outputs: a valid dialect YAML file to stdout (or --output path).
"""
import argparse
import sys
import os
import json

try:
    import anthropic
except ImportError:
    print("Error: anthropic package required. Install with: pip install anthropic")
    sys.exit(1)

import yaml
from bioLOLPython.dialects.base import REQUIRED_COMMANDS, validate_dialect

GENERATION_PROMPT = """\
You are helping create a dialect file for bioLOLPython, a bioinformatics scripting \
language where internet slang is used as command syntax for DNA analysis.

Each dialect maps slang from a specific internet culture/era to these biological \
operations. Here are the commands you must define, with examples from the "lolcat" \
dialect (~2005-2012 era):

- init: Program start greeting. Example: "HAI GENZOME"
- end: Program end. Example: "KTHXBYE"
- declare: Declare a DNA sequence variable. Must include {{name}} and {{seq}} placeholders. Example: 'DNA GO {{name}} ITZ {{seq}}'
- reverse: Reverse complement a sequence. Must include {{name}}. Example: "REVERSE THAT {{name}}"
- gc_content: Calculate GC content. Must include {{name}}. Example: "GC BOMB {{name}}"
- print: Print/output command (just the keyword, message follows). Example: "VISIBLE"
- transcribe: DNA to RNA. Must include {{name}}. Example: "TRANSCRIBE {{name}}"
- translate: DNA to protein. Must include {{name}}. Example: "TRANSLATE {{name}}"
- align: Pairwise alignment. Must include {{a}} and {{b}}. Example: "ALIGN {{a}} WIT {{b}}"
- mutate: Random mutation. Must include {{name}}. Example: "I CRAVE VIOLENCE {{name}}"
- length: Sequence length. Must include {{name}}. Example: "HOW LONG {{name}}"
- complement: Complement without reversing. Must include {{name}}. Example: "COMPLEMENT {{name}}"
- find_orf: Find open reading frame. Must include {{name}}. Example: "FIND ORF {{name}}"
- motif: Search for pattern. Must include {{name}} and {{pattern}}. Example: 'MOTIF HUNT {{name}} FOR {{pattern}}'

IMPORTANT RULES:
- Each command pattern must be ALL CAPS
- Patterns must contain the exact placeholders shown ({{name}}, {{seq}}, {{pattern}}, {{a}}, {{b}})
- {{seq}} and {{pattern}} will be quoted strings in actual use (e.g., "ATGC")
- The "print" command pattern is just a keyword — the user's message follows it
- Include fun emoji-rich response templates where applicable
- Include 3 example scripts showing the dialect in action
- Make the slang feel authentic to the era, not forced

Generate a dialect for:
- Name: {name}
- Era: {era}
- Theme/description: {description}

Output ONLY valid YAML (no markdown fences, no commentary). Follow this exact structure:

name: {name}
era: "{era}"
description: "one-line description"

commands:
  init:
    pattern: "..."
    greeting: "..."
  end:
    pattern: "..."
  declare:
    pattern: '... {{name}} ... {{seq}}'
  reverse:
    pattern: "... {{name}}"
  gc_content:
    pattern: "... {{name}}"
    response: "... {{value:.2f}}% ..."
  print:
    pattern: "KEYWORD"
  transcribe:
    pattern: "... {{name}}"
  translate:
    pattern: "... {{name}}"
  align:
    pattern: "... {{a}} ... {{b}}"
    response: "... {{score:.2f}} ... {{rating}}"
  mutate:
    pattern: "... {{name}}"
    response: "... {{name}} ... {{pos}} ... {{old}} ... {{new}}"
  length:
    pattern: "... {{name}}"
    response: "... {{name}} ... {{value}} ..."
  complement:
    pattern: "... {{name}}"
  find_orf:
    pattern: "... {{name}}"
    orf_found: "... {{orf}} ... {{length}} ..."
    orf_missing: "... {{name}} ..."
  motif:
    pattern: '... {{name}} ... {{pattern}}'
    found: "... '{{pattern}}' ... {{name}} ... {{count}} ..."
    position: "   pos {{start}}-{{end}}"
    not_found: "... '{{pattern}}' ... {{name}} ..."

examples:
  GC Content: |
    [init command]
    [declare X with "ATGCATGC"]
    [gc_content X]
    [end command]
  Protein Translation: |
    [init command]
    [declare Y with "ATGGAGGAGCC"]
    [translate Y]
    [print "Protein: " + Y]
    [end command]
  Alignment: |
    [init command]
    [declare A with "ATGCGTAGG"]
    [declare B with "ATGCGTACG"]
    [align A and B]
    [end command]
"""

AUTO_PROMPT = """\
You are a cultural analyst helping create a bioLOLPython dialect. The user wants a \
dialect based on: "{theme}"

First, identify a specific internet slang era or subculture that fits this theme. \
Then generate the dialect name (lowercase, no spaces), era range, and description.

Respond with ONLY a JSON object (no markdown):
{{"name": "...", "era": "~YYYY-YYYY", "description": "one line"}}
"""


def generate_dialect(name, era, description, model="claude-sonnet-4-20250514"):
    """Call Claude API to generate a dialect YAML."""
    client = anthropic.Anthropic()

    prompt = GENERATION_PROMPT.format(name=name, era=era, description=description)

    message = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def auto_detect_theme(theme, model="claude-sonnet-4-20250514"):
    """Use Claude to identify a dialect name/era from a theme description."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[{"role": "user", "content": AUTO_PROMPT.format(theme=theme)}],
    )

    return json.loads(message.content[0].text)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a bioLOLPython dialect using Claude API"
    )
    parser.add_argument(
        "name", nargs="?", help="Dialect name (e.g., 'cottagecore')"
    )
    parser.add_argument(
        "era", nargs="?", help="Era range (e.g., '~2020-2022')"
    )
    parser.add_argument(
        "description", nargs="?", help="Theme description"
    )
    parser.add_argument(
        "--auto", metavar="THEME",
        help="Auto-detect name/era from a theme (e.g., 'what Gen Alpha says in 2026')"
    )
    parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--model", default="claude-sonnet-4-20250514",
        help="Claude model to use"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate the generated YAML before outputting"
    )

    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable required.", file=sys.stderr)
        sys.exit(1)

    # Auto mode: detect name/era from theme
    if args.auto:
        print(f"🤖 Detecting dialect from theme: '{args.auto}'...", file=sys.stderr)
        info = auto_detect_theme(args.auto, model=args.model)
        name = info["name"]
        era = info["era"]
        description = info["description"]
        print(f"   → {name} ({era}): {description}", file=sys.stderr)
    elif args.name and args.era and args.description:
        name = args.name
        era = args.era
        description = args.description
    else:
        parser.error("Provide name/era/description or use --auto THEME")

    print(f"🧬 Generating '{name}' dialect...", file=sys.stderr)
    yaml_content = generate_dialect(name, era, description, model=args.model)

    # Validate if requested
    if args.validate:
        try:
            dialect_def = yaml.safe_load(yaml_content)
            validate_dialect(dialect_def)
            print(f"✅ Dialect '{name}' is valid.", file=sys.stderr)
        except Exception as e:
            print(f"❌ Validation failed: {e}", file=sys.stderr)
            sys.exit(1)

    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(yaml_content)
        print(f"💾 Saved to {args.output}", file=sys.stderr)
    else:
        print(yaml_content)


if __name__ == "__main__":
    main()
