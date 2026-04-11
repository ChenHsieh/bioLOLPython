"""
Remote dialect fetching and caching.

Fetches dialect YAML files from a remote registry (GitHub raw URL by default),
caches them locally in ~/.bioLOL/dialects/, and reloads the dialect registry.
"""
import os
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

from bioLOLPython.dialects.base import USER_DIR

# Default registry: raw GitHub URL pointing to the definitions/ directory
DEFAULT_REGISTRY_URL = (
    "https://raw.githubusercontent.com/ChenHsieh/bioLOLPython/master/"
    "bioLOLPython/dialects/definitions"
)

# Default index file listing available dialect filenames
INDEX_FILENAME = "index.txt"

# Cache TTL: 24 hours
CACHE_TTL_SECONDS = 86400


def _ensure_user_dir():
    USER_DIR.mkdir(parents=True, exist_ok=True)


def _is_cache_fresh(path, ttl=CACHE_TTL_SECONDS):
    """Check if a cached file is fresh enough."""
    if not path.exists():
        return False
    age = time.time() - path.stat().st_mtime
    return age < ttl


def _fetch_url(url, timeout=10):
    """Fetch content from a URL."""
    req = Request(url, headers={"User-Agent": "bioLOLPython"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def fetch_dialect(name, registry_url=DEFAULT_REGISTRY_URL):
    """Fetch a single dialect YAML from the remote registry and cache it."""
    _ensure_user_dir()
    url = f"{registry_url}/{name}.yaml"
    content = _fetch_url(url)
    cache_path = USER_DIR / f"{name}.yaml"
    cache_path.write_text(content)
    return cache_path


def fetch_index(registry_url=DEFAULT_REGISTRY_URL):
    """Fetch the index of available remote dialects."""
    url = f"{registry_url}/{INDEX_FILENAME}"
    content = _fetch_url(url)
    return [line.strip() for line in content.splitlines() if line.strip()]


def update_dialects(registry_url=DEFAULT_REGISTRY_URL, force=False):
    """Fetch all remote dialects and update local cache.

    Returns a list of (name, status) tuples where status is
    'updated', 'cached', or 'error: ...'.
    """
    _ensure_user_dir()
    results = []

    # Try to fetch index; if unavailable, fetch known dialect names
    try:
        dialect_names = fetch_index(registry_url)
    except URLError:
        # Fallback: try common names
        dialect_names = ["lolcat", "gen_z", "brainrot"]

    for name in dialect_names:
        cache_path = USER_DIR / f"{name}.yaml"
        if not force and _is_cache_fresh(cache_path):
            results.append((name, "cached"))
            continue
        try:
            fetch_dialect(name, registry_url)
            results.append((name, "updated"))
        except Exception as e:
            results.append((name, f"error: {e}"))

    return results
