# -*- coding:utf-8 -*-
import maya.cmds as cm
import os
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import re
try:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import __version__
    from shiboken import wrapInstance
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2 import __version__
    from shiboken2 import wrapInstance

u'''
#从maya检测场景是否有按面给材质的物体：

import toolbox_library.modeling.checkAssignFaceShader as checkAssignFaceShader

if checkAssignFaceShader.getFirstAssignFaceShaderObjFromAll():
    print(u'有按面给材质的物体！')
else:
    print(u'没有按面给材质的物体！')
'''

def getFaceShaderType(obj):
    u'''
    是否按面给材质的物体,
    return：
    0：不是按面给
    1：按面给，但可以修复(所有面给一个材质球)
    2：按面给，不可以修复(起码有两个材质球是按面给材质的情况)
    '''
    shapeList = cm.listRelatives(obj,s = True,pa = True,ni = True)
    #print(shapeList)
    if shapeList:
        faceSgSet = set()
        instGrps = cm.getAttr('%s.instObjGroups'%shapeList[0])
        if instGrps:
            for i in range(len(instGrps)):
                objGrps = cm.getAttr('%s.instObjGroups[%d].objectGroups'%(shapeList[0],i),mi = True)
                if objGrps:
                    for j in range(len(objGrps)):
                        sgList = cm.listConnections('%s.instObjGroups[%d].objectGroups[%d]'%(shapeList[0],i,objGrps[j]),s = False,type = 'shadingEngine')
                        connectionList = cm.listConnections('%s.instObjGroups[%d].objectGroups[%d]'%(shapeList[0],i,objGrps[j]),s = False,type = 'shadingEngine',connections = True,plugs = True)

                        if sgList:
                            
                            for i in range(0,len(connectionList),2):
                                
                                compList = cm.getAttr('%s.objectGrpCompList'%connectionList[i])
                                if compList:
                                    for comp in compList:
                                        if re.match('f\[(\d+):(\d+)\]|f\[(\d+)\]',comp):
                                            faceSgSet.add(sgList[i / 2])
                                            break
        faceSgSetCount = len(faceSgSet)
        if faceSgSetCount > 1:
            return 2
        elif faceSgSetCount == 1:
            return 1
        else:
            return 0
        return 0
    else:
        return 0

def getAssignFaceShaderTypeList(objList):
    canFixList = list()
    badList = list()

    for obj in objList:
        
        faceShaderType = getFaceShaderType(obj)
        if faceShaderType == 1:

            canFixList.append(obj)
        elif faceShaderType == 2:
            badList.append(obj)

    return canFixList,badList

def getFirstAssignFaceShaderObj(objList):
    canFixList = list()
    badList = list()

    for obj in objList:
        
        faceShaderType = getFaceShaderType(obj)
        if faceShaderType != 0:

            return obj

    return None

def getFirstAssignFaceShaderObjFromAll():
    u'''
    获取首个按面给材质的物体，如果无则返回None
    '''
    objList = list()
    allMesh = cm.ls(type = 'mesh',ni = True)
    for mesh in allMesh:
        transformList = cm.listRelatives(mesh,p = True,pa = True,type = 'transform')
        if transformList:
            objList.append(transformList[0])
    return getFirstAssignFaceShaderObj(objList)

def getAssignFaceShaderTypeListFromAll():
    u'''
    获取所有按面给材质的物体名字,分两个列表，一个可修复，一个不可修复
    '''
    objList = list()
    allMesh = cm.ls(type = 'mesh',ni = True)
    for mesh in allMesh:
        transformList = cm.listRelatives(mesh,p = True,pa = True,type = 'transform')
        if transformList:
            objList.append(transformList[0])
    return getAssignFaceShaderTypeList(objList)