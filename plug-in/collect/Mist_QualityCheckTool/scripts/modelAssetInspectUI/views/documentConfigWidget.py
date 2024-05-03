# -*- coding: utf-8 -*-
import os
from PySide2 import QtWidgets
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import maya.OpenMayaUI as omui
import urllib
import modelAssetInspectUI.common.utils_fun_dict as utils_fun_dict
import modelAssetInspectUI.common.util_helper as util_helper
import sys
if sys.version_info[0] == 2:
    reload(utils_fun_dict)
    reload(util_helper)
elif sys.version_info[0] > 2:
    import importlib
    importlib.reload(utils_fun_dict)  
    importlib.reload(util_helper) 


import webbrowser
import sys
from shiboken2 import wrapInstance
def getMayaWin():
    ptr = omui.MQtUtil.mainWindow()
    try:
        mayaWin = wrapInstance(long(ptr), QtWidgets.QWidget)
    except:
        mayaWin = wrapInstance(int(ptr), QtWidgets.QWidget)
    return mayaWin
class DocumentConfigItem(QWidget):
    urlChanged=Signal(str,str)
    def __init__(self,title,url):
        super(DocumentConfigItem,self).__init__()
        self._title=title
        self._url=url
        self.create_widgets()
        self.create_layouts() 
        self.create_connections()

    def create_widgets(self):
        self.lb_title=QLabel(self._title)
        self.le_document_url=QLineEdit(self._url)
        self.pb_paste=QPushButton(u"重置")
        self.pb_test_open=QPushButton(u"测试跳转")
        

    def create_layouts(self):
        self.main_layout=QHBoxLayout(self)
        self.main_layout.addWidget(self.lb_title)
        self.main_layout.addWidget(self.le_document_url)
        self.main_layout.addWidget(self.pb_paste)
        self.main_layout.addWidget(self.pb_test_open)
        self.main_layout.setStretch(0,9)
        self.main_layout.setStretch(1,9)
        self.main_layout.setStretch(2,2)
        self.main_layout.setStretch(2,2)

    def create_connections(self):
        self.pb_paste.clicked.connect(lambda:self.le_document_url.setText(""))
        self.pb_test_open.clicked.connect(lambda:DocumentConfigItem.open_url(self.le_document_url.text()))
        self.le_document_url.textChanged[str].connect(lambda text:self.urlChanged.emit(self._title,text))


    @staticmethod
    def open_url(url):
        webbrowser.open(url.encode("gbk"))

class DocumentConfigWidget(QDialog):
    JSON_PATH=os.path.join(os.path.dirname(__file__),"document_configs.json")
    JSON_HELPER=util_helper.UtilJsonHelper(JSON_PATH)
    CONFIG_KEY="configs"
    def __init__(self, parent=getMayaWin()):
        super(DocumentConfigWidget,self).__init__(parent)
        self.checkes=utils_fun_dict.CHECK_FUN_DICT.keys()
        self.json_configs=DocumentConfigWidget.genarate_configs()
        self.setGeometry(1920/2-600,100,self.width(),self.height())
        self.setWindowTitle(u"配置质检文档")
        self.setMinimumWidth(700)
        self.setMinimumHeight(900)
        self.create_widgets()
        self.create_layouts()
        self.load_checks()

    def create_widgets(self):
        self.lv_checks=QListWidget()

    def create_layouts(self):
        self.main_layout=QHBoxLayout(self)
        self.main_layout.addWidget(self.lv_checks)

    def create_connections(self):
        self.lv_checks.itemChanged
        
    def load_checks(self):
        """载入配置项
        """        
        for config in self.json_configs.keys():
            url=self.json_configs[config]
            self.create_check_item(config,url)

    def create_check_item(self,title,url):
        """创建列表组件
        """        
        item=QListWidgetItem()
        item.setSizeHint(QSize(20, 40))
        item.setFlags(item.flags() & Qt.ItemIsSelectable)
        check_item=DocumentConfigItem(title,url)
        check_item.urlChanged.connect(lambda t,u:self.change_url(t,u))
        self.lv_checks.addItem(item)
        self.lv_checks.setItemWidget(item,check_item)

    def change_url(self,title,url):
        """改变组件的url，自动保存
        """        
        self.json_configs[title]=url
        json_data=DocumentConfigWidget.JSON_HELPER.load_json()
        json_data[DocumentConfigWidget.CONFIG_KEY]=self.json_configs
        DocumentConfigWidget.JSON_HELPER.write_json(json_data)



    @staticmethod
    def genarate_configs():
        """生成配置字典
        """        
        result=dict()
        json_data=DocumentConfigWidget.JSON_HELPER.load_json()
        for key in utils_fun_dict.CHECK_FUN_DICT.keys():
            if DocumentConfigWidget.CONFIG_KEY in json_data.keys():
                configs=json_data[DocumentConfigWidget.CONFIG_KEY]
                if key in configs.keys():
                    url=configs[key]
                    result[key]=url
        return result
