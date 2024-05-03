# -*- coding: utf-8 -*-
import sys
spPath = "D:/Cling_toolbox/plug-in/spPaint3d"
scriptPath = spPath + '/scripts'
iconPath = spPath + '/icons'
sys.path.append(scriptPath)

import maya.mel as mel
mel.eval('putenv XBMLANGPATH \"{}\"'.format(iconPath.encode('GBK')))

import spPaint3dGui
spPaint3dwin=spPaint3dGui.spPaint3dWin()
