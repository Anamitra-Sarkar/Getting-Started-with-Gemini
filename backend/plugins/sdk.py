"""Plugin SDK stubs for Vaelis.

Plugins should implement a `register()` function that accepts a `VaelisContext`.
This module provides helper types and a simple registry for server-side plugins.
"""
from typing import Callable, Dict, Any


class VaelisContext:
    def __init__(self, services: Dict[str, Any]):
        self.services = services


_registry: Dict[str, Callable[[VaelisContext], None]] = {}


def register_plugin(name: str, fn: Callable[[VaelisContext], None]):
    _registry[name] = fn


def run_registry(ctx: VaelisContext):
    for name, fn in _registry.items():
        try:
            fn(ctx)
        except Exception:
            pass
