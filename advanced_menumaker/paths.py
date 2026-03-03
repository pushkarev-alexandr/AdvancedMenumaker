"""
Helpers for working with filesystem paths and icon locations.
"""

import os
from pathlib import Path
from typing import Optional, Sequence, Union

from advanced_menumaker.config import (
    ALLOW_ICONS_FROM_PLUGIN_PATH,
    ICONS_EXT,
    ICONS_IN_SEP_FOLDER,
    ICONS_SEP_FOLDER_PATH as CONFIG_ICONS_SEP_FOLDER_PATH,
)

PathInput = Union[str, Path]


def normalizePath(path: Optional[PathInput]) -> Optional[Path]:
    """
    Expand vars/user and resolve relative paths against this file location.
    Returns None for empty input.
    """
    if not path:
        return None
    expanded = os.path.expandvars(os.path.expanduser(str(path)))
    normalized = Path(expanded)
    if not normalized.is_absolute():
        # Use abspath to keep drive letter (e.g. Z:) instead of converting to UNC.
        # Resolve relative paths against the project root (folder that contains this package).
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        base = Path(project_root)
        normalized = base / normalized
    # Collapse any ".." while preserving drive letter
    return Path(os.path.abspath(str(normalized)))


def toNukePath(path: PathInput) -> str:
    """Convert Path/string to Nuke-friendly path with forward slashes."""
    return Path(path).as_posix()


def isAnyGizmo(lst: Sequence[str]) -> bool:
    """Return True if at least one string in the list has a .gizmo or .nk extension."""
    for i in lst:
        if i.endswith(".gizmo") or i.endswith(".nk"):
            return True
    return False


def isAnyFolder(path: Path, lst: Sequence[str]) -> bool:
    """Return True if path contains at least one directory whose name is in lst."""
    for i in lst:
        if (path / i).is_dir():
            return True
    return False


def isAnyGizmosRecursive(path: Optional[PathInput]) -> bool:
    """Recursively walk the folder and its contents; return True if any gizmo is found."""
    path = normalizePath(path)
    if path and path.is_dir():
        lst = [entry.name for entry in path.iterdir()]
        if isAnyGizmo(lst):
            return True
        elif isAnyFolder(path, lst):
            for i in lst:
                if isAnyGizmosRecursive(path / i):
                    return True
    return False


def folderName(path: Optional[PathInput]) -> str:
    """Return the last non-empty component of the path (the folder name)."""
    path = normalizePath(path)
    if path:
        return path.name
    return ""


_ICONS_SEP_FOLDER_PATH: Optional[Path] = normalizePath(CONFIG_ICONS_SEP_FOLDER_PATH)


def getIconPath(name: str, path: Optional[PathInput] = None) -> str:
    """
    Return path to an icon (absolute or relative). name is the icon name without
    extension; path is the folder of the current gizmo/menu. Only .png is supported.
    """
    if ICONS_IN_SEP_FOLDER:
        if _ICONS_SEP_FOLDER_PATH:
            icon = _ICONS_SEP_FOLDER_PATH / (name + ICONS_EXT)
            if icon.is_file():
                return toNukePath(icon)
    elif path:
        base_path = normalizePath(path)
        if base_path:
            icon = base_path / (name + ICONS_EXT)
            if icon.is_file():
                return toNukePath(icon)
    if ALLOW_ICONS_FROM_PLUGIN_PATH:
        return name + ICONS_EXT
    else:
        return ""

