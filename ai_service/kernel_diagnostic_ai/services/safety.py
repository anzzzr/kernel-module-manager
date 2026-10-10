"""Safety filter module for diagnostic recommendations.

Detects and flags dangerous shell execution patterns, destructive disk commands,
privilege escalations, and security-disabling commands returned by LLMs.
"""

import re
from typing import List, Tuple

DANGEROUS_PATTERNS = [
    # Pipe-to-shell patterns: curl ... | sh, wget ... | bash
    (r"(?:curl|wget)[^|\n]+(?:\|\s*(?:ba)?sh|\|\s*sudo\s*(?:ba)?sh)", "PIPE_TO_SHELL"),
    # Destructive deletions: rm -rf / or rm -rf *
    (r"rm\s+-(?:r|f|rf|fr)\s+[/~*]", "DESTRUCTIVE_RM"),
    # Direct raw disk writing: dd of=/dev/sd..., dd of=/dev/nvme...
    (r"\bdd\s+[^>\n]*of=/dev/[a-z0-9]+", "RAW_DISK_OVERWRITE"),
    # Filesystem wiping: mkfs.* /dev/...
    (r"\bmkfs(?:\.[a-z0-9]+)?\s+/dev/[a-z0-9]+", "FILESYSTEM_CREATION"),
    # Insecure permission opens: chmod -R 777 /
    (r"chmod\s+(?:-R\s+)?777\s+[/~]", "INSECURE_PERMISSIONS"),
    # Disabling system security: setenforce 0, disabling Secure Boot entirely, mokutil --disable-validation
    (r"\b(?:setenforce\s+0|mokutil\s+--disable-validation)\b", "DISABLE_SECURITY_CONTROLS"),
    # Adding arbitrary external untrusted repositories / curl to apt sources
    (r"(?:add-apt-repository|curl\s+.*tee\s+/etc/apt/sources)", "UNTRUSTED_PACKAGE_SOURCE"),
]


def scan_recommendation(text: str) -> List[str]:
    """Scan a single recommendation string for dangerous patterns."""
    flags = []
    for pattern, flag_name in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            flags.append(flag_name)
    return flags


def sanitize_recommendations(recommendations: List[str]) -> Tuple[List[str], List[str]]:
    """Scan and sanitize a list of recommendations.

    Returns:
        (sanitized_recommendations, safety_flags)
    """
    cleaned_recs = []
    all_flags = []

    for rec in recommendations:
        detected = scan_recommendation(rec)
        if detected:
            all_flags.extend(detected)
            # Fully redact the dangerous recommendation
            cleaned_recs.append(
                f"[SECURITY WARNING: Blocked dangerous recommendation matching security policy {detected}]"
            )
        else:
            cleaned_recs.append(rec)

    # Deduplicate flags while preserving order
    unique_flags = list(dict.fromkeys(all_flags))
    return cleaned_recs, unique_flags
