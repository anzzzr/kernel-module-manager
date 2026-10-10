"""Response caching engine with TTL and SHA-256 fingerprinting."""

import hashlib
import time
from typing import Any, Dict, Optional

# In-memory LRU-style cache: {hash: (response_dict, expiry_time)}
_CACHE: Dict[str, tuple[Dict[str, Any], float]] = {}
_DEFAULT_TTL = 300.0  # 5 minutes TTL

# Operational Cache Counters
_cache_hits = 0
_cache_misses = 0


def generate_cache_key(evidence_json: str, corpus_version: str, model_name: str) -> str:
    """Generate deterministic SHA-256 cache key from evidence, corpus, and model."""
    fingerprint = f"{evidence_json}|{corpus_version}|{model_name}"
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()


def get_cached_response(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve response from cache if not expired."""
    global _cache_hits, _cache_misses
    now = time.time()
    if key in _CACHE:
        entry, expiry = _CACHE[key]
        if now < expiry:
            _cache_hits += 1
            return entry
        else:
            del _CACHE[key]
    _cache_misses += 1
    return None


def store_cached_response(key: str, response: Dict[str, Any], ttl_seconds: float = _DEFAULT_TTL):
    """Store response in cache with TTL."""
    # Prevent unbounded growth: evict expired or oldest
    if len(_CACHE) > 500:
        now = time.time()
        expired = [k for k, (_, exp) in _CACHE.items() if now >= exp]
        for k in expired:
            del _CACHE[k]
        if len(_CACHE) > 500:
            first_key = next(iter(_CACHE))
            del _CACHE[first_key]

    _CACHE[key] = (response, time.time() + ttl_seconds)


def get_cache_stats() -> Dict[str, Any]:
    """Return cache operational metrics."""
    total = _cache_hits + _cache_misses
    hit_rate = (float(_cache_hits) / float(total)) if total > 0 else 0.0
    return {
        "cache_hits": _cache_hits,
        "cache_misses": _cache_misses,
        "total_lookups": total,
        "hit_rate": hit_rate,
        "cached_entries": len(_CACHE),
    }


def clear_cache():
    """Clear all cached entries and counters."""
    global _cache_hits, _cache_misses
    _CACHE.clear()
    _cache_hits = 0
    _cache_misses = 0

