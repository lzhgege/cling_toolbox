# -*- coding: utf-8 -*-
# :copyright: Copyright (c) 2020 ClouArt GuangZhou
# Ftrack events
# AUTHOR = '___NEIL_CHENZHONG___'


from PySide2 import QtCore, QtGui, QtWidgets
import maya.cmds as cmds

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(371, 252)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainVBL = QtWidgets.QVBoxLayout()
        self.mainVBL.setObjectName("mainVBL")
        self.infoTB = QtWidgets.QTextBrowser(Form)
        self.infoTB.setObjectName("infoTB")
        self.mainVBL.addWidget(self.infoTB)
        self.cmdBtn = QtWidgets.QPushButton(Form)
        self.cmdBtn.setMinimumSize(QtCore.QSize(0, 30))
        self.cmdBtn.setAutoDefault(False)
        self.cmdBtn.setDefault(False)
        self.cmdBtn.setFlat(False)
        self.cmdBtn.setObjectName("cmdBtn")
        self.mainVBL.addWidget(self.cmdBtn)
        self.horizontalLayout.addLayout(self.mainVBL)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(u"清理 UV Sets")
        self.infoTB.setPlainText(u"功能：\n    删除 map1 以外的所有uvSets\n用法：\n    1.视图里框选要操作的对象\n    2.点击 执行 按钮")
        self.cmdBtn.setText(u"执行")

    def create_connections(self):
        self.cmdBtn.clicked.connect(self.doCleanupUVSets)

    def doCleanupUVSets(self):
        print("doCleanupUVSets ...")
        uvs_list = cmds.polyUVSet(query=True, allUVSets=True)
        if len(uvs_list)>0 and 'map1' in uvs_list:
            for uvs in uvs_list:
                if 'map1' in uvs:
                    continue
                else:
                    print(u"    删除(Delete)", uvs)
                    cmds.polyUVSet( delete=True, uvSet=uvs)
        else:
            print(u"    uvset \"map1\" 不存在，忽略！")
        cmds.inViewMessage( amg = u'清理uvSets，执行完成，详细执行信息请看脚本编辑器。', pos='midCenter', fade=True )


class yTUVSets(Ui_Form, QtWidgets.QWidget):
    def __init__(self, parent=None):
        Ui_Form.__init__(self)
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.retranslateUi(self)
        self.create_connections()


doo = yTUVSets()
doo.show()