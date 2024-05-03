# -*- coding: utf-8 -*-
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from shiboken2 import wrapInstance
import sys
import os
import maya.OpenMayaUI as omui

def replace_path(path):
    return path.replace('\\', '/')
def sys_append_path(path):
    path=replace_path(path)
    if path not in sys.path:
        sys.path.append(path)
import os
import os.path as opath
import webbrowser
file_dir_path,file_name = opath.split(__file__.replace('\\', '/'))
path_scripts = file_dir_path + '/scripts'
# sys_append_path(path_scripts)
sys.path.insert(0,path_scripts)   # 放到第一个避免跟gpucache 内config冲突

from Model import  Model_Rename_Window_CJ
import Model.Model_Rename_Window_CJ as Model_Rename_Window_CJ

sys.path.append(file_dir_path)
import common_tool
import config
import qcombocheckbox
import json_helper
#reload(qcombocheckbox)


if sys.version_info[0] == 2:
    reload(common_tool)
    reload(config)
    reload(Model_Rename_Window_CJ)
    reload(json_helper)
elif sys.version_info[0] > 2:
    try:
        import importlib
        importlib.reload(common_tool)
        importlib.reload(config)
        importlib.reload(Model_Rename_Window_CJ)
        importlib.reload(json_helper)
    except:
        pass


def getMayaWin():
    ptr = omui.MQtUtil.mainWindow()
    try:
        mayaWin = wrapInstance(long(ptr), QtWidgets.QWidget)
    except:
        mayaWin = wrapInstance(int(ptr), QtWidgets.QWidget)
    return mayaWin


from qcombocheckbox import QComboCheckBox
CJ_NAME=u"模型场景"



class DesignerUI(QtWidgets.QDialog):
    def __init__(self,parent=getMayaWin()):
        super(DesignerUI, self).__init__(parent)
        self.setObjectName("Mist_RenameTool")
        self.json_helper=json_helper.JsonHelper()
        self.json_config_path= r"C:\Users\{}\Documents\maya\misttoolboxsetting\{}.json".format(os.getenv("username"),self.objectName())
        # self.setWindowTitle(u"{0}".format(file_name.replace(".py","")))
        self.setWindowTitle(u"迷雾-命名工具")
        self.setWindowFlags(self.windowFlags()^QtCore.Qt.WindowContextHelpButtonHint)
        self.setGeometry(1920-400,0,0,0)
        self.setFixedHeight(650)
        self.setFixedWidth(350)
        self.setWindowIcon(QtGui.QIcon(self.get_logo_path()))
        self.create_widgets()
        self.set_qcomboxcheck()
        self.create_layout()
        self.create_connections()
        self.load_selected_config()
        self.setGeometry(1920-500,100,self.width(),self.height())


    def get_logo_path(self):
        path=opath.dirname(opath.dirname(file_dir_path))
        return opath.join(path,"tools_images","mist_tool_logo.png")

    def create_widgets(self):
        self.qcombox=QComboCheckBox()
        self.document=QtWidgets.QPushButton(u"工具帮助文档")
        self.cj_rename=Model_Rename_Window_CJ.ModelRenameWindow_CJ()
        self.common_tool=common_tool.CommonTool()
        self.tabs=QtWidgets.QTabWidget()


    def create_layout(self):
        self.main_layout=QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.qcombox)
        self.main_layout.addWidget(self.document)
        self.main_layout.addWidget(self.tabs)
        self.set_default_empty_delete(self.common_tool.is_default_delete_empty())

    def create_connections(self):
        self.tabs.currentChanged.connect(self.tabs_current_changed)
        self.common_tool.connect_check(self.tool_default_delete_group_check)
        self.qcombox.hidepopup_signal.connect(self.hidepopup)
        self.document.clicked.connect(self.open_document)

    def tool_default_delete_group_check(self):
        """默认删除空组
        """        
        self.set_default_empty_delete(self.common_tool.is_default_delete_empty())

    def set_default_empty_delete(self,value):
        """默认删除空组
        """        
        self.cj_rename.set_default_empty_delete(value)

    def hidepopup(self):
        """面板选择隐藏弹出
        """        
        self.tabs.clear()
        self.load_tabs(self.get_selected_names())
        self.save_selected_config()
        

    def get_selected_names(self):
        """取面板选择的名字
        """        
        names=[i.text() for i in self.qcombox.get_selected()]
        if self.qcombox.is_all():
            indexs=[x for x in range(0,self.qcombox.count())]
            names=self.qcombox.get_texts(indexs)
        return names

    def load_tabs(self,names=None):
        """载入选项卡
        """        
        tabs=QtWidgets.QTabWidget()
        if not names or CJ_NAME in names:
            self.tabs.addTab(self.cj_rename,CJ_NAME)

    def tabs_current_changed(self):
        """当前选项卡改变
        """        
        text=self.tabs.tabText(self.tabs.currentIndex())
        if text==CJ_NAME:
            self.setFixedWidth(380)
            self.setFixedHeight(800)


    def load_selected_config(self):
        """载入选中的配置
        """
        json_data=self.json_helper.load_json(self.json_config_path)
        if not json_data:
            self.load_tabs()
            return

        key=config.ConfigKey.PANEL_SELECT 
        if key in json_data.keys():
            data=json_data[key]
            if not data:
                self.load_tabs()
                return
            names=data.split("|")
            for name in names:
                self.qcombox.select_text(name)
            self.load_tabs(names)

    def save_selected_config(self):
        """保存选择的配置
        """        
        dir_path=os.path.dirname(self.json_config_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        path=os.path.join(dir_path,self.json_config_path)
        list_str="|".join(self.get_selected_names())
        json_data={
            config.ConfigKey.PANEL_SELECT:list_str
        }
        self.json_helper.write_json(self.json_config_path, json_data)

    def set_qcomboxcheck(self):
        """设置面板选项的勾选
        """        
        items=[CJ_NAME]
        self.qcombox.addItems(items)

    def open_document(self):
        text=self.tabs.tabText(self.tabs.currentIndex())
        url=u"http://wiki.4wgame.com/pages/viewpage.action?pageId=27363539#heading-"+text
        webbrowser.open(url.encode("gbk"))
try:
    designer_ui.close()
    designer_ui.deleteLater()
except:
    pass
designer_ui = DesignerUI()
designer_ui.show()

