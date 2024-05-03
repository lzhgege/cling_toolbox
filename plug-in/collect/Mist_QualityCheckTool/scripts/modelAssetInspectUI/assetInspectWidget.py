# -*- coding: utf-8 -*-
import os
import sys
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import functools
from modelAssetInspectUI.views import assetInspectCentralWidget

try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *
from modelAssetInspectUI.common import utils
from modelAssetInspectUI.common import util_helper

if sys.version_info[0] == 2:
    reload(assetInspectCentralWidget)
    reload(utils)
    reload(util_helper)
elif sys.version_info[0] > 2:
    try: 
        import importlib
        importlib.reload(assetInspectCentralWidget)
        importlib.reload(utils)
        importlib.reload(util_helper)
    except:
        pass



MODULE_CHECKS_KEY="module_checks"
class AssetInspectWidget(MayaQWidgetDockableMixin, QWidget):
    def __init__(self, parent=None):
        super(AssetInspectWidget, self).__init__(parent)
        json_path=r"C:\Users\{}\Documents\maya\eatoolboxsettings\checktool.json".format(os.environ["username"])
        self.json_helper=util_helper.UtilJsonHelper(json_path)
        self.is_load_checks=False
        self.setWindowTitle(u"质检工具20230627")
        self.setObjectName("AssetInspectWidget")
        self.button_list=[]
        self.create_widget()
        self.create_layout()
        self.set_checks_data()


    def create_widget(self):
        self.group_checks=self.gen_checks()
        self.dockingFrame = QMainWindow(self)
        self.dockingFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.dockingFrame.setWindowFlags(Qt.Widget)
        self.dockingFrame.setDockOptions(QMainWindow.AnimatedDocks)

        self.centralWidget = assetInspectCentralWidget.AssetInspectCentralWidget()
        self.dockingFrame.setCentralWidget(self.centralWidget)

    def create_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.group_checks)
        layout.addWidget(self.dockingFrame, 0)
        self.setLayout(layout)

    def gen_checks(self):
        """生成勾选模块
        """        
        group=QGroupBox(u"模块选择")
        layout=QHBoxLayout(group)
        checks_dicts=utils.CHECK_DICT_ZH
        
        for check in checks_dicts:
            button=QPushButton(checks_dicts[check])
            button.setObjectName(check)
            button.setStyleSheet("background-color:rgb(0,0,0,0)")
            button.clicked.connect(functools.partial(self.checkes_changed,button))
            self.button_list.append(button)
            layout.addWidget(button)
        return group

    def set_checks_data(self):
        json_data=self.json_helper.load_json()
        if not json_data:
            return
        checks_data=json_data[MODULE_CHECKS_KEY]
        if not checks_data:
            return
        for button in self.button_list:
            objectname=button.objectName()
            if objectname in checks_data:
                button.setStyleSheet("background-color:rgb(0,0,0,255)")
        self.centralWidget.load_modules(checks_data)
        pass

    def checkes_changed(self, widget):
        self.set_button_bgc(widget)
        checked_list=[]
        for button in self.button_list:
            if self.get_button_state(button):
                checked_list.append(button.objectName())
        self.centralWidget.load_modules(checked_list)
        json_data=dict()
        json_data[MODULE_CHECKS_KEY]=checked_list
        self.json_helper.write_json(json_data)
        pass

    def set_button_bgc(self, widget):
        style = widget.styleSheet()
        if style == "background-color:rgb(0,0,0,0)":
            widget.setStyleSheet("background-color:rgb(0,0,0,255)")
        elif style == "background-color:rgb(0,0,0,255)":
            widget.setStyleSheet("background-color:rgb(0,0,0,0)")
        pass

    def get_button_state(self, widget):
        style = widget.styleSheet()
        if style == "background-color:rgb(0,0,0,0)":
            return False
        elif style == "background-color:rgb(0,0,0,255)":
            return True
        return None
        

if __name__ == "__main__":
    tsetWin = AssetInspectWidget()
    tsetWin.show()