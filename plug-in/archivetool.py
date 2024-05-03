# -*- coding: utf-8 -*-

from PySide2 import QtCore
import maya
from maya.app.general import zipScene
import maya.OpenMayaUI as omui
import zlib
import zipfile
import maya.cmds as cmds
import os, sys
from os import path
import io
import shutil
import json
from shiboken2 import wrapInstance
import webbrowser


# sync api
lib_path = 'Z:/Scripts/Mist/Mist_Alembic_Plugins/lib'
if not lib_path in sys.path:
    sys.path.append(lib_path)
try:
    import ly_globals
    reload(ly_globals)
    MayaVersion = cmds.about(v=True)
    ly_globals.sync_api('maya', MayaVersion)
except Exception as e:
    raise Exception('Globals Initialize Error') 

import ly_maya_lib as mayalib
reload(mayalib)    





from PySide2.QtWidgets import QCheckBox, QFileDialog, QGroupBox, QHBoxLayout, QLineEdit, QMessageBox, QPushButton,QDialog,QLabel,QProgressBar, QVBoxLayout,QWidget
def getMayaWin():
    ptr = omui.MQtUtil.mainWindow()
    mayaWin = wrapInstance(long(ptr), QWidget)
    return mayaWin

class JsonHelper:
    def __init__(self):
       self.path=r"C:\Users\{}\Documents\maya\eatoolboxsettings\achivetool.json".format(os.environ["username"])
    def load_json(self):
        """[载入json]

        Args:
            file_name ([str]): [路径文件名]

        Returns:
            [str]: [json文本]
        """        
        if not os.path.exists(self.path):
            return None
        with io.open(self.path,'r',encoding='utf-8') as f:
            return json.load(f)

    def write_json(self,json_obj):
        """[写入json]

        Args:
            json_obj ([str]): [json_str文本]
            file_name ([str]): [文件名]
        """        
        with io.open(self.path,'w',encoding='utf-8') as f:
            f.write(unicode(json.dumps(json_obj,ensure_ascii=False,indent=4)))

class MistArchiveTool(QDialog):
    def __init__(self,parent=getMayaWin()):
        super(MistArchiveTool,self).__init__(parent)
        self._target_dir=None
        self._directory_key="directory"
        self._external_key="external"
        self.setWindowTitle(u"迷雾_制片归档工具")
        self.json_helper=JsonHelper()
        self.setWindowFlags(QtCore.Qt.Window)
        self.setMinimumWidth(700)
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.load_configs()
        
        
    def create_widgets(self):
        self.widget_open_dir=QWidget()
        self.widget_progress=QWidget()
        self.lb_set_dir=QLabel(u"指定或粘贴文件路径:")
        self.lb_notice=QLabel()
        self.lb_progress=QLabel(u"进度")
        self.le_dir=QLineEdit()
        self.progress=QProgressBar()
        self.progress.setMaximumHeight(15)
        self.pb_open_dir=QPushButton(u"指定文件夹")
        self.pb_document=QPushButton(u"文档")
        self.pb_start_collection=QPushButton(u"开始归档")
        self.cb_external=QCheckBox(u"zip")

    def create_layout(self):
        self.layout_open_dir=QHBoxLayout(self.widget_open_dir)
        self.layout_open_dir.addWidget(self.lb_set_dir)
        self.layout_open_dir.addWidget(self.le_dir)
        self.layout_open_dir.addWidget(self.pb_open_dir)
        self.layout_open_dir.addWidget(self.pb_document)

        self.layout_progress=QHBoxLayout(self.widget_progress)
        self.layout_progress.addWidget(self.lb_progress)
        self.layout_progress.addWidget(self.progress)
        self.layout_progress.addWidget(self.cb_external)
        self.layout_progress.addWidget(self.pb_start_collection)


        self.main_layout=QVBoxLayout(self)
        self.main_layout.addWidget(self.widget_open_dir)
        self.main_layout.addWidget(self.widget_progress)

    def create_connections(self):
        self.pb_open_dir.clicked.connect(self.open_dir)
        self.pb_start_collection.clicked.connect(self.archive)
        self.le_dir.textChanged.connect(self.dir_change)
        self.cb_external.stateChanged.connect(self.set_configs)
        self.pb_document.clicked.connect(self.open_document)

    def start_collection(self):
        self.progress.setValue(0)
        if not self._target_dir:
            QMessageBox.warning(self,"警告","请设置归档的目标文件夹",QMessageBox.Yes)
            return
        files=self.zipScene(self.cb_external.isChecked())
        self.progress.setRange(0,len(files))
        self.copy2(files,lambda value:self.progress.setValue(value))

    def archive(self):
        current_file = cmds.file(q=True, sceneName=True)
        # If the scene has not been saved
        if not current_file:
            QMessageBox.warning(self,u"警告","场景没保存!归档之前必须保存")
            return   
        elif not os.path.isfile(current_file):
            msg = u'归档失败，找不到场景文件 {}'.format(fileName)
            QMessageBox.warning(self,u"警告",msg)
            return
        
        
        mayalib.archive(current_file, self.le_dir.text(), is_zip=self.cb_external.isChecked(), callback=self.progress_callback)

    def progress_callback(self, i, capacity):
        self.progress.setRange(0, capacity)
        self.progress.setValue(i)
        
    def open_document(self):
        webbrowser.open("http://wiki.4wgame.com/pages/viewpage.action?pageId=27363615")

    def open_dir(self):
        self._target_dir=QFileDialog.getExistingDirectory(self,u"选择一个文件夹")
        self.le_dir.setText(self._target_dir)  

    def get_scene_shortname(self):
        shortname=cmds.file(q=True,sceneName=True,shortName=True)
        name,ext=shortname.split(".")
        return name

    def replafe_path(self,path):
        return path.replace("/","\\")

    def copy2(self,files,progress_func):
        target_path=path.join(self._target_dir,self.get_scene_shortname())
        target_path=self.replafe_path(target_path)
        file_index=1
        for file in files:
            dirname,file_name=path.split(file)
            dirname=self.replafe_path(dirname)
            sub=dirname.split(":\\")[1]
            target_file_path=path.join(target_path,sub)
            if not path.exists(target_file_path):
                os.makedirs(target_file_path)
            target_file=path.join(target_file_path,file_name)
            shutil.copy(file,target_file)
            progress_func(file_index)
            file_index=file_index+1
        QMessageBox.information(self,"提示","归档完毕",QMessageBox.Yes)
        os.startfile(self._target_dir.encode("gbk"))

    def zipScene(self,archiveUnloadedReferences):
        fileName = cmds.file(q=True, sceneName=True)
        # If the scene has not been saved
        if (fileName==""):
            QMessageBox.warning(self,u"警告","场景没保存!归档之前必须保存")
            return    

        # If the scene has been created, saved and then erased from the disk 
        elif (cmds.file(q=True, exists=True)==0):
            msg = u'归档失败，找不到场景文件 {}'.format(fileName)
            QMessageBox.warning(self,u"警告",msg)
            return
        
        # If the scene has been modified    
        elif (cmds.file(q=True, anyModified=True)==1):
                    
                    if(cmds.about(batch=True)):
                            # batch mode, save the scene automatically.
                            cmds.warning( maya.stringTable['y_zipScene.kSavingSceneBeforeArchiving' ] )
                            cmds.file(force=True, save=True)

        # get the default character encoding of the system
        theLocale = cmds.about(codeset=True)

        # get a list of all the files associated with the scene
        files = cmds.file(query=1, list=1, withoutCopyNumber=1)
             
        # If user choose to archive unloaded reference files, then find all referenced files of the current scene. 
        # For any unloaded reference, load them first, get file list that should be archived and then restore its unloaded status.
        if( archiveUnloadedReferences == True):
            # refNodes = cmds.ls(type='reference')
            refNodes = []
            for each in cmds.file(q=True, r=True):
                resolve = cmds.file(each, q=True, rfn=True)
                if resolve and cmds.objExists(resolve):
                    refNodes.append(resolve)
                
            isLoadOldList = []
            for refNode in refNodes:
                if(refNode.find('sharedReferenceNode') == -1 and refNode != '_UNKNOWN_REF_NODE_'):
                    isLoadOld = cmds.referenceQuery(refNode, isLoaded=True)
                    isLoadOldList.append(isLoadOld)
                    # Load the unloaded reference
                    if(isLoadOld == False):
                        cmds.file(loadReference=refNode, loadReferenceDepth = 'all')
                    # Get all external files related to this reference
                    filesOfThisRef = cmds.file(query=1, list=1, withoutCopyNumber=1)
                    for fileOfThisRef in filesOfThisRef:
                        files.append(fileOfThisRef)
                    # Unload the reference that are unloaded at the beginning
                    if(isLoadOld == False):
                        cmds.file(unloadReference=refNode)    
            # remove the possible duplicated file names
            files = set(files)
            files = list(files)  
        return files  
    def dir_change(self):
        self._target_dir=self.le_dir.text()
        self.set_configs()

    def set_configs(self):
        json_data=dict()
        json_data[self._directory_key]=self.le_dir.text()
        json_data[self._external_key]=self.cb_external.isChecked()
        self.json_helper.write_json(json_data)

    def load_configs(self):
        json_data=self.json_helper.load_json()
        if not json_data:
            return
        if self._directory_key in json_data.keys():
            text=json_data[self._directory_key]
            self._target_dir=text
            self.le_dir.setText(text)
        if self._external_key in json_data.keys():
            self.cb_external.setChecked(json_data[self._external_key])
        else:
            self.cb_external.setChecked(True)

try:
    mist_archivetool.close()
    mist_archivetool.deleteLater()
except:
    pass
mist_archivetool = MistArchiveTool()
mist_archivetool.show()