"""VTMS web API boundary.

This package exposes the deterministic VTMS-V1 simulation engine without
reimplementing thermal physics.
"""

from .app import app

__all__ = ["app"]
