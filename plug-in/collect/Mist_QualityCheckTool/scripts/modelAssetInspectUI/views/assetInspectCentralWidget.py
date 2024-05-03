# -*- coding: utf-8 -*-
import os
import modelAssetInspectUI.views.straightFrameBaseWidget as straightFrameBaseWidget
import modelAssetInspectUI.common.utils as utils
# reload(utils)
# reload(straightFrameBaseWidget)
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class AssetInspectCentralWidget(QWidget):
    def __init__(self, parent=None):
        super(AssetInspectCentralWidget, self).__init__(parent)
        self.base_widgets=dict()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self.widget_type_list = list()

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("QScrollArea{border:none}")
        layout.addWidget(self.scrollArea)

        scrollWidget = QWidget(self)
        self.scrollArea.setWidget(scrollWidget)

        self.scrolllayout = QVBoxLayout(self)
        self.scrolllayout.setContentsMargins(0, 3, 3, 3)
        self.scrolllayout.setSpacing(2)
        scrollWidget.setLayout(self.scrolllayout)

        settingRunLayout = QVBoxLayout(self)
        settingRunLayout.setContentsMargins(3, 3, 3, 3)
        layout.addLayout(settingRunLayout)

        self.setting = QCheckBox(u"全选/全不选", self)
        self.run = QPushButton(u"开始检查", self)

        settingRunLayout.addWidget(self.setting)
        settingRunLayout.addWidget(self.run)

        self.initState()

    def initState(self):
        self.setting.setChecked(True)
        self.setting.clicked.connect(self.setSettingChecked)
        # self.run.clicked.connect(self.runChecked)

    def setSettingChecked(self):
        value = self.setting.isChecked()
        for widget in self.widget_type_list:
            widget.setChecked(value)

    def runChecked(self):
        check_items = list()
        for widget in self.widget_type_list:
            if widget.isHidden():
                continue
            items = widget.getCheckItems()
            if items:
                check_items.extend(items)
        # if check_items:
        #     for i in check_items:
        #         print i.objectName()

        return check_items
    
    def getAllItems(self):
        all_items = list()
        for widget in self.widget_type_list:
            items = widget.getItmes()
            all_items.extend(items)
            
        return all_items


    def load_modules(self,module_list):
        #清空所有的质检项目
        widgets_count=self.scrolllayout.count()
        for widget in self.widget_type_list:
            self.scrolllayout.removeWidget(widget)
            widget.setHidden(True)
            

        module_dict=utils.CHECK_DICT
        module_dict_zh=utils.CHECK_DICT_ZH
        color=0
        for module in module_list:
            base_widget=self.get_widget(module)
            if not base_widget:
                name=module_dict_zh[module]
                base_widget = straightFrameBaseWidget.StraightFrameBaseWidget(name, self)
                base_widget.setColor(color)
                base_widget.setObjectName(module)
                if color==0:
                    color=1
                else:
                    color=0
                type_list = module_dict[module]
                base_widget.addItmes(type_list)
                self.widget_type_list.append(base_widget)

            base_widget.setHidden(False)
            base_widget.setChecked(True)
            self.set_module(base_widget)
            
            self.scrolllayout.addWidget(base_widget)

    def get_widget(self,object_name):
        result=None
        for i in self.widget_type_list:
            if object_name==i.objectName():
                result=i
        return result


    def set_module(self,basewidget):
        if basewidget.objectName()=="Mesh":
            #basewidget.setItmeColor(u"是否有五边面", "#760000")
            basewidget.setItmeColor(u"shape信息", "#B60000")
            basewidget.setItmeColor(u"模型渲染属性是否正常", "#FFD700")
            # basewidget.setItmeColor(u"是否cv点有数据", "#B60000")
            # basewidget.setTtemChecked(u"是否有五边面", False)
            # basewidget.setTtemChecked(u"shape信息", False)
            #basewidget.setTtemChecked(u"是否cv点有数据", False)
        #黄色
        basewidget.setItmeColor(u"变态属性", "#FFD700")
        basewidget.setItmeColor(u"多shape结构", "#FFD700")
        basewidget.setItmeColor(u"渲染模型参数异常", "#FFD700")
        basewidget.setItmeColor(u"非渲染模型参数异常", "#FFD700")
        #蓝色
        basewidget.setItmeColor(u"以下模型设置不影响渲染", "#0080FF")
        basewidget.setItmeColor(u"检查材质文件多余绑定节点", "#0080FF")
        basewidget.setItmeColor(u"Opaque 没有开启", "#0080FF")
        #绿色
        basewidget.setItmeColor(u"shape信息", "#2E8B57")

if __name__ == "__main__":
    tsetWin = AssetInspectCentralWidget()
    tsetWin.show()