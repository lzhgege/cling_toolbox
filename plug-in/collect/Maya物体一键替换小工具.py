# -*- coding: utf-8 -*-
import pymel.core as pm
import webbrowser

name = "cling"
biaoti = "Maya�滻С����"

#-------------------------------------------------------------------------------
#�������
#-------------------------------------------------------------------------------
def FrameUI():
    try:
        pm.deleteUI(name)
    except:
        pass
            
    pm.window(name, title=biaoti, bgc=(0, 0, 0.1)) 
    
    
    
    pm.frameLayout(l="ѡ��", bgc=(0.1, 0.2, 0.3))
    pm.columnLayout(adj=1)
    pm.rowLayout(nc=2, cw2=(10, 10), adj=1)
    pm.button("c01sad1", l="���ػ�������", w=150, h=40, bgc=(0.6, 0.5, 0.6), c="baseaaa()")
    pm.button("c01saaad1", l="�����滻����", w=150, h=40, bgc=(0.6, 0.5, 0.6), c="otheraaa()")
    pm.setParent("..")
    
    pm.frameLayout(l="�滻", bgc=(0.3, 0.2, 0.1))
    pm.columnLayout(adj=1)
    pm.rowLayout(nc=1, cw1=(10), adj=1)
    pm.button("c01sad1", l="ִ���滻", w=150, h=40, bgc=(1, 1, 1), c="runaaa()")
    pm.setParent("..")        
    
    pm.frameLayout(l="ɾ��", bgc=(0, 0, 0))
    pm.columnLayout(adj=1)
    pm.rowLayout(nc=1, cw1=(10), adj=1)
    pm.button("c01sad1", l="ɾ��������", w=150, h=40, bgc=(1, 1, 1), c="deleteold()")
    pm.setParent("..")   
    
    pm.frameLayout(l="�ı䳯��", bgc=(0, 0, 0))
    pm.columnLayout(adj=1)
    pm.rowLayout(nc=3, cw3=(10, 10, 10), adj=1)
    pm.button("c0112e1", l="X+90", w=100, h=40, bgc=(0.8, 0, 0), c="xxxa()")
    pm.button("c011122e1", l="Y+90", w=100, h=40, bgc=(0, 0.7, 0), c="yyya()")
    pm.button("c0112e31", l="Z+90", w=100, h=40, bgc=(0, 0, 0.3), c="zzza()")
    pm.setParent("..")

    pm.window(name, e=1, w=2, h=20)
    pm.showWindow(name)

FrameUI()

def baseaaa():
    global Sel_Base
    Sel_Base = pm.ls(sl=1)[0]

def otheraaa():
    global sel_Othery
    global Sel_Base
    sel_Othery = pm.selected()

def runaaa():
    global sel_Othery
    global Sel_Base
    for i in sel_Othery:
        pm.select(i, r=1)
        position  = pm.xform(q=1, ws=1, rp=1)
        pm.select(cl=1)
        pm.select(Sel_Base, r=1)
        pm.duplicate(rr=1)
        pm.move(position[0], position[1], position[2], rpr=1)
        pm.select(cl=1)

def deleteold():
    global sel_Othery
    global Sel_Base
    for i in sel_Othery:  
        pm.select(i, r=1)
        now = pm.ls(sl=1)[0]
        pm.select(now, r=1)
        pm.mel.doDelete()

def xxxa():                  
    sel_mmm = pm.selected()
    for i in sel_mmm:
        pm.select(i, r=1)
        sel_this = pm.ls(sl=1)[0]
        ro_01_x = pm.getAttr(sel_this + ".rotateX")
        pm.setAttr(sel_this + ".rotateX", ro_01_x + 90)
    pm.select(sel_mmm, r=1)

def yyya():  
    sel_mmm = pm.selected()
    for i in sel_mmm:
        pm.select(i, r=1)
        sel_this = pm.ls(sl=1)[0]
        ro_01_y = pm.getAttr(sel_this + ".rotateY")
        pm.setAttr(sel_this + ".rotateY", ro_01_y + 90)
    pm.select(sel_mmm, r=1)

def zzza():  
    sel_mmm = pm.selected()
    for i in sel_mmm:
        pm.select(i, r=1)
        sel_this = pm.ls(sl=1)[0]
        ro_01_z = pm.getAttr(sel_this + ".rotateZ")
        pm.setAttr(sel_this + ".rotateZ", ro_01_z + 90)
    pm.select(sel_mmm, r=1)

