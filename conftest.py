"""
conftest.py — project-root pytest configuration.

Ensures that `proofpatch.sample` resolves to the top-level `sample/`
directory, which lives alongside the `proofpatch/` package directory rather
than inside it.
"""
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Make sure the project root is on sys.path so `proofpatch` (the package
# at proofpatch/) is importable.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Register `proofpatch.sample` as a namespace package backed by ROOT/sample/
# so that `import proofpatch.sample.baseline.pagination` works even though
# `sample/` is a sibling of the `proofpatch/` package directory, not a child.
import proofpatch  # noqa: E402  (ensures the parent package is loaded first)

_sample_path = str(ROOT / "sample")

if "proofpatch.sample" not in sys.modules:
    _pkg = types.ModuleType("proofpatch.sample")
    _pkg.__path__ = [_sample_path]
    _pkg.__package__ = "proofpatch.sample"
    _pkg.__spec__ = None
    sys.modules["proofpatch.sample"] = _pkg
    proofpatch.sample = _pkg  # type: ignore[attr-defined]
