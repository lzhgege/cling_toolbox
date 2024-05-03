# -*- coding: utf-8 -*-
import pymel.core as pm
import os

def switchProxyLevel(proxyLevel):
    sel = pm.ls(selection=True)
    for obj in sel:
        proxyShapes = obj.listRelatives(type="aiStandIn")
        if not proxyShapes:
            pm.warning(u"物体 {} 没有 Arnold Standin 代理.".format(obj))
            continue
        proxyAttr = proxyShapes[0].dso.get()
        if not proxyAttr.endswith(("_H.ass", "_M.ass", "_L.ass", "_N.ass", "_E.ass", "_D.ass", "_S.ass")):
            pm.warning(u"物体 {} 的代理文件不符合命名规范.".format(obj))
            continue

        proxyDir = os.path.dirname(proxyAttr)
        proxyName = os.path.basename(proxyAttr)
        newProxyName = (proxyName.replace("_H.ass", "_{}.ass".format(proxyLevel[0]))
                .replace("_M.ass", "_{}.ass".format(proxyLevel[0]))
                .replace("_L.ass", "_{}.ass".format(proxyLevel[0]))
                .replace("_N.ass", "_{}.ass".format(proxyLevel[0]))
                .replace("_E.ass", "_{}.ass".format(proxyLevel[0]))
                .replace("_D.ass", "_{}.ass".format(proxyLevel[0]))
                .replace("_S.ass", "_{}.ass".format(proxyLevel[0])))

        newProxyAttr = os.path.join(proxyDir, newProxyName)

        if not os.path.exists(newProxyAttr):
            pm.warning(u"物体 {} 的 {} 级别代理文件不存在.".format(obj, proxyLevel))
            continue

        proxyShapes[0].dso.set(newProxyAttr)
        pm.warning(u"成功切换 {} 的代理为 {} 级别.".format(obj, proxyLevel))

def createWindow():
    windowID = "proxySwitcherWindow"
    if pm.window(windowID, exists=True):
        pm.deleteUI(windowID)
        
    pm.window(windowID, title=u"代理切换器", sizeable=True )
    
    pm.columnLayout(adjustableColumn=True)
    
    pm.text(label=u"选择所需修改代理")
    
    highButton = pm.button(label="High", command=lambda *args: switchProxyLevel("High"))
    mediumButton = pm.button(label="Medium", command=lambda *args: switchProxyLevel("Medium"))
    lowButton = pm.button(label="Low", command=lambda *args: switchProxyLevel("Low"))
    ningjie = pm.button(label=u"凝结版", command=lambda *args: switchProxyLevel("N"))
    emission = pm.button(label=u"自发光版", command=lambda *args: switchProxyLevel("E"))
    simaa = pm.button(label=u"无灯笼版", command=lambda *args: switchProxyLevel("D"))
    sha = pm.button(label=u"沙", command=lambda *args: switchProxyLevel("S"))
    
    
    pm.setParent("..")
    
    pm.showWindow(windowID)
    
createWindow()
