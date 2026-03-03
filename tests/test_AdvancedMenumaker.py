from AdvancedMenumaker import normalizePath

def test_normalizePath():
    assert normalizePath('../../gizmos') == 'Z:\\Nuke_Workgroup\\gizmos'
