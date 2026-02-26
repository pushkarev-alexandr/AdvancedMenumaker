# Advanced Menumaker
Automatically creates a menu for gizmos from the specified folder.
This tool offers many advanced settings for flexible menu creation and customization.

## Configuration

All configuration is stored in `config.py`.
Below is a description of the main settings:

- **CUSTOM_GIZMOS_PATHS**: List of folder paths for which menus will be created.  
  Each folder uses the common rules described below.

- **IGNORE_FOLDERS_FULL**: Folder names that will be completely ignored.  
  These folders are not added to `pluginPath` and are not shown in the menu.

- **IGNORE_MENU_FOLDERS**: Folder names that will not be added as separate menus.  
  Gizmos from these folders can still be used if the folder is not blocked by `IGNORE_FOLDERS_FULL`.

- **IGNORE_SUBFOLDERS_STRUCTURE**: For these folders all gizmos are placed into a single menu,  
  even if there are subfolders inside. New submenus are not created for subfolders.

- **GROUP_RESTRICTED**: List of gizmo names that must not be loaded as Groups,  
  usually because of special knobs such as `Eyedropper_Knob` or `IArray_Knob` (for example in `PointPositionMask`).

- **IGNORE_GIZMOS**: List of gizmo or file names (with or without extension)  
  for which no menu item will be created.

- **MULTI_MENU_MODE**: Multi-folder mode.  
  When enabled, each subfolder inside the main gizmo folder becomes a separate menu.
  When disabled (default), a single `Gizmos` menu is created with all gizmos and subfolders.

- **MENU_FOR_BASE_FOLDER**: Controls whether a menu is created for the base folder in multi‑menu mode.  
  If `False`, gizmos from `CUSTOM_GIZMOS_PATHS` are ignored when multi‑menu mode is enabled.  
  If `True`, a separate menu is created for the base folder.

- **LOAD_GIZMO_AS_GROUP**: If `True`, gizmos are loaded into Nuke as Groups by default,  
  except for the ones listed in `GROUP_RESTRICTED`.

- **ICONS_IN_SEP_FOLDER**: If `True`, icons are loaded from the folder specified in `ICONS_SEP_FOLDER_PATH`.  
  If `False`, icons are searched next to the gizmo file.

- **ALLOW_ICONS_FROM_PLUGIN_PATH**: If `True`, and the icon cannot be found next to the gizmo  
  or in the separate icons folder (when `ICONS_IN_SEP_FOLDER` is enabled),  
  Nuke will try to resolve the icon from anywhere in `pluginPath`.  
  If `False`, the icon will not be displayed even if it exists somewhere in `pluginPath`.

- **ICONS_EXT**: File extension for icons. Currently only `.png` is supported.
