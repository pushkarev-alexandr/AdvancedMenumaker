from advanced_menumaker.paths import normalizePath
from pathlib import Path

def test_normalizePath():
    assert normalizePath('../../gizmos') == Path('Z:\\Nuke_Workgroup\\gizmos')
