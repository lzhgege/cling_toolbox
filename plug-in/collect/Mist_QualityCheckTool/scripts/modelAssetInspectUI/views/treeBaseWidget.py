# -*- coding: utf-8 -*-
import maya.cmds as cmds
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class TreeBaseWidget(QTreeView):

    def __init__(self, parent=None):
        super(TreeBaseWidget, self).__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setHeaderHidden(True)

        self.list_data = list()

        model = QStandardItemModel()
        self.setModel(model)
        self.selModel = self.selectionModel()
        self.selModel.selectionChanged.connect(self.selectObject)

        self.setMinimumHeight(180)

    def clearData(self):
        self.model().clear()
        self.list_data = list()

    def setData(self, data):
        if not isinstance(data, list):
            return
        self.clearData()
        self.addDatas(data)

        # 默认是展开子节点状态
        self.expandAll()

    def addData(self, data):
        model = self.model()
        if isinstance(data, list):
            if len(data) == 2:
                if not isinstance(data[1], list):
                    return
                item = QStandardItem(data[0])
                model.appendRow(item)
                for i in data[1]:
                    citem = QStandardItem(i)
                    item.appendRow(citem)

    def addDatas(self, datas):
        for data in datas:
            self.addData(data)

    def selectObject(self, ModelIndex):
        datas = []
        for d in self.getSelectItemDatas():
            if not d.count('.vtx[') and not d.count('.e[') and not d.count('.f['):
                datas.append(d.split('.')[0])
            else:
                datas.append(d)
        select_lists = [data for data in datas if cmds.objExists(data)]
        cmds.select(select_lists, r=True)

    def getData(self):
        model = self.model()
        row = model.rowCount()
        datas = list()
        for i in xrange(row):
            items_data = list()
            item = model.item(i, 0)
            items_data.append(item.text())
            child_row = item.rowCount()
            child_data = list()
            for c in xrange(child_row):
                child_item = item.child(c)
                child_data.append(child_item.text())

            items_data.append(child_data)
            datas.append(items_data)
        return datas

    def removeSelectItems(self, datas=None):
        pass
    
    def getSelectItemDatas(self):
        indexs = self.selModel.selectedIndexes()
        select_lists = list()
        for i in indexs:
            if i.isValid():
                str_data = i.data().split()[0]
                select_lists.append(str_data)

               
        return select_lists

    def itemCount(self):
        return self.model().rowCount()

    def findItem(self, name):
        model = self.model()
        row = model.rowCount()
        for i in xrange(row):
            item = model.item(i, 0)
            child_row = item.rowCount()
            for c in xrange(child_row):
                child_item = item.child(c)
                if child_item.text() == name:
                    return child_item
        return None

    def setItemSpecialStyle(self, item, value=False):
        font = item.font()
        font.setItalic(value)
        font.setUnderline(value)
        item.setFont(font)

    def setItemStyle(self, datas):
        if not isinstance(datas, list):
            return
        for data in datas:
            item = self.findItem(data[0])
            if item:
                self.setItemSpecialStyle(item, data[1])


if __name__ == "__main__":
    tsetWin = TreeBaseWidget()
    tsetWin.show()
    tsetWin.setData([['Item 1', ['a1', "b1"]], ['Item 2', ['a2', "b2"]], ['Item 3', ['a3', "b3"]]])
    tsetWin.getData()
    Item = tsetWin.findItem("a1")
    tsetWin.setItemSpecialStyle(Item, True)
