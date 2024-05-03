# -*- coding: utf-8 -*-
from modelAssetInspectUI.common import utils

import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya
import logging

import listBaseWidget
import tableBaseWidget
import treeBaseWidget
import frameBaseWidget

import modelAssetInspectUI.common.utils_fun_dict as utils_fun_dict
from modelAssetInspectUI.model.checkBase import getIntermediateObjectDatas
import modelAssetInspectUI.model.loggingBase as loggingBase
import documentConfigWidget

import processWidget
import functools



import sys
if sys.version_info[0] == 2:
    reload(frameBaseWidget)
    reload(documentConfigWidget)
    reload(loggingBase)
    reload(listBaseWidget)
    reload(tableBaseWidget)
    reload(utils_fun_dict)
    reload(processWidget)
    reload(treeBaseWidget)
elif sys.version_info[0] > 2:
    import importlib
    importlib.reload(frameBaseWidget)
    importlib.reload(documentConfigWidget)
    importlib.reload(loggingBase)
    importlib.reload(listBaseWidget)
    importlib.reload(tableBaseWidget)
    importlib.reload(utils_fun_dict)
    importlib.reload(processWidget)
    importlib.reload(treeBaseWidget)





import webbrowser
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

MESSAGE_TITLE = u'警告'
MESSAGE_STRING = u'选择的物体中,有ref或其它情况！\n请自行处理！'

NOT_CHECKED = u"未检查"
EXISTING_STRING = u"存在物体"

COMPLETE_INSPECTION_MESSAGE = u"重新检查完成！"

SHAPES_LABEL_NAME = u"检查transform下面是否有多个shape"


class BackBaseWidget(QWidget):

    def __init__(self, name, parent=None, win_type="list"):
        super(BackBaseWidget, self).__init__(parent)
        self.name = name
        self.document_configs=documentConfigWidget.DocumentConfigWidget.genarate_configs()
        self.setObjectName(self.name+"widget")

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        self.logger.handlers = list()
        loggingBase.setLoggingConsole(self.logger)
        
        self.processWidget = processWidget.ProcessWidget(self)
        self.processWidget.setWindowTitle(self.name)
        self.processWidget.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        button_name = u"(0个){}".format(self.name)
        self.button = frameBaseWidget.BaseButton(button_name, self)
        self.widget = QWidget(self)

        self.widget_layout = QVBoxLayout()
        self.widget_layout.setContentsMargins(5, 0, 5, 0)
        self.widget_layout.setSpacing(2)
        self.widget.setLayout(self.widget_layout)

        winFun = None
        
        if win_type == "list":
            winFun = listBaseWidget.ListBaseWidget
        
        if win_type == "table":
            winFun = tableBaseWidget.TableBaseWidget
            
        if win_type == "tree":
            winFun = treeBaseWidget.TreeBaseWidget
            
        self.dataWidget = winFun(self.widget)
        repairLayout = QHBoxLayout(self)
        repairLayout.setContentsMargins(0, 0, 0, 0)

        self.documentButton = QPushButton(u"文档")
        if self.name in self.document_configs.keys() and self.document_configs[self.name]:
            repairLayout.addWidget(self.documentButton)

        self.againButton = QPushButton(u"重新检查")
        repairLayout.addWidget(self.againButton)

        self.repairButton = QPushButton(u"修复")
        repairLayout.addWidget(self.repairButton)

        self.widget_layout.addWidget(self.dataWidget)
        self.widget_layout.addLayout(repairLayout)

        layout.addWidget(self.button)
        layout.addWidget(self.widget)

        self.show_value = True
        self.initState()

    def initState(self):
        self.button.clicked.connect(self.showHiedWidget)
        self.button.clicked.emit()
        self.button.setButtonIocn()
        self.againButton.clicked.connect(self.againCheck)
        self.documentButton.clicked.connect(self.openDocument)

    def showHiedWidget(self):
        value = self.widget.isHidden()
        self.set_show_or_hide(value)
        if not self.show_value:
            self.dataWidget.hide()
    def set_show_or_hide(self,value):
        if value:
            self.widget.show()
        else:
            self.widget.hide()

    def setData(self, datas):
        new_datas = []
        if isinstance(datas, list):
            num = len(datas)
            if self.name in utils_fun_dict.NOT_DATA_WIDGET:
                button_name = u"({}){}".format(EXISTING_STRING, self.name)
                self.button.setText(button_name)
            else:
                button_name = u"({}个){}".format(num, self.name)
                self.button.setText(button_name)
                
            self.dataWidget.setData(datas)

            if self.name == SHAPES_LABEL_NAME:
                data = getIntermediateObjectDatas(datas)
                self.dataWidget.setItemStyle(data)
            if num > 0 and (self.name in utils.CHECK_DICT_HAS_DATA_GREEN):
                self.button.setColor("green")
            elif num > 0 and (self.name in utils.CHECK_DICT_HAS_DATA_YELLOW):
                # self.button.setStyleSheet("color: #292421")
                self.button.setColor("yellow")
                # self.button.setStyleSheet("QPushButton{color: #292421;}")
            elif num > 0 and (self.name in utils.CHECK_DICT_HAS_DATA_BLUE):
                self.button.setColor("blue")
            elif num == 0:
                self.button.setColor("green")
            else:
                self.button.setColor("red")

    def removeRepair(self):
        self.widget_layout.removeWidget(self.repairButton)

    def connectFun(self, fun, up_widget=True):
        self.repairButton.clicked.connect(functools.partial(self.runFun, fun, up_widget))

    def clear(self):
        button_name = u"(0个){}".format(self.name)
        self.button.setText(button_name)
        self.dataWidget.clearData()
        self.button.setColor("default")

    def runFun(self, fun, up_widget=True):
        if isinstance(self.dataWidget, tableBaseWidget.TableBaseWidget):
            win = fun(self.dataWidget)
            self._setSubWindow(win)
            return

        # if self.name == u"是否有五边面":
        #     win = fun(self.dataWidget)
        #     self._setSubWindow(win)
        #     return
        
        datas = self.dataWidget.getSelectItemDatas()
        if datas and self.name not in [u"检查重名", u"空间名", u"是否有多余的材质"]:
            print(fun.__name__)
            removeData = fun(datas)

            if self.name == SHAPES_LABEL_NAME:
                self.dataWidget.setItemStyle(removeData)
                return

            print(removeData,datas)
            if len(removeData) != len(datas):
                QMessageBox.warning(self, MESSAGE_TITLE, MESSAGE_STRING, QMessageBox.Yes, QMessageBox.Yes)

            if up_widget and isinstance(self.dataWidget, listBaseWidget.ListBaseWidget):
                if self.name in [u"动画层", u"是否含有renderSetup信息"]:
                    fun = utils_fun_dict.CHECK_FUN_DICT[self.name][1]
                    values = fun(self.callbackFun)
                    self.setData(values)
                else:
                    self.dataWidget.removeSelectItems(removeData)
                    button_name = u"({}个){}".format(self.dataWidget.itemCount(), self.name)
                    self.button.setText(button_name)
                    if len(self.dataWidget.getData()) == 0:
                        self.button.setColor("green")
        else:
            fun(datas)

    def _setSubWindow(self, widget):
        '''
        设置子集窗口
        :param widget:
        :return:
        '''
        widget.setWindowFlags(Qt.Window)
        desktop = QApplication.desktop().screenGeometry()
        width = ((desktop.width() - widget.width()) / 2)
        height = ((desktop.height() - widget.height()) / 2)
        widget.move(QPoint(width, height))
        widget.show()

    def openDocument(self):
        """打开文档
        """  
        url=self.document_configs[self.name].encode("gbk")
        webbrowser.open(url)    

    def againCheck(self):
        '''
        重新检查
        :return:
        '''
        #loggingBase.setLoggingFileName(self.logger)

        self.processWidget.reset()
        self.processWidget.show()

        fun = utils_fun_dict.CHECK_FUN_DICT[self.name][1]
        values = fun(self.callbackFun)
        if not self.processWidget.state:
            return

        self.setData(values)
        # if values:
        #     self.logger.info(u"{}(检查-未通过)".format(self.name))
        # else:
        #     self.logger.info(u"{}(检查-通过)".format(self.name))

        self.processWidget.hide()
        OpenMaya.MGlobal.displayInfo(COMPLETE_INSPECTION_MESSAGE)
        
    def callbackFun(self, text=None, num=0):
        '''
        重新检查时,实时刷新<检查提示UI>给进度提示,可以强制退出检查
        :param text: str,
        :param num:
        :return:
        '''
        if not self.processWidget.state:
            return False

        QApplication.processEvents()
        self.processWidget.setNumObject(num)
        if text:
            self.processWidget.setText(text)
        self.processWidget.add()
        return True
    
    def setRepairName(self, text):
        '''
        设置修复的控件的名字
        如果值是None就把控件删除
        :param text: str,
        :return:
        '''
        if text:
            self.repairButton.setText(text)
        if text is None:
            self.repairButton.setParent(None)
            del self.repairButton

    def setNotChecked(self):
        '''
        设置widget是没有检查的状态
        :return:
        '''
        button_name = u"({}){}".format(NOT_CHECKED, self.name)
        self.button.setText(button_name)
        self.dataWidget.clearData()
        self.button.setColor("default")
    
    def hideDataWidget(self):
        self.show_value = False
        self.dataWidget.hide()


if __name__ == "__main__":
    tsetWin = BackBaseWidget(u"测试")
    tsetWin.show()
    tsetWin.setData(['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5', 'Item 6', 'Item 7', 'Item 8', 'Item 9'])