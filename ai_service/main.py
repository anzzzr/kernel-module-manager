"""Legacy entrypoint — redirects to app.main for backward compatibility.

Usage:
    uvicorn main:app          (old-style, still works)
    uvicorn app.main:app      (preferred)
"""

from app.main import app  # noqa: F401
