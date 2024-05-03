# -*- coding: utf-8 -*-
import os,sys,re
import arnold as ar
import functools
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

def mayaMainWindows():
    mainWindowsPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowsPtr),QtWidgets.QWidget)
from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def __init__(self):
        self.file_type = []
        self.screen_checkbox = []
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 400)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter_2 = QtWidgets.QSplitter(Form)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.treeWidget = QtWidgets.QTreeWidget(self.splitter_2)
        self.treeWidget.setObjectName("treeWidget")
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.cut_progressBar = QtWidgets.QProgressBar(self.splitter)
        self.cut_progressBar.setMinimumSize(QtCore.QSize(0, 25))
        self.cut_progressBar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.cut_progressBar.setProperty("value", 0)
        self.cut_progressBar.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.cut_progressBar.setTextVisible(True)
        self.cut_progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.cut_progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.cut_progressBar.setObjectName("cut_progressBar")
        self.pushButton = QtWidgets.QPushButton(self.splitter)
        self.pushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.splitter_2)
        
        self.printButton = QtWidgets.QPushButton(self.splitter)
        self.printButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.printButton.setObjectName("printButton")
        
        #设置窗口flags
        self.setWindowFlags(QtCore.Qt.Window)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        #自适应
        header = self.treeWidget.header()  # type: QtWidgets.QHeaderView
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        #qss
        qss = '''QTreeView::branch:!adjoins-item{
    border-image:url(:/branch-vline.svg) 0;
}

QTreeView::branch:has-siblings:adjoins-item{
    border-image:url(:/branch-more.svg) 0;
}

QTreeView::branch:!has-children:!has-siblings:adjoins-item{
    border-image:url(:/branch-end.svg) 0;
}

QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings{
    border-image:none;
    image:url(:/moveUVRight.png);
}

QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings{
    border-image:none;
    image:url(:/moveUVDown.png);
}
'''
        self.treeWidget.setStyleSheet(qss)
        # 右键UI
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.showrtextMenu)
        self.create_ass_proxy_Menu()
        #____________________________
        self.setAcceptDrops(True)
        #按钮执行
        self.ui_control()
    def retranslateUi(self, Form):
        Form.setWindowTitle(u"读取Maya文件Ass贴图_20230915")
        self.pushButton.setText("Start")
        self.treeWidget.headerItem().setText(0, u"AssPath--PicPath")
        self.treeWidget.headerItem().setText(1, u"Tx文件")
        self.printButton.setText(u"打印路径")
    #================================右键菜单
    def create_ass_proxy_Menu(self):
        iconA = QtGui.QIcon()
        iconA.addPixmap(QtGui.QPixmap(":\hsTearOff.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #创建右键菜单 
        self.ass_proxy_Menu = QtWidgets.QMenu(self)
        self.menuitemA = self.ass_proxy_Menu.addAction(u'复制路径')
        self.menuitemA.setIcon(iconA)
        self.ass_proxy_Menu.addSeparator()
        self.menuitemC = self.ass_proxy_Menu.addAction(u'全部展开')
        self.menuitemD = self.ass_proxy_Menu.addAction(u'全部收起')
        self.ass_proxy_Menu.addSeparator()
        self.menuitemB = self.ass_proxy_Menu.addMenu(u'筛选')
        
        self.menuitemB.addSeparator()


        #
        self.menuitemA.triggered.connect(self.copy_filepath)
        
        self.menuitemC.triggered.connect(self.treeWidget.expandAll)
        self.menuitemD.triggered.connect(self.treeWidget.collapseAll)
        
    #右键点击时调用的函数 
    def showrtextMenu(self):
        # 菜单在鼠标点击的位置显示
        self.ass_proxy_Menu.exec_(QtGui.QCursor().pos())
    
    #================================右键 UI 执行函数
    def ui_control(self):
        self.pushButton.clicked.connect(self.check_ass_texture_path)
        self.printButton.clicked.connect(self.print_to_file)

    # 复制路径
    def copy_filepath(self):
        sel_treeitem=self.treeWidget.selectedItems()
        for item in sel_treeitem:
            print item.text(0)
            clipboard = QApplication.clipboard()
            clipboard.setText(item.text(0))

    def print_to_file(self):
        result = cmds.fileDialog2(fileMode=0, dialogStyle=2, caption="Save as")
        if result is not None:
            texture_paths = {}
            missing_texture_paths = set()
            ass_paths = {}
            missing_ass_paths = set()
            scene_texture_paths = {}
            missing_scene_texture_paths = set()
            abc_paths = {}  # 用于保存abc文件的路径
            missing_abc_paths = set()  # 用于保存不存在的abc文件的路径

            root = self.treeWidget.invisibleRootItem()
            for i in range(root.childCount()):
                item = root.child(i)
                # 检查ass文件是否存在
                if os.path.exists(item.text(0)):
                    # 保存完整的ass路径
                    dir_path = os.path.dirname(item.text(0))
                    if dir_path not in ass_paths:
                        ass_paths[dir_path] = set()
                    ass_paths[dir_path].add(item.text(0))
                else:
                    missing_ass_paths.add(item.text(0))

                for j in range(item.childCount()):
                    child_item = item.child(j)
                    # 只保存贴图路径的根目录
                    dir_path = os.path.dirname(child_item.text(0))
                    parent_dir = os.path.dirname(dir_path)
                    # 检查贴图文件是否存在
                    if os.path.exists(child_item.text(0)):
                        if parent_dir not in texture_paths:
                            texture_paths[parent_dir] = set()
                        texture_paths[parent_dir].add(dir_path)
                    else:
                        missing_texture_paths.add(child_item.text(0))

            # 获取场景内所有的file节点，并获取它们的贴图路径
            file_nodes = cmds.ls(type='file')
            for node in file_nodes:
                texture_path = cmds.getAttr(node + '.fileTextureName')
                dir_path = os.path.dirname(texture_path)
                parent_dir = os.path.dirname(dir_path)
                # 检查贴图文件是否存在
                if os.path.exists(texture_path):
                    if parent_dir not in scene_texture_paths:
                        scene_texture_paths[parent_dir] = set()
                    scene_texture_paths[parent_dir].add(dir_path)
                else:
                    missing_scene_texture_paths.add(texture_path)

            # 获取场景内所有的AlembicNode节点，并获取它们的abc 文件路径
            Alembic_nodes = cmds.ls(type='AlembicNode')
            for node in Alembic_nodes:
                abc_path = cmds.getAttr(node + '.abc_File')
                # 检查abc文件是否存在
                if os.path.exists(abc_path):
                    dir_path = os.path.dirname(abc_path)
                    if dir_path not in abc_paths:
                        abc_paths[dir_path] = set()
                    abc_paths[dir_path].add(abc_path)
                else:
                    missing_abc_paths.add(abc_path)

            outfile = open(result[0], 'w')
            outfile.write('=================== ASS 路径 ===================\n')
            for dir_path in ass_paths:
                for path in ass_paths[dir_path]:
                    outfile.write(path + '\n')
                outfile.write('-----------------------------------------\n')
            outfile.write('=================== 缺失ASS文件 ===================\n')
            for path in missing_ass_paths:
                outfile.write(path + '\n')
            outfile.write('=================== ASS贴图目录 ===================\n')
            for parent_dir in texture_paths:
                for path in texture_paths[parent_dir]:
                    outfile.write(path + '\n')
                outfile.write('-----------------------------------------\n')
            outfile.write('=================== ASS贴图缺失 ===================\n')
            for path in missing_texture_paths:
                outfile.write(path + '\n')
            outfile.write('=================== 场景贴图路径 ===================\n')
            for parent_dir in scene_texture_paths:
                for path in scene_texture_paths[parent_dir]:
                    outfile.write(path + '\n')
            outfile.write('-----------------------------------------\n')
            outfile.write('=================== 场景贴图缺失 ===================\n')
            for path in missing_scene_texture_paths:
                outfile.write(path + '\n')
            outfile.write('=================== ABC文件路径 ===================\n')  # 输出abc文件的路径
            for dir_path in abc_paths:
                for path in abc_paths[dir_path]:
                    outfile.write(path + '\n')
            outfile.write('-----------------------------------------\n')
            outfile.write('=================== 缺失ABC文件 ===================\n')  # 输出缺失的abc文件的路径
            for path in missing_abc_paths:
                outfile.write(path + '\n')
            outfile.close()

    # 添加筛选类型
    def add_screen_type(self):
        self.menuitemB.clear()
        self.menuitemB_A = self.menuitemB.addAction(u'All')
        self.menuitemB_B = self.menuitemB.addAction(u'None')
        self.menuitemB_A.triggered.connect(functools.partial(self.change_screen,True))
        self.menuitemB_B.triggered.connect(functools.partial(self.change_screen,False))
        for item in self.file_type:
            newAction = self.menuitemB.addAction(item)
            newAction.triggered.connect(self.refersh_search)
            newAction.setCheckable(True)
            newAction.setChecked(True)
            self.screen_checkbox.append(newAction)

    # 筛选--all--none
    def change_screen(self,screen_bool):
        for widget in self.screen_checkbox:
            widget.setChecked(screen_bool)
        #刷新筛选
        self.refersh_search()
    def refersh_search(self):

        screen_show_type = []
        screen_hidden_type = []
        for item in self.screen_checkbox:
            if item.isChecked():
                screen_show_type.append(item.text())
            else:
                screen_hidden_type.append(item.text())

        # 显示
        for file_type in screen_show_type:
            for itemwidget in self.treeWidget.findItems(("." + file_type), Qt.MatchContains|Qt.MatchRecursive):
                self.treeWidget.setItemHidden(itemwidget,False)
        for file_type in screen_hidden_type:
            for itemwidget in self.treeWidget.findItems(("." + file_type), Qt.MatchContains|Qt.MatchRecursive):
                self.treeWidget.setItemHidden(itemwidget,True)
    #================================执行函数
    # 获取场景中的所有ass节点路径
    def return_all_asspath(self):
        getAllNodes = cmds.ls(type='aiStandIn')
        if getAllNodes:
            # 分析ass代理文件贴图路径
            getAllAss = []
            for node in getAllNodes:
                getPath = cmds.getAttr(node + ".dso")
                if getPath and getPath not in getAllAss:
                    getAllAss.append(getPath)
            return getAllAss
        else:
            return None
    
    # 获取ass节点中的ass节点和image节点
    def get_ass_imageandass(self,path):
        getAllPath = []
        ar.AiBegin()
        ar.AiMsgSetConsoleFlags(ar.AI_LOG_ALL)
        ar.AiASSLoad(path, ar.AI_NODE_ALL)
        iterator = ar.AiUniverseGetNodeIterator(ar.AI_NODE_ALL)

        while not ar.AiNodeIteratorFinished(iterator):
            node = ar.AiNodeIteratorGetNext(iterator)
            if ar.AiNodeIs(node, "MayaFile") or ar.AiNodeIs(node, "procedural") or ar.AiNodeIs(node, "image"):
                getPath = ar.AiNodeGetStr(node, "filename")
                if getPath and getPath not in getAllPath:
                    getAllPath.append(getPath)
        ar.AiNodeIteratorDestroy(iterator)
        ar.AiEnd()
        return getAllPath
    
    # 添加treewidgetitem
    def add_treewidgetitem(self,_widget,filefullpath):
        # 
        newChileItem=QtWidgets.QTreeWidgetItem(_widget)
        newChileItem.setText(0,str(filefullpath))
        #字体颜色
        brush_red = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush_red.setStyle(QtCore.Qt.NoBrush)
        brush_green = QtGui.QBrush(QtGui.QColor(0, 255, 0))
        brush_green.setStyle(QtCore.Qt.NoBrush)
        if filefullpath.endswith(".tx"):
            newChileItem.setForeground(0, brush_green)
        elif filefullpath.endswith(".ass"):
            return
        elif not filefullpath.endswith(".tx"):
            newChileItem.setForeground(0, brush_red)
        
        #tx文件是否存在
        icon_0 = QtGui.QIcon()
        if os.path.exists(u"{}.tx".format(filefullpath.rsplit(".",1)[0])):
            icon_0.addPixmap(QtGui.QPixmap(":\confirm.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            newChileItem.setIcon(1,icon_0)
        else:
            icon_0.addPixmap(QtGui.QPixmap(":\error.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            newChileItem.setIcon(1,icon_0)
        #文件是否存在
        icon_1 = QtGui.QIcon()
        if os.path.exists(filefullpath):
            icon_1.addPixmap(QtGui.QPixmap(":\confirm.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            newChileItem.setIcon(0,icon_1)
        else:
            icon_1.addPixmap(QtGui.QPixmap(":\error.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            newChileItem.setIcon(0,icon_1)
    
    # 递归获取ass文件中的ass节点和image节点
    def get_ass_all_assandimage(self,asspath):
        _dic = {}
        _dic[asspath] =[]
        ass_nodes = self.get_ass_imageandass(asspath)
        for node in ass_nodes:
            if node.endswith(".ass"):
                _dic[asspath].append(self.get_ass_all_assandimage(node))
            else:
                _dic[asspath].append(node)
        return _dic
    
    # 递归添加treewidgetitem
    def from_dic_ass_widget(self, _dic, _widget):
        if _dic:
            for key,val in _dic.items():
                newItem=QtWidgets.QTreeWidgetItem(_widget)
                newItem.setText(0,key)
                for item in val:
                    if type(item) == type({}):
                        self.from_dic_ass_widget(item, newItem)
                    else:
                        if "udim" in item:
                            pass
                        else:
                            self.add_treewidgetitem(newItem, item)
                            if not item.rsplit(".",1)[-1] in self.file_type:
                                self.file_type.append(item.rsplit(".",1)[-1])
    
    # udim贴图返回所有udim文件
    def return_udim_allfile(self, udim_fullpath):
        _list = []
        file_path = udim_fullpath.rsplit("/",1)[0]
        file_type = udim_fullpath.rsplit("/",1)[-1].rsplit("<udim>",1)[0]
        for f in os.listdir(file_path):
            if file_type in f:
                _list.append(file_path + "/" + f)
        return _list
    # 执行
    def check_ass_texture_path(self):
        self.treeWidget.clear()
        all_ass_path = self.return_all_asspath()
        
        if all_ass_path:
            #进度条
            self.cut_progressBar.setValue(0)
            self.cut_progressBar.setMaximum(len(all_ass_path))
            #清除旧的UI
            if self.treeWidget.topLevelItemCount():
                self.treeWidget.clear()
            for index,val in enumerate(all_ass_path):
                #进度条+1
                self.cut_progressBar.setValue(index + 1)
                
                all_node_dic = self.get_ass_all_assandimage(val)
                self.from_dic_ass_widget(all_node_dic,self.treeWidget)

            self.cut_progressBar.setValue(len(all_ass_path))
            self.cut_progressBar.setFormat(u"完成")

            self.add_screen_type()

            #展开
            self.treeWidget.expandAll()


            cmds.confirmDialog( title=u'提示！！',icon='information', message=u"检查完成               \n\n可以右键进行筛选查看", button=[u'关闭'])

        else:
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"场景中未发现Arnold代理", button=[u'关闭'])
    



class MainWindow(Ui_Form,QtWidgets.QWidget):
    def __init__(self,parent=mayaMainWindows()):
        Ui_Form.__init__(self)
        QtWidgets.QWidget.__init__(self,parent)
        self.setupUi(self)
        self.retranslateUi(self)


try:
    win.close()
    win.deleteLater()
except:
    pass
win=MainWindow()
win.show()

