"""
Configuration variables for AdvancedMenumaker.
Edit values here to customize how gizmo menus are built.
"""

CUSTOM_GIZMOS_PATHS = ['../../gizmos', '~/.nuke/my_gizmos']

IGNORE_FOLDERS_FULL = [
    '__pycache__',
    '.git',
    'autosaves',
    'Cattery',
    'freelance',
    'backup',
    'GizmoPacks',
    'NukeDiffusion',
    'ComfyUI',
    'ComfyUINuke',
    'NukeSamurai',
    'TechCheck',
]

IGNORE_MENU_FOLDERS = ['manual', 'obsolete', 'from_freelance']

IGNORE_SUBFOLDERS_STRUCTURE = ['KZ_toolsets']

GROUP_RESTRICTED = ['PointPositionMask', 'Defocus_Aberrations', 'afanasy', 'ColorMatrixManual']

IGNORE_GIZMOS = ['Conform_base']

MULTI_MENU_MODE = False

MENU_FOR_BASE_FOLDER = True

LOAD_GIZMO_AS_GROUP = True

# Icons
ICONS_IN_SEP_FOLDER = False
ICONS_SEP_FOLDER_PATH = ''
ALLOW_ICONS_FROM_PLUGIN_PATH = False
ICONS_EXT = '.png'

