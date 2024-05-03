# -*- coding: utf-8 -*-
import sys
file_path,file_name = os.path.split(__file__.replace('\\', '/'))
paths = [file_path + '/scripts', 
         file_path + '/scripts/modelAssetInspectUI',
         file_path + '/scripts/modelAssetInspectUI/common',
         file_path + '/scripts/modelAssetInspectUI/model',
         file_path + '/scripts/modelAssetInspectUI/views',
         ]
for each in paths:         
    sys.path.append(each)

import modelAssetInspectUI.assetInspectWidget as assetInspectWidget
import modelAssetInspectUI.inspectFeedbackWidget as inspectFeedbackWidget
import modelAssetInspectUI.views.documentConfigWidget as documentConfigWidget

if sys.version_info[0] == 2:
    reload(assetInspectWidget)
    reload(inspectFeedbackWidget)
    reload(documentConfigWidget)
elif sys.version_info[0] > 2:
    try:
        import importlib
        importlib.reload(assetInspectWidget)
        importlib.reload(inspectFeedbackWidget)
        importlib.reload(documentConfigWidget)
    except:
        pass
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets
def getMayaWin():
    ptr = omui.MQtUtil.mainWindow()
    try:
        mayaWin = wrapInstance(long(ptr), QtWidgets.QWidget)
    except:
        mayaWin = wrapInstance(int(ptr), QtWidgets.QWidget)
    return mayaWin

# if 'SHD_Widget_Mist' in dir():
#     pass
# else:
#     SHD_Widget_Mist = None

# def createUI():
#     global SHD_Widget_Mist
#     if SHD_Widget_Mist is None:
#         SHD_Widget_Mist = assetInspectWidget.AssetInspectWidget()
#         SHD_Widget_Mist.show(dockable=True, retain=False, width=260, closeCallback="SHD_Widget_Mist=None")
#         workspaceControlName_b = SHD_Widget_Mist.objectName() + 'WorkspaceControl'

#         inspectWidget = inspectFeedbackWidget.InspectFeedbackWidget(SHD_Widget_Mist.centralWidget)
#         inspectWidget.show(dockable=True, retain=False, width=260, area='right', controls=workspaceControlName_b)
#     else:
#         if int(cmds.about(q=True, v=True)) <= 2016:
#             SHD_Widget_Mist.show()
#             try:
#                 inspectWidget = inspectFeedbackWidget.InspectFeedbackWidget(SHD_Widget_Mist.centralWidget)
#                 inspectWidget.show(dockable=True, retain=False, width=260, area='right')
#             except:
#                 pass
#         else:
#             try:
#                 control_widget = getWorkspaceControlRootWidget(SHD_Widget_Mist)
#                 control_widget.activateWindow()
#                 if control_widget.isMinimized():
#                     control_widget.showNormal()
#             except:
#                 pass

# def getWorkspaceControlRootWidget(widget, value=5):
#     parent_widget = widget.parent()
#     value -= 1
#     if value == 0:
#         return parent_widget
#     else:
#         return getWorkspaceControlRootWidget(parent_widget, value)

class MistCheckTool(QtWidgets.QMainWindow):
    def __init__(self,parent=getMayaWin()):
        super(MistCheckTool, self).__init__(parent)
        self.setWindowTitle(u"质检工具20230814")
        self.setMinimumHeight(600)
        self.setMinimumWidth(800)
        self.setGeometry(1920-self.width()-300,100,self.width(),self.height())
        self.create_widgets()
        self.create_layouts()
    def create_widgets(self):
        self.create_bar()
        self.main_widget=QtWidgets.QWidget()
        self.group1=QtWidgets.QGroupBox(u"质检项")
        self.group1.setMinimumWidth(300)
        self.left_widget=assetInspectWidget.AssetInspectWidget()
        self.group2=QtWidgets.QGroupBox(u"检查结果")
        self.right_widget=inspectFeedbackWidget.InspectFeedbackWidget(self.left_widget.centralWidget)
        self.setCentralWidget(self.main_widget)

    def create_layouts(self):
        layout_left=QtWidgets.QHBoxLayout()
        layout_left.addWidget(self.left_widget)
        self.group1.setLayout(layout_left)

        layout_result=QtWidgets.QHBoxLayout()
        layout_result.addWidget(self.right_widget)
        self.group2.setLayout(layout_result)

        self.spliter=QtWidgets.QSplitter()
        self.spliter.addWidget(self.group1)
        self.spliter.addWidget(self.group2)
        self.spliter.setSizes([400,400])

        self.main_layout=QtWidgets.QHBoxLayout(self.main_widget)
        self.main_layout.addWidget(self.spliter)

    def create_bar(self):
        bar=self.menuBar()
        file=bar.addMenu(u"文件")
        config=file.addAction(u"配置")
        config.triggered.connect(self.open_config)
    
    def open_config(self):
        self.doc_widget=documentConfigWidget.DocumentConfigWidget()
        self.doc_widget.show()

try:
    mist_check_tool.close()
    mist_check_tool.deleteLater()
except:
    pass
mist_check_tool = MistCheckTool()
mist_check_tool.show()
