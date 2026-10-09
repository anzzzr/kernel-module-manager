"""Backward-compatibility re-export for app.main."""

from kernel_diagnostic_ai.main import app, health, lifespan

__all__ = ["app", "health", "lifespan"]
