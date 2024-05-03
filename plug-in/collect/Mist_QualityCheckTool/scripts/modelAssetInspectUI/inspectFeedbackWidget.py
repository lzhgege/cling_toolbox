# -*- coding: utf-8 -*-
import os
import sys
import logging
import webbrowser
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import modelAssetInspectUI.common.utils_fun_dict as utils_fun
from modelAssetInspectUI.common import utils
import modelAssetInspectUI.views.inspectFeedbackCentralWidget as inspectFeedbackCentralWidget
from modelAssetInspectUI.model.checkBase import getIntermediateObjectDatas
import modelAssetInspectUI.model.loggingBase as loggingBase

from modelAssetInspectUI.views import documentConfigWidget
from modelAssetInspectUI.views.documentConfigWidget import DocumentConfigWidget


if sys.version_info[0] == 2:
    reload(utils_fun)
    reload(utils)
    reload(documentConfigWidget)
elif sys.version_info[0] == 3:
    import importlib
    importlib.reload(utils_fun)    
    importlib.reload(utils)
    importlib.reload(documentConfigWidget)


# reload(inspectFeedbackCentralWidget)
# reload(utils_fun)
# reload(loggingBase)
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class InspectFeedbackWidget(MayaQWidgetDockableMixin, QWidget):

    def __init__(self, parent=None):
        super(InspectFeedbackWidget, self).__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        self.logger.handlers = list()
        loggingBase.setLoggingConsole(self.logger)

        self.assetWidgrt = parent

        self.setWindowTitle(u"检查结果")
        self.setObjectName("InspectFeedbackWidget")

        self.pb_expand=QPushButton(u"一键展开/收缩")
        self.pb_document=QPushButton(u"帮助文档")


        self.dockingFrame = QMainWindow(self)
        self.dockingFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.dockingFrame.setWindowFlags(Qt.Widget)
        self.dockingFrame.setDockOptions(QMainWindow.AnimatedDocks)

        self.centralWidget = inspectFeedbackCentralWidget.InspectFeedbackCentralWidget()
        
        self.dockingFrame.setCentralWidget(self.centralWidget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.pb_document)
        layout.addWidget(self.pb_expand)
        layout.addWidget(self.dockingFrame, 0)
        self.setLayout(layout)

        try:
            self.assetWidgrt.run.clicked.connect(self.runChecked)
        except:
            pass
        self.pb_document.clicked.connect(self.openDocument)
        self.pb_expand.clicked.connect(self.centralWidget.set_widgets_show_or_hide)

    def openDocument(self):
        webbrowser.open("http://wiki.4wgame.com/pages/viewpage.action?pageId=27363146")

    def openConfigDocument(self):
        self.document_widget=DocumentConfigWidget(self)
        self.document_widget.show()

    def runChecked(self):
        checkeds=self.assetWidgrt.runChecked()
        if not checkeds:
            QMessageBox.warning(self,"警告","请勾选质检项再运行")
            return
        self.centralWidget.showProcess()
        self.centralWidget.clear()
        self.repaint()
        self.run()

    def feedbackCompleted(self):
        self.centralWidget.showInspect()

    def run(self):
        #loggingBase.setLoggingFileName(self.logger)
        items = [i.objectName() for i in self.assetWidgrt.runChecked()]
        self.centralWidget.processWidget.setItems(items)
        if not items:
            return
        for name in items:
            if not self.centralWidget.processWidget.state:
                return

            self.centralWidget.processWidget.setText(name)
            # self.repaint()
            # QApplication.processEvents()
            lable_name = utils_fun.CHECK_FUN_DICT[name][0]
            fun = utils_fun.CHECK_FUN_DICT[name][1]
            repair_fun = utils_fun.CHECK_FUN_DICT[name][2]
            win_type = utils_fun.CHECK_FUN_DICT[name][3]

            if name in items:
                values = fun(self.callbackFun)
                # if values:
                #     self.logger.info(u"{}(检查-未通过)".format(name))
                # else:
                #     self.logger.info(u"{}(检查-通过)".format(name))
                if not values:
                    continue
            else:
                values = list()

            if values is None:
                values = list()
            self.centralWidget.addBackWidget(name, values, fun=repair_fun, win_type=win_type, repair_text=lable_name)

            if name == u"检查transform下面是否有多个shape":
                if values:
                    dataWidget = self.centralWidget.getBackWidget(name).dataWidget
                    dataWidget.setSelectionMode(QAbstractItemView.SingleSelection)
                    datas = getIntermediateObjectDatas(values)
                    dataWidget.setItemStyle(datas)

            backWidgetWidget = self.centralWidget.getBackWidget(name)
            if name not in items:
                backWidgetWidget.setNotChecked()

            if name in utils_fun.NOT_DATA_WIDGET:
                backWidgetWidget.hideDataWidget()
        self.feedbackCompleted()

    def callbackFun(self, text=None, num=0):

        if not self.centralWidget.processWidget.state:
            return False

        QApplication.processEvents()
        self.centralWidget.processWidget.setNumObject(num)
        if text:
            self.centralWidget.processWidget.setObjectText(text)
        self.centralWidget.processWidget.add()
        return True
        # self.repaint()
    


if __name__ == "__main__":
    tsetWin = BackInspectWidget()
    tsetWin.show()