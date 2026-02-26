import AdvancedMenumaker as am

for CUSTOM_GIZMOS_PATH in am.CUSTOM_GIZMOS_PATHS:
    am.addPluginPathRecursive(CUSTOM_GIZMOS_PATH)
