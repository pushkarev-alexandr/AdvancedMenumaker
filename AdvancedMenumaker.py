"""
AdvancedMenumaker: automatically collects gizmos from configured paths
and creates Nuke menus for them.
"""

import nuke, os
from typing import Any, Optional, Sequence

from advanced_menumaker.config import (
    CUSTOM_GIZMOS_PATHS,
    IGNORE_FOLDERS_FULL,
    IGNORE_MENU_FOLDERS,
    IGNORE_SUBFOLDERS_STRUCTURE,
    GROUP_RESTRICTED,
    IGNORE_GIZMOS,
    MULTI_MENU_MODE,
    MENU_FOR_BASE_FOLDER,
    LOAD_GIZMO_AS_GROUP,
)
from advanced_menumaker.paths import (
    PathInput,
    folderName,
    getIconPath,
    isAnyGizmo,
    isAnyGizmosRecursive,
    normalizePath,
    toNukePath,
)
currentModuleName: str = os.path.splitext(os.path.basename(__file__))[0]

def getNewNodes(allNodes: Sequence[Any]) -> list[Any]:
    """
    Given a list of all nodes before creating new ones, return a list of newly
    created nodes that were not in the original list.
    """
    newNodes = []
    for i in nuke.allNodes():
        if i not in allNodes:
            newNodes.append(i)
    return newNodes

def getLastClickPosition() -> list[int]:
    """
    Return the position of the last mouse click. Works even if nodes are selected:
    temporarily deselects them, creates a Dot to read position, then restores selection.
    """
    selected = nuke.selectedNodes()
    for node in selected:
        node.setSelected(False)
    dot = nuke.createNode('Dot', inpanel=False)
    x = dot.xpos()+dot.screenWidth()/2
    y = dot.ypos()+ dot.screenHeight()/2
    nuke.delete(dot)
    for node in selected:
        node.setSelected(True)
    return [int(x), int(y)]

def inputsFromOneNodeToAnother(fromNode: Any, toNode: Any) -> None:
    """Reconnect all inputs that were connected to fromNode so they connect to toNode."""
    for depNode in fromNode.dependent(forceEvaluate = False):
        for i in range(depNode.inputs()):
            if depNode.input(i)==fromNode:
                depNode.setInput(i, toNode)

def placeNewNode(node):
    """
    Connect the new node and position it in the DAG: either at last click position
    if nothing is selected, or wired to selected nodes with inputs rewired accordingly.
    """
    node.setSelected(False)
    for i in range(node.inputs()):
        node.setInput(i, None)
    selected = nuke.selectedNodes()
    if not selected:
        c = getLastClickPosition()
        node.setXYpos(int(c[0]-node.screenWidth()/2), int(c[1]-node.screenHeight()/2))
    else:
        for i, sel in enumerate(selected):
            if i<node.maxInputs():
                node.setInput(i, sel)
                inputsFromOneNodeToAnother(sel, node)
    for i in selected:
        i.setSelected(False)
    node.setSelected(True)
    node.showControlPanel()

def autocolor(node):
    """If autocolor is enabled in preferences, set the matching tile color for the node."""
    preferences = nuke.toNode('preferences')
    if preferences.knob('autocolor').value():
        for knName in list(preferences.knobs().keys()):
            if knName.startswith('NodeColourClass'):
                classes = preferences.knob(knName).value()
                for keyword in classes.split():
                    if node.name().lower().count(keyword.lower()):
                        color = preferences.knob(knName.replace('Class', '')+'Color').value()
                        node.knob('tile_color').setValue(color)
                        return

def formatGizmoName(basename: str) -> str:
    """
    Build a unique gizmo node name from a file basename: strip extension, replace
    spaces with underscores, append numeric suffix (with extra underscore if name
    ends with a digit). Returns 'untitled' for empty basename.
    """
    if basename=='.gizmo':
        return 'untitled'
    else:
        name = os.path.splitext(basename)[0].replace(' ', '_')
        name += ['', '_'][name[-1].isdigit()]
        for i in range(1, 1000):
            if not nuke.toNode(name+str(i)):
                return name+str(i)
        return 'Something_wrong_with_node_naming'

def loadGizmoAsGroup(pathToGizmo: str) -> None:
    """
    Load a .gizmo file as a Group node: read file, replace 'Gizmo' with 'Group',
    paste into script, then position and name the new node. Falls back to createNode
    if the file format is unexpected.
    """
    if not pathToGizmo.endswith('.gizmo') or not os.path.isfile(pathToGizmo):
        return
    gizmo_line = 'Gizmo {\n'
    group_line = 'Group {\n'
    if nuke.NUKE_VERSION_MAJOR > 12:
        file = open(pathToGizmo, encoding="utf8")
    else:
        file = open(pathToGizmo)
    lines = []
    for line in file:
        lines.append(line)
    file.close()

    basename = os.path.basename(pathToGizmo)
    if lines.count(gizmo_line) == 1:
        i = lines.index(gizmo_line)
        lines.pop(i)
        lines.insert(i, group_line)
        groupText = ''
        for line in lines:
            groupText += line
        allNodes = nuke.allNodes()
        nuke.scriptReadText(groupText)
        newNode = getNewNodes(allNodes)[0]
        placeNewNode(newNode)
        newNode['name'].setValue(formatGizmoName(basename))
        autocolor(newNode)
    else:
        nuke.createNode(basename)

def getPseudonym(menu: Any, fName: str) -> str:
    """If a menu item named fName already exists, return fName with a numeric suffix."""
    if menu.findItem(fName):
        for i in range(1, 100):
            pseudonym = fName+str(i)
            if not menu.findItem(pseudonym):
                return pseudonym
    return fName

def addMenuRecursive(
    menu: Any,
    path: Optional[PathInput],
    isIgnoreSubfolders: bool = False,
    index: int = -1,
    stop: bool = False,
) -> Optional[Any]:
    """
    Recursively add menu items for gizmos under path. isIgnoreSubfolders flattens
    subfolders into the same menu; stop stops recursion (used for base folder in multi-menu mode).
    """
    path = normalizePath(path)
    if not path:
        return None
    fName = folderName(path)
    if fName and fName not in IGNORE_FOLDERS_FULL and fName not in IGNORE_MENU_FOLDERS and isAnyGizmosRecursive(path):
        if isIgnoreSubfolders:
            newMenu = menu
        else:
            newMenu = menu.addMenu(getPseudonym(menu, fName), icon=getIconPath(fName, path), index=index)
        lst = [entry.name for entry in path.iterdir()]
        if isAnyGizmo(lst):
            for i in lst:
                spl = os.path.splitext(i)
                gName = spl[0]
                ext = spl[1]
                if gName in IGNORE_GIZMOS or i in IGNORE_GIZMOS:
                    continue
                if isAnyGizmo([ext]):
                    iconPath = getIconPath(gName, path)
                    if ext=='.gizmo':
                        if LOAD_GIZMO_AS_GROUP and gName not in GROUP_RESTRICTED:
                            gizmo_path = toNukePath(path / i)
                            newMenu.addCommand(gName, f'{currentModuleName}.loadGizmoAsGroup("{gizmo_path}")', icon=iconPath)
                        else:
                            newMenu.addCommand(gName, f'nuke.createNode("{gName}")', icon=iconPath)
                    elif ext=='.nk':
                        nk_path = toNukePath(path / i)
                        newMenu.addCommand(gName, f'nuke.nodePaste("{nk_path}")', icon=iconPath)
        if not stop:
            for i in lst:
                child_path = path / i
                if child_path.is_dir():
                    addMenuRecursive(newMenu, child_path, isIgnoreSubfolders or fName in IGNORE_SUBFOLDERS_STRUCTURE)
        return newMenu
    return None

def addPluginPathRecursive(path: Optional[PathInput]) -> None:
    """
    Add path and all its subfolders to nuke.pluginPath, except folders whose name
    is in IGNORE_FOLDERS_FULL.
    """
    path = normalizePath(path)
    fName = folderName(path)
    if path and path.is_dir() and fName not in IGNORE_FOLDERS_FULL:
        nuke.pluginAddPath(toNukePath(path))
        lst = [entry.name for entry in path.iterdir()]
        for i in lst:
            child_path = path / i
            if child_path.is_dir():
                addPluginPathRecursive(child_path)

def updateMenu(path: Optional[PathInput], name: str, stop: bool = False) -> None:
    """
    Remove the existing menu with the given name and recreate it in the same position.
    Name is passed because it may have a numeric suffix from getPseudonym.
    """
    nodes = nuke.menu('Nodes')
    if nodes.findItem(name):
        index = [i.name() for i in nodes.items()].index(name)
        nodes.removeItem(name)
    else:
        index = -1
    path = normalizePath(path)
    if path and path.is_dir():
        addPluginPathRecursive(path)
        newMenu = addMenuRecursive(nodes, path, index=index, stop=stop)
        if newMenu:
            updateCommand = f'{currentModuleName}.updateMenu("{toNukePath(path)}", "{newMenu.name()}", {stop})'
            newMenu.addCommand('update', updateCommand, icon='update.png')

def createMenu() -> None:
    """
    Entry point called from menu.py on Nuke startup. Creates menus for each path
    in CUSTOM_GIZMOS_PATHS. addPluginPathRecursive is run from init.py, not here.
    """
    for CUSTOM_GIZMOS_PATH in CUSTOM_GIZMOS_PATHS:
        CUSTOM_GIZMOS_PATH = normalizePath(CUSTOM_GIZMOS_PATH)
        if CUSTOM_GIZMOS_PATH and CUSTOM_GIZMOS_PATH.is_dir():
            if not MULTI_MENU_MODE or MENU_FOR_BASE_FOLDER:
                newMenu = addMenuRecursive(nuke.menu('Nodes'), CUSTOM_GIZMOS_PATH, stop=MULTI_MENU_MODE and MENU_FOR_BASE_FOLDER)
                if newMenu:
                    updateCommand = f'{currentModuleName}.updateMenu("{toNukePath(CUSTOM_GIZMOS_PATH)}", "{newMenu.name()}", {MULTI_MENU_MODE and MENU_FOR_BASE_FOLDER})'
                    newMenu.addCommand('update', updateCommand, icon='update.png')
            if MULTI_MENU_MODE:
                lst = [entry for entry in CUSTOM_GIZMOS_PATH.iterdir() if entry.is_dir()]
                for folder in lst:
                    newMenu = addMenuRecursive(nuke.menu('Nodes'), folder)
                    if newMenu:
                        updateCommand = f'{currentModuleName}.updateMenu("{toNukePath(folder)}", "{newMenu.name()}")'
                        newMenu.addCommand('update', updateCommand, icon='update.png')
