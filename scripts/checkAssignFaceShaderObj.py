# -*- coding:utf-8 -*-
import maya.cmds as cm
import os
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import re
import checkAssignFaceShader
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

def getMayaWin():
    ptr = omui.MQtUtil.mainWindow()
    mayaWin = wrapInstance(long(ptr), QWidget)
    return mayaWin

def isBad(obj):
    u'''
    是否按面给材质的物体
    '''
    shapeList = cm.listRelatives(obj,s = True,pa = True,ni = True)
    #print(shapeList)
    if shapeList:
    
        instGrps = cm.getAttr('%s.instObjGroups'%shapeList[0])
        if instGrps:
            for i in range(len(instGrps)):
                objGrps = cm.getAttr('%s.instObjGroups[%d].objectGroups'%(shapeList[0],i),mi = True)
                if objGrps:
                    for j in range(len(objGrps)):
                        sgList = cm.listConnections('%s.instObjGroups[%d].objectGroups[%d]'%(shapeList[0],i,j),s = False,type = 'shadingEngine')
                        connectionList = cm.listConnections('%s.instObjGroups[%d].objectGroups[%d]'%(shapeList[0],i,j),s = False,type = 'shadingEngine',connections = True,plugs = True)

                        if sgList:
                            for i in range(0,len(connectionList),2):
                                
                                compList = cm.getAttr('%s.objectGrpCompList'%connectionList[i])
                                if compList:
                                    for comp in compList:
                                        if re.match('f\[(\d+):(\d+)\]|f\[(\d+)\]',comp):
                                            return True
        return False
    else:
        return False


def getAssignFaceShaderObjList(objList): 
    okList = list()
    badList = list()

    for obj in objList:
        
        if isBad(obj):
            badList.append(obj)
            # print(u'%s 是按面给材质的物体，不合规范！'%obj)
        else:
            okList.append(obj)
            # print(u'%s 符合规范！'%obj)

    # print(u'按面给材质，不符合规范：')
    # for bad in badList:
    #     print(bad)

    # print('')

    # print(u'符合规范：')
    # for ok in okList:
    #     print(ok)

    return badList


def getAssignFaceShaderObjListWhereCanFix(objList):
    badList = list()

    for obj in objList:
        
        objFaceShaderType = checkAssignFaceShader.getFaceShaderType(obj)
        if objFaceShaderType == 1:
            badList.append(obj)

    return badList



def getAssignFaceShaderObjListFromSelected():
    objList = cm.ls(sl = True)
    return getAssignFaceShaderObjList(objList)


def getAssignFaceShaderObjListFromAll():
    u'''
    获取所有按面给材质的物体名字
    '''
    objList = list()
    allMesh = cm.ls(type = 'mesh',ni = True)
    for mesh in allMesh:
        transformList = cm.listRelatives(mesh,p = True,pa = True,type = 'transform')
        if transformList:
            objList.append(transformList[0])
    return getAssignFaceShaderObjList(objList)


def getAssignFaceShaderObjListFromAllWhereCanFix():
    u'''
    获取所有按面给材质但可以修复的物体名字
    '''
    objList = list()
    allMesh = cm.ls(type = 'mesh',ni = True)
    for mesh in allMesh:
        transformList = cm.listRelatives(mesh,p = True,pa = True,type = 'transform')
        if transformList:
            objList.append(transformList[0])
    return getAssignFaceShaderObjListWhereCanFix(objList)

class objListView(QListView):
    def __init__(self,parent = None):
        QListView.__init__(self,parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.clicked.connect(self.selectObj)

    def selectObj(self,index):
        objList = list()
        row = index.row()
        item = self.model().item(row)
        obj = item.text()
        endStr = u'(不可修复)'
        if obj.endswith(endStr):
            strCount = len(obj)
            endStrCount = len(endStr)
            obj = obj[:strCount - endStrCount]
        objList.append(obj)
        if objList:
            cm.select(objList,r = True)

        # print('selectionChanged')    
        

def getRealSgFromFaceShaderObj(obj):
    u'''    
    此函数获取全部面给一个sg的那个sg，没有返回none。只适合于按面给材质这种检测。
    (如果按面给材质，但是全部面是一个sg，那就说明可以给这个物体材质而不是按面给)
    '''
    faceCount = cm.polyEvaluate(obj,f = True)
    meshList = cm.listRelatives(obj,s = True,pa = True,ni = True)
    if meshList:
        mesh = meshList[0]
        faceSgList = cm.listConnections('%s.instObjGroups[0].objectGroups'%mesh,s = False,type = 'shadingEngine')
        sgConnectionList = cm.listConnections('%s.instObjGroups[0].objectGroups'%mesh,s = False,type = 'shadingEngine',connections = True,plugs = True)
        # sgIndexList = cm.getAttr('%s.instObjGroups[0].objectGroups'%mesh,mi = True)
        faceSgCountDict = dict()
        # print(faceSgList)
        # print(sgConnectionList)
        # return None
        if not faceSgList or not sgConnectionList:
            return None
        for faceSg in faceSgList:
            faceSgCountDict[faceSg] = 0
        
        if len(faceSgList) * 2 == len(sgConnectionList):
            # return
        
            for i in range(len(faceSgList)):
                sgConnection = sgConnectionList[2 * i]
                sgFaceStrList = cm.getAttr('%s.objectGrpCompList'%sgConnection)
                sgFaceCount = 0
                # print(sgFaceStrList)
                #如果objectGrpCompList为空，这个也是其中一个情况
                if not sgFaceStrList:
                    return faceSgList[i]
                #如果objectGrpCompList的面数量为物体面数，这个也是其中一个情况
                for s in sgFaceStrList:
                    #print(s)
                    matchObj = re.match('f\[(\d+):(\d+)\]|f\[(\d+)\]',s)
                    if matchObj:
                        #print(matchObj.groups())
                        #print(matchObj.group(1))
                        #print(int(matchObj.group[1]))
                        if not matchObj.group(3):
                            sgFaceCount += (int(matchObj.group(2)) - int(matchObj.group(1)) + 1)
                        else:
                            sgFaceCount += 1
                faceSgCountDict[faceSgList[i]] += sgFaceCount
                if faceSgCountDict[faceSgList[i]] == faceCount:
                    return faceSgList[i]
    return None
    
def replaceSg(obj,sg):
    u'''
    断开obj的mesh(非中间物)的sg连接，赋予obj这个sg
    '''
    meshList = cm.listRelatives(obj,s = True,pa = True,ni = True)
    if meshList:
        mesh = meshList[0]
        
        connectionList = cm.listConnections(mesh,s = False,type = 'shadingEngine',connections = True,plugs = True)
        for i in range(0,len(connectionList),2):
            cm.disconnectAttr(connectionList[i],connectionList[i + 1])
        cm.sets(obj,e = True,forceElement = sg)
        #print(connectionList)

def fixFaceShaderObj(obj):
    sg = getRealSgFromFaceShaderObj(obj)
    if sg:
        replaceSg(obj,sg)
        
def fixAllFaceShaderObj():
    faceShaderObjList = getAssignFaceShaderObjListFromAllWhereCanFix()
    if faceShaderObjList:
        for faceShaderObj in faceShaderObjList:
            fixFaceShaderObj(faceShaderObj)
    cm.confirmDialog( title=u'信息', message=u'修复完毕！\n再检查一次看看！', button=[u'好滴'], defaultButton=u'好滴', dismissString='No' )

class objShaderIsBadWin(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        self.setWindowTitle(u'按面给材质模型检测及修复')

        layout = QGridLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.setRowStretch(0,1)
        self.setLayout(layout)

        self.badListView = objListView(self)
        self.badListView.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.badListView.hide()
        model = QStandardItemModel(self.badListView)
        # model.appendRow(QStandardItem('dfsaf'))
        # self.model = model
        self.badListView.setModel(model)

        tipLabel = QLabel(u'',self)
        tipLabel.setFixedHeight(30)
        self.tipLabel = tipLabel

        doitBtn = QPushButton(u'列出所有按面给材质的模型',self)
        doitBtn.clicked.connect(self.checkShaderIsBad)
        doitBtn.setFixedHeight(30)

        fixBtn = QPushButton(u'修复场景内  所有面给一个材质球  的模型',self)
        fixBtn.clicked.connect(fixAllFaceShaderObj)
        fixBtn.setFixedHeight(30)


        trashBtn = QPushButton(self)
        trashBtn.setFixedSize(20,20)
        trashBtn.clicked.connect(self.clear)
        iconPath = os.path.join(os.path.dirname(__file__),'trash.png').replace('\\','/')
        try:
            iconPathUnicode = iconPath.decode('gbk')
        except:
            iconPathUnicode = iconPath.decode('utf-8')

        trashBtn.setIcon(QIcon(iconPathUnicode))

        layout.addWidget(doitBtn,0,0,1,5)
        layout.addWidget(tipLabel,1,0,1,4)
        layout.addWidget(trashBtn,1,4,1,1)
        layout.addWidget(self.badListView,2,0,1,5)
        layout.addWidget(fixBtn,3,0,1,5)

        self.resize(300,300)

        self.setStyleSheet(u'''
            *{
                font-size:11px;
                font-family:"Microsoft YaHei";
            }
        ''')


    def checkShaderIsBad(self):
        # if not self.badListView.isVisible():
        #     self.badListView.show()
        canFixList,badList = checkAssignFaceShader.getAssignFaceShaderTypeListFromAll()

        #listView
        rowCount = self.badListView.model().rowCount()
        for i in range(rowCount):
            self.badListView.model().removeRow(0)
        #self.badListView.clear()
        # model = QStandardItemModel(self.badListView)
        # model = self.model
        model = self.badListView.model()
        for canFix in canFixList:
            model.appendRow(QStandardItem(canFix))
        for bad in badList:
            model.appendRow(QStandardItem(bad + u'(不可修复)'))
        # self.badListView.setModel(model)
        #self.badListView.model()
        
        #tipLabel
        if len(canFixList) + len(badList):
            self.tipLabel.setText(u'检查完毕。以下物体按面给材质，不符合规范：')
        else:
            self.tipLabel.setText(u'检查完毕，没有问题！')

    def clear(self):
        rowCount = self.badListView.model().rowCount()
        for i in range(rowCount):
            self.badListView.model().removeRow(0)
        self.tipLabel.setText('')


    def closeEvent(self,event):
        event.accept()
        self.deleteLater()

def objShaderIsBadUI():
    winName = 'objShaderIsBadWin'
    if cm.window(winName,q = True,exists = True):
        cm.deleteUI(winName)
    win = objShaderIsBadWin(getMayaWin())
    win.setWindowFlags(Qt.Window)
    win.setObjectName(winName)
    # win.resize(300,200)
    win.show()


if __name__ == '__main__':
    checkAssignFaceShaderObj.objShaderIsBadUI()