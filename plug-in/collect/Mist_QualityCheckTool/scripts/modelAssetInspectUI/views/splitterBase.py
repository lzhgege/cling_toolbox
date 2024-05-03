# -*- coding: utf-8 -*-
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class SplitterHandleBase(QSplitterHandle):
    moveed = Signal(int)

    def __init__(self, orientation, parent):
        super(SplitterHandleBase, self).__init__(orientation, parent)
        self.old_y = None

    def mousePressEvent(self, evnet):
        QSplitterHandle.mousePressEvent(self, evnet)
        self.old_y = evnet.y()

    def mouseMoveEvent(self, evnet):
        QSplitterHandle.mouseMoveEvent(self, evnet)
        new_y = evnet.y()
        value = new_y - self.old_y
        print(value)
        self.moveed.emit(value)


class SplitterBase(QSplitter):

    def __init__(self, orientation,  parent=None):
        super(SplitterBase, self).__init__(orientation, parent)

    def createHandle(self):
        splitter = SplitterHandleBase(Qt.Vertical, self)
        return splitter


if __name__ == "__main__":
    tsetWin = SplitterBase()
    tsetWin.show()
