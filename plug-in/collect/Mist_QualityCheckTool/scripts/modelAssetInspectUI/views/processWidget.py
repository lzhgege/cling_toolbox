# -*- coding: utf-8 -*-
import modelAssetInspectUI.views.processBase as processBase
# reload(processBase)

try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class ProcessWidget(processBase.ProcessBase):

    def __init__(self, parent=None):
        super(ProcessWidget, self).__init__(parent)

        self.numObject = None
        self.progress = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        checkLayout = QHBoxLayout(self)
        checkLayout.setContentsMargins(0, 0, 0, 0)

        checkName = QLabel(u"正在检查物体：", self)
        self.checkItem = QLineEdit(self)
        self.checkItem.setReadOnly(True)
        self.checkItem.setStyleSheet("QLineEdit{border: none;"
                                     "background-color:#444444;}")

        checkLayout.addStretch()
        checkLayout.addWidget(checkName)
        checkLayout.addWidget(self.checkItem)
        checkLayout.addStretch()

        self.processBar = QProgressBar(self)

        layout.addLayout(checkLayout)
        layout.addWidget(self.processBar)

        self.initState()

        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.WindowModal)

    def initState(self):
        self.setMaximumHeight(42)

    def setText(self, text):
        self.checkItem.setText(text)
        
    def setValue(self, value):
        self.processBar.setValue(value)

    def reset(self):
        self.processBar.reset()
        self.checkItem.clear()
        self.progress = 0

        self.numObject = 0

    def value(self):
        return self.processBar.value()

    def setNumObject(self, value):
        self.numObject = value
        
    def add(self):
        progress = self.getProgress()
        self.progress = self.progress + progress
        self.setValue(self.progress)

    def getProgress(self):
        value = self.numObject
        if self.numObject == 0:
            value = 1
        return 100.0/value


if __name__ == "__main__":
    tsetWin = ProcessWidget()
    tsetWin.show()
