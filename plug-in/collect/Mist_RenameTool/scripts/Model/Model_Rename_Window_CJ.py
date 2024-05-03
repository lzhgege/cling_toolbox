#coding:utf-8
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import Model.Model_Name_Cmd_CJ as Model_Name_Cmd_CJ

import sys
if sys.version_info[0] == 2:
    reload(Model_Name_Cmd_CJ)
elif sys.version_info[0] > 2:
    try:
        import importlib
        importlib.reload(Model_Name_Cmd_CJ)
    except:
        pass


import os
import collections
from PySide2 import QtWidgets
from PySide2 import QtCore
import functools
from PySide2.QtCore import Slot
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

class CustomQComboBox(QtWidgets.QComboBox):
    def wheelEvent(self, *args, **kwargs):
        pass

class ModelRenameWindow_CJ(QtWidgets.QWidget):
    def __init__(self):
        super(ModelRenameWindow_CJ,self).__init__()
        self.modelnamecmd = Model_Name_Cmd_CJ.ModelNameTool_CJ()
        self.winname = 'Model_Rename_Window'
        self.frameLayouts = list()
        self.bigGrp = 'Geometry'
        self.main_layout=QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        if cmds.window(self.winname,q=1,ex=1):
            cmds.deleteUI(self.winname)
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.is_default_delete_empty_group=False
        mel.eval(lockHistoryCmd)

    def set_default_empty_delete(self,value):
        self.is_default_delete_empty_group=value;
    def create_widgets(self):
        self.btn_standard=QtWidgets.QPushButton(u"制作规范")
        self.btn_standard.setStyleSheet("background:blue")
        self.btn_show_or_hidden=QtWidgets.QPushButton()
        self.label_info=QtWidgets.QLabel(u"当前场景组")
        self.label_info.setFixedHeight(15)
        self.btn_show_or_hidden.setText(u"隐藏已整理")
        self.btn_show_or_hidden.setStyleSheet("background:green")
        self.btn_change_name_via_group = QtWidgets.QPushButton(u"根据组名修改物体名")
        self.btn_delete_empty_group=QtWidgets.QPushButton(u"删除空组")
        self.line_edit_custom_grp=QtWidgets.QLineEdit()
        self.line_edit_custom_grp.setPlaceholderText(u"自定义组")
        self.line_edit_custom_grp.setFixedHeight(25)
        self.btn_custom_grp_apply=QtWidgets.QPushButton(u"应用")
        self.btn_custom_grp_apply.setFixedWidth(40)
        self.btn_custom_grp_apply.setFixedHeight(25)
        self.btn_custom_grp_clear=QtWidgets.QPushButton(u"清空输入")
        self.btn_custom_grp_clear.setFixedWidth(60)
        self.btn_custom_grp_clear.setFixedHeight(25)


        self.group_create_modify=QtWidgets.QGroupBox()
        self.group_create_modify.setFixedHeight(80)
        self.group_create_modify.setTitle(u"创建修改组")
        self.btn_create_scence_base=QtWidgets.QPushButton(u"创建场景基础组")
        self.btn_change_scence_base=QtWidgets.QPushButton(u"更改场景基础组")
        self.group_prepare_for_cfx=QtWidgets.QGroupBox()
        self.group_prepare_for_cfx.setFixedHeight(60)
        self.group_prepare_for_cfx.setTitle(u"为CFX作准备")
        self.btn_create_set_for_tool = QtWidgets.QPushButton(u"为道具创建set")
        self.layout_group_prepare_for_cfx=QtWidgets.QVBoxLayout()
        self.layout_group_prepare_for_cfx.addWidget(self.btn_create_set_for_tool)
        self.layout_group_prepare_for_cfx.setSpacing(0)
        self.group_prepare_for_cfx.setLayout(self.layout_group_prepare_for_cfx)
        self.create_combox_buttons()

    def create_layout(self):

        self.layout_group_operate=QtWidgets.QVBoxLayout()
        self.layout_create_scence=QtWidgets.QHBoxLayout()
        self.layout_custom_grp=QtWidgets.QHBoxLayout()
        self.layout_group_operate.addLayout(self.layout_create_scence)
        self.layout_group_operate.addLayout(self.layout_custom_grp)

        self.layout_create_scence.addWidget(self.btn_create_scence_base)
        self.layout_create_scence.addWidget(self.btn_change_scence_base)

        self.layout_custom_grp.addWidget(self.line_edit_custom_grp)
        self.layout_custom_grp.addWidget(self.btn_custom_grp_apply)
        self.layout_custom_grp.addWidget(self.btn_custom_grp_clear)


        self.group_create_modify.setLayout(self.layout_group_operate)
        self.layout_button_other=QtWidgets.QHBoxLayout()
        self.layout_button_other.addWidget(self.btn_show_or_hidden)
        self.layout_button_other.addWidget(self.btn_change_name_via_group)
        self.layout_button_other.addWidget(self.btn_delete_empty_group)

        self.main_layout.addWidget(self.btn_standard)
        self.main_layout.addWidget(self.label_info)
        self.main_layout.addLayout(self.layout_button_other)
        self.main_layout.addWidget(self.group_create_modify)
        self.main_layout.addLayout(self.layout_buttons)
        self.main_layout.addWidget(self.group_prepare_for_cfx)


    def create_connections(self):
        self.btn_standard.clicked.connect(lambda:os.system(u"explorer Z:\Resources\Mist\All\规范\资产场景流程规范".encode("GBK")))
        self.btn_create_scence_base.clicked.connect(self.createBaseGrpCmd)
        self.btn_change_scence_base.clicked.connect(self.changePrefix)
        self.btn_show_or_hidden.clicked.connect(self.btn_show_or_hideden_click)
        self.btn_change_name_via_group.clicked.connect(self.renameChildren)
        self.btn_create_set_for_tool.clicked.connect(self.createSetForPrp)
        self.btn_delete_empty_group.clicked.connect(self.delete_empty_group)
        self.btn_custom_grp_clear.clicked.connect(lambda:self.line_edit_custom_grp.setText(""))
        self.btn_custom_grp_apply.clicked.connect(lambda:self.createCustomGrp(self.line_edit_custom_grp.text(),"GenaralCustom"))
        self.btn_dl_clear.clicked.connect(lambda: self.line_edit_dl.setText(""))
        self.btn_dl_apply.clicked.connect(lambda: self.createCustomGrp(self.line_edit_dl.text(),"DlCustom"))

    def createCustomGrp(self,custom_grp,custom_str):
        if not custom_grp:
            cmds.warning(u"组名不能为空")
            return
        self.butCmd_new(custom_grp,custom_str)

    def clearLayout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())

    def delete_empty_group(self):
        mel.eval("source cleanUpScene.mel")
        mel.eval("deleteEmptyGroups;")

    def btn_show_or_hideden_click(self):
        text=self.btn_show_or_hidden.text()
        if text==u"显示":
            self.set_btn_show_text_and_style(u"隐藏已整理","background:green")
            self.show_or_hide_all(True)
        else:
            self.set_btn_show_text_and_style(u"显示","background:red")
            self.show_or_hide_all(False)

    def set_btn_show_text_and_style(self,text,sheet):
        self.btn_show_or_hidden.setStyleSheet(sheet)
        self.btn_show_or_hidden.setText(text)

    def create_combox_buttons(self):
        butDictList = Model_Name_Cmd_CJ.ModelKindReadTool_CJ.getButDictList(self.modelnamecmd.prefix)
        self.layout_buttons=QtWidgets.QVBoxLayout()
        for butTuple in butDictList:
            self.create_group_buttons(butTuple)

    def add_splite_line(self,layout,is_hline_or_vline=True):
        '''
        添加分割线，可以横向或者纵向
        is_hline_or_vline 横向或者纵向
        layout 要附加的布局
        '''
        self.line = QtWidgets.QFrame()
        if is_hline_or_vline:
            self.line.setFrameShape(QtWidgets.QFrame.HLine)
        else:
            self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(self.line)

    def create_group_buttons(self, butTuple):
        group_title = butTuple[1]
        #创建一个分组，病添加一个栅格布局
        group_box = QtWidgets.QGroupBox()
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(0)
        butDict=butTuple[0]
        group_box.setLayout(grid_layout)
        group_box.setTitle(group_title)
        self.layout_buttons.addWidget(group_box)
        row_index=0#行索引
        coloum_index=0#列索引
        for but in butDict.keys():
            if but.find('separator'):
                grp = butDict[but][0]

                #自定义代理按钮
                if(grp.find("DlCustom")>-1):
                    self.line_edit_dl=QtWidgets.QLineEdit()
                    self.line_edit_dl.setPlaceholderText(u"自定义代理")
                    self.btn_dl_apply=QtWidgets.QPushButton(u"应用")
                    self.btn_dl_clear=QtWidgets.QPushButton(u"清空输入")
                    row_index=row_index+1
                    grid_layout.addWidget(self.line_edit_dl,row_index,0)
                    grid_layout.addWidget(self.btn_dl_apply,row_index,1)
                    grid_layout.addWidget(self.btn_dl_clear,row_index,2)
                    return

                siblingBrothers = butDict[but][2]
                if siblingBrothers:
                    names=[]
                    for i in range(siblingBrothers):
                        name=butDict[but][1] + chr(i + 97)
                        names.append(name)
                    comb_box=self.create_combbox(names,grp)
                    grid_layout.addWidget(comb_box,row_index,coloum_index)
                else:
                    button=QtWidgets.QPushButton(butDict[but][1])
                    button.clicked.connect(lambda: self.butCmd_new(grp))
                    grid_layout.addWidget(button,row_index,coloum_index)

            else:
                pass
            coloum_index = coloum_index + 1
            if(coloum_index==3):
                coloum_index=0
                row_index=row_index+1
        group_box.setFixedHeight(row_index*60)
        
    def create_combbox(self,items,grp):
        comb_box = CustomQComboBox()
        comb_box.addItems(items)
        comb_box.setObjectName(grp)
        comb_box.activated.connect(lambda selected_index:self.butOptionMenuCmd_new(selected_index,comb_box))
        return comb_box

    def changePrefix(self,*argvs):
        #text = cmds.textFieldButtonGrp(self.prefixTextFieldButtonGrp,q = True,text = True)
        objs = cmds.ls(sl = True)
        if objs:
            if cmds.nodeType(objs[0]) == 'transform':                  
                self.modelnamecmd.prefix = objs[0][:-len(self.bigGrp)]
                #cmds.text(self.prefixText,e = True,label = objs[0])
                self.rebuildUI()
                return
        cmds.warning(u'请选择场景基础组')
        #cmds.textFieldButtonGrp(self.prefixTextFieldButtonGrp,e = True,text = '')

    def lockSelectionHistory(self,lock):
        objList = cmds.ls(sl = True)
        for obj in objList:
            mel.eval("lockHistory(\"%s\",%d)"%(obj,lock))

    def rebuildUI(self):
        self.clearLayout(self.main_layout)
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def butOptionMenuCmd_new(self,index,comb_box=None):
        group_text='_ModGrp'
        grp=comb_box.objectName()
        name=comb_box.currentText()
        newGrp = grp.replace(group_text,'_{0}{1}'.format(name[-1],group_text))
        self.butCmd_new(newGrp)

    def butCmd_new(self,grp=None,custom_str=None):
        #取选中的对象
        self.selobj = pm.ls(selection=True)
        if not self.selobj:
            cmds.warning(u"请选择对象后再操作")
            return
        selobj_temp=[]
        if type(self.selobj) is list:
            selobj_temp=self.selobj
        else:
            selobj_temp.append(self.selobj)
        try:
            #不存在组就创建组
            if not cmds.objExists(grp):
                if custom_str:
                    grp=self.modelnamecmd.creatGrps_new(grp,custom_str)
                else:
                    self.modelnamecmd.creatGrps_new()
                self.label_info.setText(u"当前场景组:"+self.modelnamecmd.prefix+self.bigGrp)
            for obj in self.selobj:
                try:
                    #取形状和节点类型判断，如果是mesh和aiStandIn就指定父级为grp
                    if pm.listRelatives(obj, shapes=True) is not None:
                        if self.modelnamecmd.is_mesh_or_aiStandIn(obj):
                            pm.parent(obj, grp)
                except:
                    pass

            self.modelnamecmd.renameChildrenByParentName_new(parent=grp)
            #重命名之后选中，并删除空组
            objs = cmds.listRelatives(grp, children=True)
            remove_objs=[]
            for obj in objs:
                if cmds.listRelatives(obj, shapes=True) is None:
                    objs.remove(obj)
            cmds.select(objs)
        except Exception as result:
            cmds.warning(result.message)
        if self.is_default_delete_empty_group:
            self.delete_empty_group()

    def show_or_hide_all(self, is_show):
        text=u"隐藏"
        if is_show:
            text=u"显示"
        allgrpdict = self.modelnamecmd.baseGrps()
        for grp in allgrpdict.keys():
            if not cmds.objExists(grp):
                continue
            try:
                if is_show :
                    cmds.setAttr(grp+'.v',1)
                else:
                    cmds.setAttr(grp + '.v', 0)
            except Exception as result:
                  cmds.warning(result.message)

    def createBaseGrpCmd(self):
        self.modelnamecmd.prefix = 'CJ_'
        self.modelnamecmd.creatGrps()
        temp_grp=self.bigGrp
        if temp_grp=="Geometry":
            temp_grp="Geometry"
        cmds.select(temp_grp,r = True)
        self.changePrefix()

    def renameChildren(self):
        selobjs = cmds.ls(sl=1)
        if type(selobjs) is list:
            if len(selobjs) > 0:
                for obj in selobjs:
                    if cmds.listRelatives(obj,s=1) is not None:
                        parentgrp = cmds.listRelatives(obj,p=1)
                        if parentgrp is not None:
                            self.modelnamecmd.renameChildrenByParentName(parent=parentgrp)
                    else:
                        if cmds.listRelatives(obj,c=1) is not None:
                            self.modelnamecmd.renameChildrenByParentName(parent=obj)

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

    def delete_empty_group(self):
        mel.eval("source cleanUpScene.mel")
        mel.eval("deleteEmptyGroups;")
        n = 0
        while True:
            n += 1
            deleteList = []
            transforms = cmds.ls(type='transform')
            if transforms:
                for tran in transforms:
                    if cmds.nodeType(tran) == 'transform':
                        children = cmds.listRelatives(tran, c=True)
                        if children == None:
                            deleteList.append(tran)
            if not deleteList:
                break
            else:
                cmds.delete(deleteList)
                if n > 10:
                    break
