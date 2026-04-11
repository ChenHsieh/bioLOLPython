"""
Base dialect infrastructure.

Each dialect defines patterns for bio commands using a template syntax:
  - {name}, {a}, {b}  -> capture a variable name (word characters)
  - {seq}             -> capture a quoted sequence string
  - {pattern}         -> capture a quoted pattern string
  - Remaining text    -> matched literally (case-sensitive)

Patterns are compiled into regexes at registration time.
Dialects can be defined as YAML files or Python dicts.
"""
import re
import os
import yaml
from pathlib import Path

# Template placeholders -> regex groups
_PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")

_PLACEHOLDER_PATTERNS = {
    "seq": r'"(?P<seq>[^"]*)"',
    "pattern": r'"(?P<pattern>[^"]*)"',
}

# Required commands every dialect must define
REQUIRED_COMMANDS = [
    "init", "end", "declare", "reverse", "gc_content",
    "print", "transcribe", "translate", "align", "mutate",
    "length", "complement", "find_orf", "motif",
]

# Bundled YAML definitions directory
BUNDLED_DIR = Path(__file__).parent / "definitions"

# User dialect directory
USER_DIR = Path.home() / ".bioLOL" / "dialects"


def _compile_pattern(template):
    """Compile a dialect pattern template into a regex."""
    parts = _PLACEHOLDER_RE.split(template)
    regex_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Literal text — escape and normalize spaces to \s+
            escaped = re.escape(part.strip())
            escaped = escaped.replace(r"\ ", r"\s+")
            regex_parts.append(escaped)
        else:
            # Placeholder name
            if part in _PLACEHOLDER_PATTERNS:
                regex_parts.append(_PLACEHOLDER_PATTERNS[part])
            else:
                regex_parts.append(rf"(?P<{part}>\w+)")
    return re.compile(r"^\s*" + r"\s+".join(p for p in regex_parts if p) + r"(?:\s+.*)?$")


def compile_dialect(dialect_def):
    """Compile all patterns in a dialect definition, adding 'matcher' to each command."""
    for cmd_name, cmd_def in dialect_def["commands"].items():
        cmd_def["matcher"] = _compile_pattern(cmd_def["pattern"])
    return dialect_def


def validate_dialect(dialect_def):
    """Validate a dialect definition has all required fields."""
    for field in ("name", "era", "description", "commands"):
        if field not in dialect_def:
            raise ValueError(f"Dialect missing required field: '{field}'")
    for cmd in REQUIRED_COMMANDS:
        if cmd not in dialect_def["commands"]:
            raise ValueError(
                f"Dialect '{dialect_def['name']}' missing command: '{cmd}'"
            )
        if "pattern" not in dialect_def["commands"][cmd]:
            raise ValueError(
                f"Dialect '{dialect_def['name']}' command '{cmd}' missing 'pattern'"
            )
    return True


def load_yaml_dialect(path):
    """Load and compile a dialect from a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        dialect_def = yaml.safe_load(f)
    validate_dialect(dialect_def)
    return compile_dialect(dialect_def)


def discover_yaml_dialects(*dirs):
    """Discover all .yaml dialect files in the given directories.
    Later directories override earlier ones (user overrides bundled)."""
    dialects = {}
    for d in dirs:
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.yaml")):
            try:
                dialect = load_yaml_dialect(path)
                dialects[dialect["name"]] = dialect
            except Exception as e:
                # Skip invalid files silently in discovery
                print(f"⚠️ Skipping {path.name}: {e}")
    return dialects
