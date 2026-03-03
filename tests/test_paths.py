from advanced_menumaker.paths import normalizePath

def test_normalizePath():
    assert normalizePath('../../gizmos') == 'Z:\\Nuke_Workgroup\\gizmos'
