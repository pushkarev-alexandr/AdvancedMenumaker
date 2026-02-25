#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#автоматически подтягивает гизмы и создает для них меню

#v2.1.1
#create by: Pushkarev Aleksandr

#CUSTOM_GIZMOS_PATHS через точку с запятой ; можно написать пути до папок для которых будет создаваться менюшка, для каждой отдельной папки будут действовать общие правила описанные ниже
#IGNORE_FOLDERS_FULL папки с такими названиеми не будут добавляться в pluginPath и менюшку, полное игнорирование папки
#IGNORE_MENU_FOLDERS папки с этими названиями не будут создаваться в меню, но гизмы из этой папки могут использоваться если они не запрещены IGNORE_FOLDERS_FULL
#полезно для папок с устаревшими гизмами, для обратной совместимости или для папок внутри которых есть свой menu.py который сам создает менюшку
#IGNORE_SUBFOLDERS_STRUCTURE все гизмы из этой папки будут в одной менюшке, даже если внутри папки есть подпапки, новые менюшки создаваться не будут
#GROUP_RESTRICTED список названий гизм, которым нельзя быть группами, из-за специфичных кнобов по типу Eyedropper_Knob или IArray_Knob в гизме PointPositionMask
#IGNORE_GIZMOS список имен гизм или файлов (с расширением или без), для которых не будет создаваться пункт в меню
#MULTI_MENU_MODE мультипапочный режим, когда внутри папки Gizmos каждая папка, это отдельная менюшка
#по умолчанию этот режим False, что означает, что будет создана одна менюшка Gizmos в которой будут все гизмы и подпапки
#MENU_FOR_BASE_FOLDER если включен мультипапочный режим этот параметр разрешает или запрещает создание менюшки для основной базовой папки CUSTOM_GIZMOS_PATH
#если False то гизмы из папки CUSTOM_GIZMOS_PATH будут игнорироваться при мультипапочном режиме, если True то для них создастся отдельная менюшка
#LOAD_GIZMO_AS_GROUP гизмы будут подгружаться в нюк сразу как группы, за исключением тех что запрещены GROUP_RESTRICTED
#ICONS_IN_SEP_FOLDER если True то для иконок будет использоваться папка которая указана в переменной ICONS_SEP_FOLDER_PATH
#ALLOW_ICONS_FROM_PLUGIN_PATH если True, то если картинку не удастся найти рядом с гизмой или в отдельной папке если включен режим ICONS_IN_SEP_FOLDER
#картинка попробует найтись в любом месте из pluginPath, если False то картинка не отобразиться даже если она лежит где-то в pluginPath
#ICONS_EXT расширение для иконок, сейчас разрешается только .png

import nuke, os

CUSTOM_GIZMOS_PATHS = '.../gizmos;~/.nuke/my_gizmos'
IGNORE_FOLDERS_FULL = ['__pycache__','.git','autosaves','Cattery','Cryptomatte-master','freelance','backup','autosaves','GizmoPacks','NukeDiffusion','ComfyUI','ComfyUINuke','NukeSamurai', 'Beeble', 'TechCheck']#__pycache__ на всякий случай,   'byn_test_02','MRP' не используются,   у Cattery свой рекурсивный проход pluginPath и добавляется она в menu.py
IGNORE_MENU_FOLDERS = ['manual','obsolete','from_freelance']
IGNORE_SUBFOLDERS_STRUCTURE = ['KZ_toolsets']
GROUP_RESTRICTED = ['PointPositionMask','Defocus_Aberrations','afanasy','ColorMatrixManual']
IGNORE_GIZMOS = ['Conform_base']
MULTI_MENU_MODE = False
MENU_FOR_BASE_FOLDER = True
LOAD_GIZMO_AS_GROUP = True
#icons
ICONS_IN_SEP_FOLDER = False
ICONS_SEP_FOLDER_PATH = ''
ALLOW_ICONS_FROM_PLUGIN_PATH = False
ICONS_EXT = '.png'

#one dot means current directory, 2 dots - up one level, 3 dots - up two level etc.
def bakeRelativePath(path):
    if path.startswith('.'):
        dirname = os.path.dirname(__file__).replace('\\','/')+'/'
        c = len(path)-len(path.lstrip('.'))
        spl = dirname.split('/')
        if len(spl)>c:
            resSpl = spl[:-c]
        else:
            resSpl = spl[:1]
        return '/'.join(resSpl)+path.lstrip('.')
    return path

#заменяет обратные слеши на прямые и добавляет слэш в конце если его нету, если строка пустая, возвращает пустую строку
#также переводит переменные ~ и %home% в C:\Users\Fincher(в зависимости от пользователя)
def checkPath(path):
    if path:
        if path.startswith('~'):
            path = os.path.expanduser(path)
        elif path.lower().startswith('%home%'):
            path = os.path.expandvars(path)
        path = path.replace('\\','/')
        if not path.endswith('/'):
            path += '/'
        return path
    return ''

#подготовка переменных
ICONS_SEP_FOLDER_PATH = checkPath(ICONS_SEP_FOLDER_PATH)
currentModuleName = os.path.splitext(os.path.basename(__file__))[0]

#возвращает True если хотябы одна строка из списка имеет расширение .gizmo или .nk
def isAnyGizmo(lst):
    for i in lst:
        if i.endswith('.gizmo') or i.endswith('.nk'):
            return True
    return False

def isAnyFolder(path,lst):
    for i in lst:
        if os.path.isdir(path+i):
            return True
    return False

#проходится рекурсивно по всей папке и ее содержимому и возвращает True если хоть где-либо найдет гизму
def isAnyGizmosRecursive(path):
    path = checkPath(path)
    if os.path.isdir(path):
        lst = os.listdir(path)
        if isAnyGizmo(lst):
            return True
        elif isAnyFolder(path,lst):
            for i in lst:
                if isAnyGizmosRecursive(path+i):
                    return True
    return False

#получает на вход список всех нод до создания каких-либо новых нод
#возвращает список новых созданных нод которых не оказалось в старом списке
def getNewNodes(allNodes):
    newNodes = []
    for i in nuke.allNodes():
        if i not in allNodes:
            newNodes.append(i)
    return newNodes

#возвращает место последнего клика мышью, даже если были выбранны ноды, снимает выделение создает точку и потом возвращает выделение
def getLastClickPosition():
    selected = nuke.selectedNodes()
    for node in selected:
        node.setSelected(False)
    dot = nuke.createNode('Dot',inpanel=False)
    x = dot.xpos()+dot.screenWidth()/2
    y = dot.ypos()+ dot.screenHeight()/2
    nuke.delete(dot)
    for node in selected:
        node.setSelected(True)
    return [int(x),int(y)]

#берет все инпуты которые воткнуты в ноду fromNode и втыкает их в ноду toNode
def inputsFromOneNodeToAnother(fromNode,toNode):
    for depNode in fromNode.dependent(forceEvaluate = False):
        for i in range(depNode.inputs()):
            if depNode.input(i)==fromNode:
                depNode.setInput(i,toNode)

#здесь вся логика подсоединения и выставления положения ноды 
def placeNewNode(node):
    node.setSelected(False)#хотя гизмы в основном создаются без выделения, на всякий случай снимем выделение с ноды
    for i in range(node.inputs()):#а также отсоединим все инпуты
        node.setInput(i,None)
    selected = nuke.selectedNodes()
    if not selected:#если никаких нод не выбранно, создаем ноду в месте где был сделан последний клик мышью
        c = getLastClickPosition()
        node.setXYpos(int(c[0]-node.screenWidth()/2),int(c[1]-node.screenHeight()/2))
    else:#в противном случае подсоединяем ноду к выбранным нодам, с учетом максимального кол-ва входов нашей ноды
        for i,sel in enumerate(selected):
            if i<node.maxInputs():
                node.setInput(i,sel)
                inputsFromOneNodeToAnother(sel,node)#и для каждой ноды к которой мы подсоединяемся, инпуты которые были в нее воткнуты перетыкаем в нашу новую ноду
    for i in selected:#снимаем выделение со всех выбранных нод
        i.setSelected(False)
    node.setSelected(True)
    node.showControlPanel()

#если в настройках включен autocolor, выставит нужный цвет для ноды
def autocolor(node):
    preferences = nuke.toNode('preferences')
    if preferences.knob('autocolor').value():#если autocolor разрешен
        for knName in list(preferences.knobs().keys()):
            if knName.startswith('NodeColourClass'):#находим кнобы ответственные за цвет
                classes = preferences.knob(knName).value()
                for keyword in classes.split():#смторим есть ли какое-либо ключевое слово в имени нашей ноды
                    if node.name().lower().count(keyword.lower()):#если есть то выставляем цвет и выходим из функции
                        color = preferences.knob(knName.replace('Class','')+'Color').value()
                        node.knob('tile_color').setValue(color)
                        return

#из имени файла basename делает подходящее для гизмы имя
#если у гизмы нет имени называет ее untitled, отбрасывает расширение и заменяет пробелы на подчеркивания, добавляет цифру 1 в конце(через подчеркивание если в названии гизмы есть цифра в конце)
def formatGizmoName(basename):
    if basename=='.gizmo':
        return 'untitled'
    else:
        name = os.path.splitext(basename)[0].replace(' ','_')#заменяем пробелы на подчеркивания
        name+=['','_'][name[-1].isdigit()]#добавляет подчеркивание в конце если имя заканчивается на цифру
        for i in range(1,1000):
            if not nuke.toNode(name+str(i)):
                return name+str(i)
        return 'Something_wrong_with_node_naming'

#на вход подается полный путь до гизмы, которая подгружается как группа
def loadGizmoAsGroup(pathToGizmo):
    if not pathToGizmo.endswith('.gizmo') or not os.path.isfile(pathToGizmo):#если это не гизма или файла не существует выходим из функции
        return
    gizmo_line = 'Gizmo {\n'
    group_line = 'Group {\n'
    #читаем файл, записываем линии в список
    if nuke.NUKE_VERSION_MAJOR>12:
        file = open(pathToGizmo, encoding="utf8")
    else:
        file = open(pathToGizmo)
    lines = []
    for line in file:
        lines.append(line)
    file.close()

    basename = os.path.basename(pathToGizmo)
    if lines.count(gizmo_line)==1:#у гизмы может быть только одна строчка 'Gizmo {\n'
        #заменяем в тексте 'Gizmo {\n' на 'Group {\n'
        i = lines.index(gizmo_line)
        lines.pop(i)
        lines.insert(i,group_line)
        #собираем текст обратно
        groupText = ''
        for line in lines:
            groupText+=line
        allNodes = nuke.allNodes()#запоминаем все ноды до добавления гизмы
        nuke.scriptReadText(groupText)#добавляем гизму из текста
        newNode = getNewNodes(allNodes)[0]#находим только что созданную ноду
        placeNewNode(newNode)#выставляем позицию и подсоединяем инпуты
        newNode['name'].setValue(formatGizmoName(basename))#выставляем имя для ноды
        autocolor(newNode)#выставляем цвет для ноды
    else:
        nuke.createNode(basename)#создание ноды по имени предполагает, что папка в которой лежит нода добавлена в pluginPath

#возвращает полный или относительный путь до иконки в зависимости от переменных, допускается только png
def getIconPath(name,path=None):#name имя икноки без расширения, path путь до папки для текущей гизмы или менюшки для которой мы ищем иконку
    if ICONS_IN_SEP_FOLDER:#если для иконок есть отдельная папка, ищем иконку там
        icon = ICONS_SEP_FOLDER_PATH+name+ICONS_EXT
        if os.path.isfile(icon):#если по найденному пути есть картинка, возвращаем путь до нее
            return icon
    elif path:#если нету отдельной папки, должна быть текущая папка
        icon = checkPath(path)+name+ICONS_EXT
        if os.path.isfile(icon):#если по найденному пути есть картинка, возвращаем путь до нее
            return icon
    #если найти картинку по конкретному пути не получилось, тогда если можно искать картинку в plugin path росто вернем имя картинки плюс расширение, иначе пустую строку
    if ALLOW_ICONS_FROM_PLUGIN_PATH:
        return name+ICONS_EXT
    else:
        return ''

#проверяет нет ли уже менюшки с именем fName если есть, вернет имя с цифрой на конце
def getPseudonym(menu,fName):
    if menu.findItem(fName):#если такая менюшка уже существует нужно добавить число в конец имени
        for i in range(1,100):
            pseudonym = fName+str(i)
            if not menu.findItem(pseudonym):#если мы нашли название которого нету в менюшке, будем использовать его
                return pseudonym
    return fName

def folderName(path):
    path = checkPath(path)
    spl = path.split('/')
    if spl:
        spl.reverse()
        for i in spl:
            if i:
                return i
    return ''

#isIgnoreSubfolders если True, будет передоваться дальше рекурсивно всем вложенным папкам, и новые менюшки не будут создаваться, все будет в одной менюшке
#stop означает что рекурсия останавливается и дальше папки не рассматриваются
def addMenuRecursive(menu,path,isIgnoreSubfolders=False,index=-1,stop=False):
    path = checkPath(path)#раскрываем переменные, добавляем слеш в конце
    fName = folderName(path)#получаем имя текущей папки
    if fName and fName not in IGNORE_FOLDERS_FULL and fName not in IGNORE_MENU_FOLDERS and isAnyGizmosRecursive(path):#если внутри ни на каком уровне нету гизм, то менюшку создавать не надо
        if isIgnoreSubfolders:#если isIgnoreSubfolders то новую менюшку не создаем, работаем в старой
            newMenu = menu
        else:
            newMenu = menu.addMenu(getPseudonym(menu,fName),icon=getIconPath(fName,path),index=index)
        lst = os.listdir(path)#на уровень выше в том месте где вызывается функция addMenuRecursive должна быть проверка на существование папки, поэтому здесь ее нету(хотя можно и добавить)
        if isAnyGizmo(lst):#если конкретно в текущей папке есть гизмы, то нужно создать для них пункты в меню
            for i in lst:
                spl = os.path.splitext(i)
                gName = spl[0]
                ext = spl[1]#расширение с точкой
                #пропускаем гизмы/файлы, которые пользователь указал в списке IGNORE_GIZMOS
                if gName in IGNORE_GIZMOS or i in IGNORE_GIZMOS:
                    continue
                if isAnyGizmo([ext]):
                    iconPath = getIconPath(gName,path)
                    if ext=='.gizmo':
                        if LOAD_GIZMO_AS_GROUP and gName not in GROUP_RESTRICTED:#если гизму нужно и можно заргужать как группу, загружаем как группу
                            newMenu.addCommand(gName,currentModuleName+'.loadGizmoAsGroup("'+path+i+'")',icon=iconPath)
                        else:#иначе загружаем классическим способо через createNode, здесь уже загрузится нода как гизма или как группа зависит от разметки в самом файле .gizmo
                            newMenu.addCommand(gName,'nuke.createNode("'+gName+'")',icon=iconPath)
                    elif ext=='.nk':#файлы с расширением nk добавляются единственно возможным способом через nodePaste, ему нужно подавать полный путь до файла
                        newMenu.addCommand(gName,'nuke.nodePaste("'+path+i+'")',icon=iconPath)
        if not stop:#stop используется при создании менюшки для основной папки CUSTOM_GIZMOS_PATH в мультипапочном режиме
            for i in lst:
                if os.path.isdir(path+i):
                    addMenuRecursive(newMenu,path+i,isIgnoreSubfolders or fName in IGNORE_SUBFOLDERS_STRUCTURE)
        return newMenu
    return None

#добавляет все папки из path в pluginPath включая саму папку path, только если имя папки не из списка IGNORE_FOLDERS_FULL
def addPluginPathRecursive(path):
    path = bakeRelativePath(path)#расскрываем относительный путь
    path = checkPath(path)#раскрываем переменные, добавляем слеш в конце
    fName = folderName(path)#получаем имя папки
    #проверяем что папка сущесвует чтобы не сломалась функция listdir
    if os.path.isdir(path) and fName not in IGNORE_FOLDERS_FULL:#если папка в списке IGNORE_FOLDERS_FULL, то она не будет добавляться в pluginPath в том числе и все вложенные в неё папки
        nuke.pluginAddPath(path)
        lst = os.listdir(path)
        for i in lst:
            if os.path.isdir(path+i):#проверяем что это папка а не файл
                addPluginPathRecursive(path+i)

#удаляет и создает заново менюшку в том же месте
#передаем имя менюшки name потому что она могла быть названа с добавлением цифры на конце
def updateMenu(path,name,stop=False):
    nodes = nuke.menu('Nodes')
    #если такая менюшка существует, ее надо удалить и запомнить на каком месте она стояла чтобы новую добавить туда же
    if nodes.findItem(name):
        index = [i.name() for i in nodes.items()].index(name)
        nodes.removeItem(name)
    else:
        index = -1
    if os.path.isdir(path):#если папка существует, то добавляем менюшку на старое место, если нет, то мы просто прошлым действием удалили менюшку
        addPluginPathRecursive(path)
        newMenu = addMenuRecursive(nodes,path,index=index,stop=stop)
        if newMenu:
            updateCommand = '{}.updateMenu("{}","{}",{})'.format(currentModuleName,path,newMenu.name(),stop)
            newMenu.addCommand('update',updateCommand,icon='update.png')

#запускается из menu.py при запуске нюка, создает менюшки
#здесь не запускается addPluginPathRecursive потому что он запускается в init.py при старте нюка
def createMenu():
    for CUSTOM_GIZMOS_PATH in CUSTOM_GIZMOS_PATHS.split(';'):
        CUSTOM_GIZMOS_PATH = bakeRelativePath(CUSTOM_GIZMOS_PATH)#расскрываем относительный путь
        CUSTOM_GIZMOS_PATH = checkPath(CUSTOM_GIZMOS_PATH)#раскрываем переменные, добавляем слеш в конце
        if os.path.isdir(CUSTOM_GIZMOS_PATH):#все заработает только если такая папка существует
            if not MULTI_MENU_MODE or MENU_FOR_BASE_FOLDER:#создаем менюшку из папки CUSTOM_GIZMOS_PATH если это не мультипапочный режим или если в мультипапочном режиме включен режим для базовой папки
                newMenu = addMenuRecursive(nuke.menu('Nodes'),CUSTOM_GIZMOS_PATH,stop=MULTI_MENU_MODE and MENU_FOR_BASE_FOLDER)
                if newMenu:#в конце добавляем кнопку update
                    updateCommand = '{}.updateMenu("{}","{}",{})'.format(currentModuleName,CUSTOM_GIZMOS_PATH,newMenu.name(),MULTI_MENU_MODE and MENU_FOR_BASE_FOLDER)
                    newMenu.addCommand('update',updateCommand,icon='update.png')
            if MULTI_MENU_MODE:#если мультипапочный режим, то создаем менюшки для каждой папки внутри CUSTOM_GIZMOS_PATH
                lst = os.listdir(CUSTOM_GIZMOS_PATH)
                for folder in [CUSTOM_GIZMOS_PATH+f for f in lst if os.path.isdir(CUSTOM_GIZMOS_PATH+f)]:
                    newMenu = addMenuRecursive(nuke.menu('Nodes'),folder)
                    if newMenu:
                        updateCommand = '{}.updateMenu("{}","{}")'.format(currentModuleName,folder,newMenu.name())
                        newMenu.addCommand('update',updateCommand,icon='update.png')