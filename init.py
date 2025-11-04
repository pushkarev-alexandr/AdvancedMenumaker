#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#v1.1
#create by: Pushkarev Aleksandr

import nuke, os
import AdvancedMenumaker as am

#добавляет в pluginPath все папки из CUSTOM_GIZMOS_PATH если они не запрещены IGNORE_FOLDERS_FULL
#нужно для того чтобы гизмы не раскрытые в группы, работали на ферме(необходимо если гизмы добавляются по имени, а не по полному пути)
#также это запустит init.py файлы в папках из CUSTOM_GIZMOS_PATH(если эти папки не запрещены IGNORE_FOLDERS_FULL)
for CUSTOM_GIZMOS_PATH in am.CUSTOM_GIZMOS_PATHS.split(';'):
    am.addPluginPathRecursive(CUSTOM_GIZMOS_PATH)#внутри функции происходит раскрытие переменных, относительного пути и проверка на существование папки