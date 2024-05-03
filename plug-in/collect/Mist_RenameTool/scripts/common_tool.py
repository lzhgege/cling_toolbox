# coding:utf-8
import maya.cmds as cmds
# import pymel.core as pm
import maya.mel as mel
import collections
from PySide2 import QtWidgets
from PySide2 import QtCore
import functools
import re
import os,sys

toolpath = os.path.dirname(__file__).replace("\\","/")


lockHistoryCmd = '''
/***
   get object name via string
*/
global proc string getName(string $str){
    string $buffer[];
    $numTokens = `tokenize $str "." $buffer`;
    return $buffer[0];
}

/***
    lock or unlock a object
    name:object name
    lock:lock 1，unlock 0
*/
global proc lockHistory(string $name,int $lock){
    //get history log
    string $history[] = `listHistory -future 1 -allFuture $name`;
    string $obj;
    for ($obj in $history){
            lockNode -lock 0 $obj;
    }
    for ($obj in $history){
        //get connect node
        string $connection[] = `listConnections -connections 1 -plugs 1 $obj`;
        string $con;
        for($con in $connection){
            string $conObj = getName($con);
            int $conObjLock = 0;
            //if object lock,unlock
            int $conObjAreLock[] = `lockNode -q -lock $conObj`;
            $conObjLock = $conObjAreLock[0];
            if($conObjLock){
                lockNode -lock 0 $conObj;
            }
            int $isLock = `getAttr -lock $con`;
            if($isLock == !$lock){
                setAttr -lock $lock $con;
            }
            //lock back
            if($conObjLock){
                lockNode -lock 1 $conObj;
            }
        }   
    }
    if($lock){
        for ($obj in $history){
                lockNode -lock 1 $obj;
        }
        print ($name + "lock history successfully\\n");
    }else{
        print ($name + "unlock history successfully\\n");
    }
}
'''
class CommonTool(QtWidgets.QWidget):
    def __init__(self):
        super(CommonTool,self).__init__()
        self.main_layout=QtWidgets.QVBoxLayout(self)
        self.forAniGrp = 'forANI'
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        mel.eval(lockHistoryCmd)
    def is_default_delete_empty(self):
        return self.cb_delete_empty.isChecked()

    def connect_check(self,func):
        self.cb_delete_empty.clicked.connect(func)

    def create_widgets(self):
        self.btn_replace_str = QtWidgets.QPushButton(u"前后缀字符替换")
        self.cb_delete_empty = QtWidgets.QCheckBox(u"勾选后涉及创建组操作会自动删除空组")
        self.cb_delete_empty.setChecked(True)

        self.btn_change_name_via_group = QtWidgets.QPushButton(u"根据组名修改物体名")
        self.btn_lock_selected_history = QtWidgets.QPushButton(u"锁定所选择的历史")
        self.btn_lock_selected_history.setStyleSheet("background:red")
        self.btn_unlock_selected_history = QtWidgets.QPushButton(u"解锁所选择的历史")
        self.btn_unlock_selected_history.setStyleSheet("background:green")
        self.btn_shape_node_check = QtWidgets.QPushButton(u"shape节点检查")


    def create_layout(self):
        self.layout_delete_empty=QtWidgets.QVBoxLayout()
        self.layout_delete_empty.addWidget(self.cb_delete_empty)

        self.layout_replace_and_other=QtWidgets.QGridLayout()
        self.layout_replace_and_other.addWidget(self.btn_lock_selected_history,0,0)
        self.layout_replace_and_other.addWidget(self.btn_unlock_selected_history,0,1)
        self.layout_replace_and_other.addWidget(self.btn_replace_str,1,0)
        self.layout_replace_and_other.addWidget(self.btn_shape_node_check,1,1)

        self.main_layout.addLayout(self.layout_delete_empty)
        self.main_layout.addLayout(self.layout_replace_and_other)

    def create_connections(self):
        self.btn_lock_selected_history.clicked.connect(lambda: self.lockSelectionHistory(True))
        self.btn_unlock_selected_history.clicked.connect(lambda: self.lockSelectionHistory(False))
        self.btn_replace_str.clicked.connect(lambda:CommonTool.evalScriptFile(u"{}/Other/renameObject.mel".format(toolpath).encode('utf-8')))
        self.btn_shape_node_check.clicked.connect(self.shadeNodeCheck)

    def delete_empty_group(self):
        mel.eval("source cleanUpScene.mel")
        mel.eval("deleteEmptyGroups;")


    def lockSelectionHistory(self, lock):
        objList = cmds.ls(sl=True)
        for obj in objList:
            mel.eval("lockHistory(\"%s\",%d)" % (obj, lock))


    def addEyesToForAniGrp(self,*argvs):
        self.addToForAniGrp('Eye_L_001_mo')
        self.addToForAniGrp('Eye_R_001_mo')

    def addBrowToForAniGrp(self,*argvs):
        self.addToForAniGrp('Brow_L_001_mo')
        self.addToForAniGrp('Brow_R_001_mo')

    def createSetForChr(*args):
        if cmds.objExists("sim__grp__"):
            child_sets = cmds.listConnections("sim__grp__" + ".dnSetMembers", s=1, d=0)
            [cmds.delete(i) for i in child_sets]

        geo = None
        if cmds.objExists("Hair_Grp"):
            geo = cmds.sets("Cloth_Grp", "Hair_Grp", name="Geo_Grp")
        else:
            geo = cmds.sets("Cloth_Grp", name="Geo_Grp")
        geo_low = cmds.sets("NoRender_Grp", name="Geo_Low_Grp")
        cmds.sets(geo, geo_low, name="sim__grp__")

    def createSetForPrp(*args):
        if cmds.objExists("sim__grp__"):
            child_sets = cmds.listConnections("sim__grp__" + ".dnSetMembers", s=1, d=0)
            [cmds.delete(i) for i in child_sets]
        geom = cmds.sets("Geometry", name="prp_grp")
        if cmds.objExists("NoRender_Grp"):
            no_render = cmds.sets("NoRender_Grp", name="no_render")
            cmds.sets(geom, no_render, name="sim__grp__")
        else:
            cmds.sets(geom, name="sim__grp__")
    def shadeNodeCheck(self):
        '''shape节点检查，根据shape节点检查.mel脚本更改'''
        meshs=cmds.ls(type='mesh')
        for each in meshs:
            if re.search("Orig",str(each)):
                continue
            child=cmds.listRelatives(each,parent=True,type='transform')[0]
            cmds.rename(each,child+"Shape")
        print(u"shape节点检查重命名完毕")

    @staticmethod
    def evalScriptFile(filePath):
        script_str = "source \"{0}\"".format(filePath)
        #path=os.path.abspath(script_str).encode("utf-8").replace("\\","/")
        mel.eval(script_str)



