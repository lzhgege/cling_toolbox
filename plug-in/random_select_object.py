# -*- coding: utf-8 -*-
import random
import maya.cmds as cm
def selectPart(objList,percent):    
    objListCount = len(objList)
    percentList = list()
    while len(percentList) < int(objListCount * 1.0 * percent / 100) :
        index = random.randint(0, objListCount - 1)
        if not index in percentList:
            percentList.append(index)
    return percentList

def randomSelect(*argvs): 
    objList = cm.ls(sl = True) 
    percent = cm.intSliderGrp( 'eaPercentIntFieldGrp',q = True, v = True)
    indexList = selectPart(objList,percent)
    cm.select(clear = True)
    for i in indexList:
        cm.select(objList[i],add = True)
        
def randomSelectUI():
    win = 'randomSelectWin'
    if cm.window(win,exists = True):
        cm.deleteUI(win)
    cm.window(win,title = u'随机按百分比选择物体')
    cm.window(win,e = True,w = 250,h = 60)
    cm.columnLayout(adj = True)
    cm.intSliderGrp( 'eaPercentIntFieldGrp', field=True, h=50, label=u'百分比', el=u'%', 
                    minValue=0, maxValue=100, fieldMinValue=0, fieldMaxValue=100, value=50,
                    cw4=[50, 50, 100, 30] )
    cm.separator(h=10, st='none')                
    cm.button(c = randomSelect,h = 60,l = u'选择')
    cm.showWindow(win)
randomSelectUI()