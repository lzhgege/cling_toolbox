# -*- coding: utf-8 -*-
import processBase
# reload(processBase)

try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class ProcessBaseWidget(processBase.ProcessBase):

    def __init__(self, parent=None):
        super(ProcessBaseWidget, self).__init__(parent)

        self.numObject = None
        self.numItem = None
        self.items = list()
        self.progress = 0
        self.proportion = 100.0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        checkLayout = QHBoxLayout(self)
        checkLayout.setContentsMargins(0, 0, 0, 0)

        checkName = QLabel(u"正在检查项：", self)
        self.checkItem = QLineEdit(self)
        self.checkItem.setReadOnly(True)
        self.checkItem.setStyleSheet("QLineEdit{border: none;"
                                     "background-color:#444444;}")

        checkLayout.addStretch()
        checkLayout.addWidget(checkName)
        checkLayout.addWidget(self.checkItem)
        checkLayout.addStretch()

        checkItmeLayout = QHBoxLayout(self)
        checkItmeLayout.setContentsMargins(0, 0, 0, 0)

        checkNameItem = QLabel(u"在检查物体：",self)
        self.checkObjectItem = QLineEdit(self)
        self.checkObjectItem.setReadOnly(True)
        self.checkObjectItem.setStyleSheet("QLineEdit{border: none;"
                                           "background-color:#444444;}")

        checkItmeLayout.addStretch()
        checkItmeLayout.addWidget(checkNameItem)
        checkItmeLayout.addWidget(self.checkObjectItem)
        checkItmeLayout.addStretch()

        self.processBar = QProgressBar(self)

        layout.addLayout(checkLayout)
        layout.addLayout(checkItmeLayout)
        layout.addWidget(self.processBar)

        self.initState()

        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle(u"检查中:")

    def initState(self):
        self.setMaximumHeight(58)

    def setText(self, text):
        self.checkItem.setText(text)
        
    def text(self):
        return self.checkItem.text()

    def setObjectText(self, text):
        self.checkObjectItem.setText(text)

    def setValue(self, value):
        self.processBar.setValue(value)

    def reset(self):
        self.processBar.reset()
        self.checkItem.clear()
        self.checkObjectItem.clear()
        self.progress = 0
        self.proportion = 100.0
        self.numObject = 0

    def value(self):
        return self.processBar.value()

    def setNumObject(self, value):
        self.numObject = value

    def setItems(self, items):
        self.items = items
        self.numItem = len(items)

        if u"是否cv点有数据" in self.items:
            self.proportion = self.proportion - 25.0
            self.numItem = self.numItem - 1
        if u"shape信息" in self.items:
            self.proportion = self.proportion - 25.0
            self.numItem = self.numItem - 1
        if u"是否有五边面" in self.items:
            self.proportion = self.proportion - 25.0
            self.numItem = self.numItem - 1

        if self.numItem == 0:
            self.numItem = 1
        
    def add(self):
        progress = self.getProgress()
        self.progress = self.progress + progress
        self.setValue(self.progress)

    def getPercentage(self):
        return self.proportion/self.numItem

    def getProgress(self):
        text = self.text()
        percentage = self.getPercentage()
        if text in [u"是否cv点有数据", u"shape信息", u"是否有五边面"]:
            percentage = 25.0
        if self.numItem == len(self.items) == 1:
            percentage = 100.0

        if self.numObject == 0:
            self.numObject = 1
        progress = percentage/self.numObject
        return progress


if __name__ == "__main__":
    tsetWin = ProcessBaseWidget()
    tsetWin.show()
