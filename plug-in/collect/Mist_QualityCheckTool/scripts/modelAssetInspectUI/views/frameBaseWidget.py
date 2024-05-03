# -*- coding: utf-8 -*-
import os
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

app_path = os.path.dirname(os.path.dirname(__file__))
# images_path = os.path.join(app_path.decode("gbk"), 'images')
images_path = os.path.join(app_path, 'images')


class BaseButton(QPushButton):

    COLOR_DICT = {"default": ["#5d5d5d","#FFFFFF", "#707070", "#111111", "#4b4b4b"],
                  "red": ["#5d0000","#FFFFFF", "#700000", "#111111", "#4b4b4b"],
                  "green": ["#2E8B57","#FFFFFF" ,"#385E0F", "#111111", "#4b4b4b"],
                  "yellow":["#FFD700","#292421","#FF9912","#111111", "#4b4b4b"],
                  "blue":["#3D59AB","#FFFFFF","#191970","#111111", "#4b4b4b"]}

    def __init__(self, name, parent=None):
        super(BaseButton, self).__init__(name, parent=parent)
        self.iocn_type = 1

        font = QFont()
        font.setFamily(u'微软雅黑')
        font.setBold(True)
        self.setFont(font)

        icon = QIcon(os.path.join(images_path, "arrow_down2.png"))
        self.setIcon(icon)
        self.setIconSize(QSize(20, 20))

        self.setColor()

        self.setMinimumHeight(22)
        self.setMaximumHeight(22)

    def setColor(self, color="default"):

        style = "QPushButton{{text-align:left;" \
                "background-color:{};spacing:5px;color:{};}}" \
                "QPushButton:hover{{background-color:{};}}" \
                "QPushButton:pressed{{background-color:{};}}" \
                "QPushButton:disabled{{background-color:{};}}".format(*self.COLOR_DICT[color])
        self.setStyleSheet(style)

    def enterEvent(self, event):
        QPushButton.enterEvent(self, event)
        if self.iocn_type:
            icon = QIcon(os.path.join(images_path, "arrow_down1.png"))
        else:
            icon = QIcon(os.path.join(images_path, "arrow_right1.png"))
        self.setIcon(icon)

    def leaveEvent(self, event):
        QPushButton.leaveEvent(self, event)
        if self.iocn_type:
            icon = QIcon(os.path.join(images_path, "arrow_down2.png"))
        else:
            icon = QIcon(os.path.join(images_path, "arrow_right2.png"))
        self.setIcon(icon)

    def mousePressEvent(self, event):
        QPushButton.mousePressEvent(self, event)
        if event.button() == Qt.LeftButton:
            if self.iocn_type:
                icon = QIcon(os.path.join(images_path, "arrow_right1.png"))
                self.iocn_type = False
            else:
                icon = QIcon(os.path.join(images_path, "arrow_down1.png"))
                self.iocn_type = True
            self.setIcon(icon)

    def setButtonIocn(self):
        if self.iocn_type:
            icon = QIcon(os.path.join(images_path, "arrow_right2.png"))
            self.iocn_type = False
        else:
            icon = QIcon(os.path.join(images_path, "arrow_down2.png"))
            self.iocn_type = True

        self.setIcon(icon)


class FrameBaseWidget(QWidget):

    def __init__(self, name=None, parent=None):
        super(FrameBaseWidget, self).__init__(parent)

        self.itmes = list()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self.button = BaseButton(name, self)
        self.widget = QWidget(self)

        self.widget_layout = QVBoxLayout()
        self.widget_layout.setContentsMargins(5, 0, 5, 0)
        self.widget_layout.setSpacing(2)
        self.widget.setLayout(self.widget_layout)

        layout.addWidget(self.button)
        layout.addWidget(self.widget)

        self.button.clicked.connect(self.showHiedWidget)

    def showHiedWidget(self):
        value = self.widget.isHidden()
        if value:
            self.widget.show()
        else:
            self.widget.hide()

    def addItme(self, name):
        if name not in [i.objectName() for i in self.itmes]:
            checkBox = QCheckBox(name, self.widget)
            checkBox.setObjectName(name)
            self.widget_layout.addWidget(checkBox)
            self.itmes.append(checkBox)

    def addItmes(self, names):
        for n in names:
            self.addItme(n)

    def getItme(self, name):
        itme = None
        for itme_check in self.itmes:
            if itme_check.objectName() == name:
                itme = itme_check
                break
        return itme

    def getItmes(self):
        return self.itmes

    def isItme(self, name):
        value = False
        itme = self.getItme(name)
        if itme:
            value = True
        return value

    def setChecked(self, value):
        for i in self.itmes:
            i.setChecked(value)

    def setItmeColor(self, name, color):
        itme = self.getItme(name)
        if itme:
            itme.setStyleSheet("QCheckBox{{color:{}}}".format(color))

    def getCheckItems(self):
        itmes = list()
        for itme in self.itmes:
            if itme.isChecked():
                itmes.append(itme)
        return itmes


if __name__ == "__main__":
    tsetWin = FrameBaseWidget("name")
    tsetWin.show()