# -*- coding: utf-8 -*-
from maya import OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

try:
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from shiboken import wrapInstance


class ProcessBase(QWidget):

    state = True

    def getMayaWindow(self, widget):
        parent = widget.parent()
        if parent:
            if parent.objectName() == "MayaWindow":
                return widget
            else:
                return self.getMayaWindow(parent)
        else:
            return None

    def getTopParent(self):
        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        try:
            rootWidget = wrapInstance(long(mayaMainWindowPtr), QWidget)
        except:
            rootWidget = wrapInstance(int(mayaMainWindowPtr), QWidget)
        
        childrens = rootWidget.children()

        widget = self.parent()
        if widget and widget.objectName() != "MayaWindow":
            mayaTopWidget = self.getMayaWindow(widget)
            if mayaTopWidget in childrens:
                geometry = mayaTopWidget.geometry()
                width = geometry.x() + geometry.width()/2 - self.width()/2
                height = geometry.y() + geometry.height()/2 - self.height()
                return width, height

    def closeEvent(self, event):
        self.state = False
        QWidget.closeEvent(self, event)

    def showEvent(self, event):
        self.state = True
        value = self.getTopParent()
        if value:
            self.move(value[0], value[1])
        QWidget.showEvent(self, event)


if __name__ == "__main__":
    tsetWin = ProcessBase()
    tsetWin.show()
