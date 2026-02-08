def clamp(v, a, b):
    return max(a, min(b, v))

# Resolve asset paths in dev and frozen (PyInstaller) builds.
def asset_path(rel):
    import os
    import sys
    from pathlib import Path

    rel_path = Path(rel)
    # Base for PyInstaller (_MEIPASS) or this file's directory.
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

    candidates = [
        base / rel_path,
        base.parent / rel_path,         # if assets live alongside main/
        Path.cwd() / rel_path,          # current working dir (e.g., web)
        Path(rel),                      # as-given
    ]

    for c in candidates:
        if c.exists():
            return str(c)
    # Fallback to first candidate even if missing to keep predictable paths.
    return str(candidates[0])
