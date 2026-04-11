"""
Dialect registry for bioLOLPython.

Each dialect maps internet slang from a specific era to bioinformatics commands.
Dialects are loaded from YAML files in this order (later overrides earlier):
  1. Bundled definitions (bioLOLPython/dialects/definitions/*.yaml)
  2. User definitions (~/.bioLOL/dialects/*.yaml)
"""
from bioLOLPython.dialects.base import (
    BUNDLED_DIR,
    USER_DIR,
    compile_dialect,
    discover_yaml_dialects,
    load_yaml_dialect,
    validate_dialect,
)

_DIALECTS = {}


def _load_all():
    """Load dialects from YAML files (bundled + user)."""
    global _DIALECTS
    _DIALECTS = discover_yaml_dialects(BUNDLED_DIR, USER_DIR)

    # Fallback: if no YAML files found, load from Python modules
    if not _DIALECTS:
        from bioLOLPython.dialects.lolcat import DIALECT as _lolcat
        from bioLOLPython.dialects.gen_z import DIALECT as _gen_z
        from bioLOLPython.dialects.brainrot import DIALECT as _brainrot
        for d in (_lolcat, _gen_z, _brainrot):
            compiled = compile_dialect(d)
            _DIALECTS[compiled["name"]] = compiled


_load_all()


def reload_dialects():
    """Reload all dialects from disk. Useful after fetching remote dialects."""
    _load_all()


def register_dialect(dialect_def):
    """Register a dialect from a Python dict (for programmatic use)."""
    validate_dialect(dialect_def)
    compiled = compile_dialect(dialect_def)
    _DIALECTS[compiled["name"]] = compiled
    return compiled


def get_dialect(name):
    if name not in _DIALECTS:
        available = ", ".join(sorted(_DIALECTS.keys()))
        raise ValueError(f"Unknown dialect '{name}'. Available: {available}")
    return _DIALECTS[name]


def list_dialects():
    return [
        {"name": d["name"], "era": d["era"], "description": d["description"]}
        for d in _DIALECTS.values()
    ]


def dialect_names():
    return sorted(_DIALECTS.keys())
