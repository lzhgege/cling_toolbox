# -*- coding:utf-8 -*-
import maya.cmds as cm
import os
import re
import functools

u'''
调用库格式：
import toolbox_library.modeling.checkRename as checkRename
#获取第一组重名模型，没有重名返回None
#参数compareNameSpace:是否对比命名空间
#参数compareShape:是否对比shape
checkRename.getFirstAllPolygonSameNameList(compareNameSpace,compareShape)
#获取第一组重名dag节点，没有重名返回None
checkRename.getFirstAllSameNameList(compareNameSpace,compareShape)
'''


def getTransformListFromSubMesh(obj,longName = False):
    u'''
    返回子物体为polygon的transform列表
    '''
    tList = list()
    if longName:
        pa = False
        f = True
    else:
        pa = True
        f = False
    shapeList = cm.ls(obj,dagObjects = True,type = ['mesh'],noIntermediate = True)
    for shape in shapeList:
        transformList = cm.listRelatives(shape,pa = pa,f = f,p = True)
        if not transformList[0] in tList:
            tList.append(transformList[0])
    return tList

def getSameNameList(nameList,compareNameSpace = False):
    u'''
    检查重名
    返回重名列表

    compareNameSpace:是否对比命名空间，是则加入命名空间再对比重名
    '''
    sameNameGrp = list() 
    while nameList:  
        if compareNameSpace:
            shortName = nameList[0].split('|')[-1]
            id1 = [i for i,x in enumerate(nameList) if x.split('|')[-1] == shortName]
        else:
            shortName = nameList[0].split('|')[-1].split(':')[-1]
            id1 = [i for i,x in enumerate(nameList) if x.split('|')[-1].split(':')[-1] == shortName]
        if id1:
            sameNameList = list()
            for id in id1:
                sameNameList.append(nameList[id])
            for i in range(len(id1) - 1,-1,-1):
                del nameList[id1[i]]
            #print(nameList)
            if len(sameNameList) > 1:
                sameNameGrp.append(sameNameList)
    return sameNameGrp


def getFirstSameNameList(nameList,compareNameSpace = False):
    u'''
    检查重名
    返回第一组重名列表

    compareNameSpace:是否对比命名空间，是则加入命名空间再对比重名
    '''
    while nameList:  
        if compareNameSpace:
            shortName = nameList[0].split('|')[-1]
            id1 = [i for i,x in enumerate(nameList) if x.split('|')[-1] == shortName]
        else:
            shortName = nameList[0].split('|')[-1].split(':')[-1]
            id1 = [i for i,x in enumerate(nameList) if x.split('|')[-1].split(':')[-1] == shortName]
        if id1:
            sameNameList = list()
            for id in id1:
                sameNameList.append(nameList[id])
            for i in range(len(id1) - 1,-1,-1):
                del nameList[id1[i]]
            #print(nameList)
            if len(sameNameList) > 1:
                return sameNameList
    return None

def getAllPolygons():
    u'''
    获取场景内所有shape为mesh的transform
    '''
    allMeshList = cm.ls(type = 'mesh')
    polygonList = list()
    for mesh in allMeshList:
        transformList = cm.listRelatives(mesh,p = True,pa = True)
        polygonList.append(transformList[0])
    polygonList = list(set(polygonList))
    polygonList.sort()
    return polygonList

def getAllPolygonList(compareShape):
    if compareShape:
        allPolygonList = getAllPolygons()
        allMeshList = cm.ls(type = 'mesh')
        allPolygonList.extend(allMeshList)
    else:
        allPolygonList = getAllPolygons()
    return allPolygonList

def getAllDagList(compareShape):
    if compareShape:
        allDagList = cm.ls(dag = True)
    else:
        allDagList = cm.ls(type = 'transform')
    return allDagList

def getFirstAllPolygonSameNameList(compareNameSpace,compareShape = False):
    u'''
    返回场景内重名的transform(shape为mesh)的第一组
    :param compareNameSpace:是否对比命名空间
    :param compareShape:是否对比shape
    :return:有重名返回list，无返回None
    '''
    return getFirstSameNameList(getAllPolygonList(compareShape),compareNameSpace)

def getAllPolygonSameNameList(compareNameSpace,compareShape = False):
    u'''
    返回场景内所有的重名的transform(shape为mesh)
    格式为外面一个列表，里面有若干列表，
    里面的每个列表是同名但不同路径的transform
    '''
    return getSameNameList(getAllPolygonList(compareShape),compareNameSpace)
    # if sameNameList:
    #     for sameName in sameNameList:
    #         print(sameName)

def getFirstAllSameNameList(compareNameSpace,compareShape = False):
    u'''
    返回场景内重名的dagObject的第一组
    :param compareNameSpace:是否对比命名空间
    :param compareShape:是否对比shape
    :return:有重名返回list，无返回None
    '''
    return getFirstSameNameList(getAllDagList(compareShape),compareNameSpace)

def getAllSameNameList(compareNameSpace,compareShape = False):
    u'''
    返回场景内所有的重名的dagObject
    格式为外面一个列表，里面有若干列表，
    里面的每个列表是同名但不同路径的dagObject
    '''
    return getSameNameList(getAllDagList(compareShape),compareNameSpace)
