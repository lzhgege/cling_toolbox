# -*- coding: utf-8 -*-
import maya.cmds as cmds
try:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


class ListBaseWidget(QListView):

    def __init__(self, parent=None):
        super(ListBaseWidget, self).__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

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

    def addData(self, data):
        model = self.model()
        item = QStandardItem(data)
        model.appendRow(item)
        return item 

    def addDatas(self, datas):
        isColor1 = True                
        color1 = QBrush(QColor(200,200,200))
        color2 = QBrush(QColor(150,150,150))
        for data in datas:
            if isinstance(data,list):
                isColor1 = not isColor1
                color=None
                if isColor1:
                    color = color1
                else:
                    color = color2
                for da in data:
                    item=self.addData(da)
                    item.setForeground(color)
            else:
                self.addData(data)

    def selectObject(self, ModelIndex):
        # datas =[d.split('.')[0] for d in self.getSelectItemDatas()]
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
            modelIndex = model.index(i, 0)
            datas.append(modelIndex.data())
        return datas

    def removeSelectItems(self, datas):
        model = self.model()
        for data in datas:
            items = model.findItems(data)
            for item in items:
                model.removeRow(item.row())

    def getSelectItemDatas(self):
        indexs = self.selModel.selectedIndexes()
        select_lists = list()
        for i in indexs:
            if i.isValid():
                str_data = i.data()
                select_lists.append(str_data)
        
        return select_lists

    def itemCount(self):
        return self.model().rowCount()


# if __name__ == "__main__":
    # tsetWin = ListBaseWidget()
    # tsetWin.show()
    # tsetWin.setData(['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5', 'Item 6', 'Item 7', 'Item 8', 'Item 9'])
    # aaa = [u'DnCloth_002_mo.e[3439]',u'DnCloth_002_mo.e[3447]',u'DnCloth_002_mo.vtx[1865]',u'DnCloth_002_mo.vtx[1869]',u'DnCloth_002_mo.vtx[1871]',u'DnCloth_002_mo.vtx[1873]']
    # tsetWin.setData(aaa)
