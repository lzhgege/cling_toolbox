# -*- coding: utf-8 -*-
import os
import feedbackBaseWidget
import splitterBase
import processBaseWidget
import modelAssetInspectUI.common.utils as utils


import sys
if sys.version_info[0] == 2:
    reload(processBaseWidget)
    reload(feedbackBaseWidget)
    reload(splitterBase)
    reload(utils)
elif sys.version_info[0] > 2:
    import importlib
    importlib.reload(processBaseWidget)
    importlib.reload(feedbackBaseWidget)
    importlib.reload(splitterBase)
    importlib.reload(utils)


try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class InspectFeedbackCentralWidget(QWidget):

    def __init__(self, parent=None):
        super(InspectFeedbackCentralWidget, self).__init__(parent)
        self.expand_all=True
        self.back_widgets = list()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self.processWidget = processBaseWidget.ProcessBaseWidget(self)
        self.processWidget.hide()
        # layout.addWidget(self.processWidget)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("QScrollArea{border:none}")
        layout.addWidget(self.scrollArea)

        scrollWidget = QWidget(self)
        self.scrollArea.setWidget(scrollWidget)

        self.scrolllayout = QVBoxLayout(self)
        self.scrolllayout.setContentsMargins(3, 3, 3, 3)
        self.scrolllayout.setSpacing(2)
        scrollWidget.setLayout(self.scrolllayout)

        self.scrolllayout.addStretch()

    def getBackWidget(self, name):
        itme = None
        for widget in self.back_widgets:
            if widget.objectName() == name + "widget":
                itme = widget
                break
        return itme

    def addBackWidget(self, 
                      name, 
                      data=None, 
                      fun=None, 
                      up_widget=True,
                      win_type="list",
                      repair_text=None):
        if not self.getBackWidget(name):
            index = len(self.back_widgets)
            widget = feedbackBaseWidget.BackBaseWidget(name, self, win_type)
            widget.setRepairName(repair_text)
            self.scrolllayout.insertWidget(index, widget)
            self.back_widgets.append(widget)
            widget.setData(data)
            if fun:
                widget.connectFun(fun, up_widget)

    def set_widgets_show_or_hide(self):
        if self.back_widgets:
            for widget in self.back_widgets:
                widget.set_show_or_hide(self.expand_all)
        self.expand_all=not self.expand_all

    def removeBackWidget(self, name):
        if self.getBackWidget(name):
            widget = self.getBackWidget(name)
            widget.setParent(None)
            self.scrolllayout.removeWidget(widget)
            self.back_widgets.remove(widget)
            del widget

    def clear(self):
        num = len(self.back_widgets)
        for i in range(num):
            widget = self.back_widgets[-1]
            widget.setParent(None)
            self.scrolllayout.removeWidget(widget)
            self.back_widgets.remove(widget)
            del widget
    
    def showProcess(self):
        self.processWidget.reset()
        self.processWidget.show()
        self.scrollArea.hide()
        
    def showInspect(self):
        self.processWidget.close()
        self.scrollArea.show()


if __name__ == "__main__":
    tsetWin = InspectFeedbackCentralWidget()
    tsetWin.show()