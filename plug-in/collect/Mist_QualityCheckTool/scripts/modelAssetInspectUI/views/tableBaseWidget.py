# -*- coding: utf-8 -*-
import maya.cmds as cmds
import copy
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class TableBaseWidget(QTableView):

    def __init__(self, parent=None):
        super(TableBaseWidget, self).__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QTableView.SelectRows)

        self.labels = [u"shape", u"面数", u"边界体积"]
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(self.labels)
        self.setModel(model)

        header = self.horizontalHeader()
        header.sectionDoubleClicked.connect(self.sortHeader)

        self.selModel = self.selectionModel()
        self.selModel.selectionChanged.connect(self.selectObject)

        self.setMinimumHeight(180)

    def clearData(self):
        count = self.model().rowCount()
        self.model().removeRows(0, count)

    def setData(self, data):
        if not isinstance(data, list):
            return
        self.clearData()
        self.addDatas(data)

        self.resizeColumnsToContents()
        self.verticalHeader().setDefaultSectionSize(24)

    def addData(self, data_list):
        model = self.model()
        row = model.rowCount()
        for index, data in enumerate(data_list):
            if index > 0:
                data = data + u" 万"
            data = data + u"  "
            item = QStandardItem(data)
            item.setEditable(False)
            model.setItem(row, index, item)

    def addDatas(self, datas):
        for data in datas:
            self.addData(data)

    def getData(self):
        datas = list()
        model = self.model()
        row = model.rowCount()
        column = model.columnCount()
        for i in xrange(row):
            column_data = list()
            for s in xrange(column):
                modelIndex = model.index(i, s)
                value = modelIndex.data()
                value = value.split()[0]
                column_data.append(value)
            datas.append(column_data)
        return datas
        
    def sortHeader(self, index):
        datas = self.getData()
        if index == 0:
            new_datas = sorted(datas, key=lambda data: data[index], reverse=True)
        else:
            new_datas = sorted(datas, key=lambda data: float(data[index]), reverse=True)

        labels = copy.deepcopy(self.labels)
        labels[index] = self.labels[index] + u"↓"
        self.model().setHorizontalHeaderLabels(labels)

        self.setData(new_datas)

    def selectObject(self, ModelIndex):
        indexs = self.selModel.selectedIndexes()
        select_lists = list()
        for i in indexs:
            if i.isValid() and i.column() == 0:
               if cmds.objExists(i.data()):
                    select_lists.append(i.data())
           
        cmds.select(select_lists, r=True)

if __name__ == "__main__":
    tsetWin = TableBaseWidget()
    tsetWin.show()
    tsetWin.setData([['Item 1', 'Item 2', 'Item 3', 'Item 4']])
    tsetWin.clearData()