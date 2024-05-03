# -*- coding: utf-8 -*-
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class StraightBaseButton(QLabel):
    clicked = Signal(int)

    def __init__(self, *args, **kwargs):
        super(StraightBaseButton, self).__init__(*args, **kwargs)
        self.font_metrics = QFontMetrics(self.font())

        self.setMaximumWidth(25)
        self.value = False

        self.color = "#444444"

    def paintEvent(self, evnet):
        painter = QStylePainter(self)
        option = QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawRoundedRect(QRect(x + 1, y + 1, width - 1, height - 1), 5, 5)

        text = self.text()
        font = self.font()

        text_width = self.font_metrics.width(text)

        painter.setFont(font)
        painter.translate(15, (height+text_width) / 2)
        painter.rotate(-90)
        painter.drawText(0, 0, text)

    def mousePressEvent(self, event):
        QLabel.mousePressEvent(self, event)
        self.clicked.emit(self.value)
        self.value = not self.value

    def enterEvent(self, event):
        QLabel.enterEvent(self, event)
        self.setStyleSheet("background-color:#707070")

    def leaveEvent(self, event):
        QLabel.leaveEvent(self, event)
        self.setStyleSheet("background-color:{}".format(self.color))


class StraightFrameBaseWidget(QWidget):

    def __init__(self, name=None, parent=None):
        super(StraightFrameBaseWidget, self).__init__(parent)

        self.itmes = list()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        straightLayout = QHBoxLayout()
        straightLayout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(straightLayout)

        self.button = StraightBaseButton(name, self)
        self.widget = QWidget(self)

        self.widget_layout = QVBoxLayout()
        self.widget_layout.setContentsMargins(5, 0, 5, 0)
        self.widget_layout.setSpacing(2)
        self.widget.setLayout(self.widget_layout)

        straightLayout.addWidget(self.button)
        straightLayout.addWidget(self.widget)

        self.button.clicked.connect(self.setChecked)

    def addItme(self, name):
        if name not in [i.objectName() for i in self.itmes]:
            checkBox = QCheckBox(name, self.widget)
            checkBox.setObjectName(name)
            checkBox.setMinimumHeight(22)
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
            
    def setTtemChecked(self, name, value):
        itme = self.getItme(name)
        if itme and isinstance(value, bool):
            itme.setChecked(value)

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

    def setColor(self, color_type=1):
        if color_type == 1:
            rbg = "#444444"
        else:
            rbg = "#555555"

        self.button.color = rbg
        self.setStyleSheet("background:{};".format(rbg))
        self.button.setStyleSheet("background-color:{}".format(rbg))

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


if __name__ == "__main__":
    tsetWin = StraightFrameBaseWidget("name")
    tsetWin.show()
    tsetWin.addItmes(['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5', 'Item 6', 'Item 7', 'Item 8', 'Item 9'])
    tsetWin.setColor(0)


