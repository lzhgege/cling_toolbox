# -*- coding: utf-8 -*-
import sys
import functools
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

import modelAssetInspectUI.views.treeBaseWidget as treeBaseWidget
import modelAssetInspectUI.views.processWidget as processWidget
import modelAssetInspectUI.views.treeBaseWidget as treeBaseWidget

import modelAssetInspectUI.model.checkBase as checkBase

if sys.version_info[0] == 2:
    reload(checkBase)
elif sys.version_info[0] == 3:
    import importlib
    importlib.reload(checkBase)    


# reload(processWidget)
# reload(treeBaseWidget)
# reload(checkBase)
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class DetailedbackBaseWidget(QWidget):

    def __init__(self, data=None, parent=None):
        super(DetailedbackBaseWidget, self).__init__(parent)
        self.name = u'详细检查'
        self.setWindowTitle(self.name)
        self.data = data
        
        self.processWidget = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self.dataWidget = treeBaseWidget.TreeBaseWidget(self)
        self.againButton = QPushButton(u"重新检查")
        self.againAllButton = QPushButton(u"重新检查场景")

        layout.addWidget(self.dataWidget)
        layout.addWidget(self.againButton)
        layout.addWidget(self.againAllButton)

        self.initState()

    def initState(self):
        self.againButton.clicked.connect(self.againCheck)
        self.againAllButton.clicked.connect(self.againALLCheck)

    def againALLCheck(self):
        self.againCheck(True)

    def againCheck(self, isAll=False):
        '''
        重新检查
        :return:
        '''
        self.processWidget = processWidget.ProcessWidget(self)
        self.processWidget.setWindowTitle(u"详细检查中")
        self.processWidget.show()

        datas = self.data

        if isAll:
            datas = None

        values = checkBase.getCheckDetailedMeshFiveSides(datas=datas, fun=self.callbackFun)
        if not self.processWidget.state:
            return

        self.dataWidget.setData(values)
        if isAll:
            self.data = datas

        self.processWidget.close()
        OpenMaya.MGlobal.displayInfo(u"重新检查完成！")
        
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


if __name__ == "__main__":
    tsetWin = DetailedbackBaseWidget()
    tsetWin.show()
