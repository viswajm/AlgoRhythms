#!/usr/bin/env python3
"""Common path utilities for the primality testing project."""

from __future__ import annotations

import platform
from pathlib import Path

# Base directories
PYTHON_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PYTHON_DIR.parent
CPP_DIR = PROJECT_ROOT / "cpp"
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"


def resolve_python_path(path: str | Path) -> Path:
    """Resolve a path relative to the python package directory."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else (PYTHON_DIR / candidate).resolve()


def resolve_project_path(path: str | Path) -> Path:
    """Resolve a path relative to the project root."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else (PROJECT_ROOT / candidate).resolve()


def resolve_results_path(path: str | Path = "") -> Path:
    """Resolve a path inside the shared results directory."""
    candidate = Path(path)

    if candidate.is_absolute():
        return candidate

    parts = candidate.parts
    if parts and parts[0] == "results":
        candidate = Path(*parts[1:])

    return (RESULTS_DIR / candidate).resolve()


def ensure_parent_dir(path: Path) -> Path:
    """Create parent directories for the provided path if needed and return it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def format_path(path: Path) -> str:
    """Return a project-relative string for display purposes."""
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def to_wsl_path(path: Path) -> str:
    """Convert a path to its WSL representation when running on Windows."""
    resolved = path.resolve()
    drive = resolved.drive
    if not drive:
        return resolved.as_posix()

    # Example: drive 'C:' -> '/mnt/c/path/to/file'
    drive_letter = drive.rstrip(":").lower()
    remainder = resolved.as_posix().split(":", 1)[-1].lstrip("/")
    return f"/mnt/{drive_letter}/{remainder}"


def detect_cpp_binary(*names: str) -> Path:
    """Return the first existing C++ binary from the provided names."""
    candidates: list[Path] = []
    system = platform.system()

    for name in names:
        path = CPP_DIR / name
        candidates.append(path)
        if path.exists():
            return path

        if system == "Windows" and not name.endswith(".exe"):
            exe_path = CPP_DIR / f"{name}.exe"
            candidates.append(exe_path)
            if exe_path.exists():
                return exe_path

    # Fall back to the first candidate (prefer .exe on Windows if present)
    if candidates:
        return candidates[0]

    raise FileNotFoundError("No candidate binaries provided")
