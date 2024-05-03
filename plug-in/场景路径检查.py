# -*- coding: utf-8 -*-
import maya.cmds as cmds
import arnold as ar
import os
from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import codecs
from collections import OrderedDict
from collections import defaultdict

class FileCheck:
    def __init__(self):
        self.ass_nodes = cmds.ls(type='aiStandIn')
        self.alembic_nodes = cmds.ls(type='AlembicNode')

    def return_all_asspath(self):
        if self.ass_nodes:
            getAllAss = []
            for node in self.ass_nodes:
                getPath = cmds.getAttr(node + ".dso")
                if getPath and getPath not in getAllAss:
                    getAllAss.append(getPath)
            return getAllAss
        else:
            return None

    def get_ass_imageandass(self, path):
        getAllPath = []
        ar.AiBegin()
        ar.AiMsgSetConsoleFlags(ar.AI_LOG_ALL)
        ar.AiASSLoad(path, ar.AI_NODE_ALL)
        iterator = ar.AiUniverseGetNodeIterator(ar.AI_NODE_ALL)

        while not ar.AiNodeIteratorFinished(iterator):
            node = ar.AiNodeIteratorGetNext(iterator)
            if ar.AiNodeIs(node, "MayaFile") or ar.AiNodeIs(node, "procedural") or ar.AiNodeIs(node, "image"):
                getPath = ar.AiNodeGetStr(node, "filename")
                if "<udim>" in getPath:
                    udim_files = self.return_udim_allfile(getPath)
                    getAllPath.extend(udim_files)
                elif getPath and getPath not in getAllPath:
                    getAllPath.append(getPath)
        ar.AiNodeIteratorDestroy(iterator)
        ar.AiEnd()
        return getAllPath

    def print_all_paths(self):
        sections = OrderedDict([
            (u'=================== ASS 路径 ===================\n', defaultdict(list)),
            (u'=================== 缺失ASS文件 ===================\n', defaultdict(list)),
            (u'=================== ASS贴图目录 ===================\n', defaultdict(list)),
            (u'=================== ASS贴图缺失 ===================\n', defaultdict(list)),
            (u'=================== 场景贴图路径 ===================\n', defaultdict(list)),
            (u'=================== 场景贴图缺失 ===================\n', defaultdict(list)),
            (u'=================== ABC文件路径 ===================\n', defaultdict(list)),
            (u'=================== 缺失ABC文件 ===================\n', defaultdict(list))
        ])

        all_paths = []

        ass_paths = self.return_all_asspath()  # 获取所有的ass文件路径
        if ass_paths:
            for path in ass_paths:
                dir_path = os.path.dirname(path)
                sections.get(u'=================== ASS 路径 ===================\n', defaultdict(list))[dir_path].append(path)
                if not os.path.exists(path):
                    sections.get(u'=================== 缺失ASS 文件 ===================\n', defaultdict(list))[dir_path].append(path)

            # 检查ASS贴图路径
            for path in ass_paths:
                tex_paths = self.get_ass_imageandass(path)
                for tex_path in tex_paths:
                    tex_dir = os.path.dirname(tex_path)
                    if isinstance(tex_dir, str):
                        tex_dir = unicode(tex_dir, 'utf-8')
                    sections.get(u'=================== ASS贴图目录 ===================\n', defaultdict(list))[tex_dir].append(tex_path)
                    if not os.path.exists(tex_path):
                        sections.get(u'=================== ASS贴图缺失 ===================\n', defaultdict(list))[tex_dir].append(tex_path)

        # 获取并检查场景贴图路径
        scene_tex_nodes = cmds.ls(type='file')
        for node in scene_tex_nodes:
            tex_path = cmds.getAttr(node + '.fileTextureName')
            tex_dir = os.path.dirname(tex_path)
            if isinstance(tex_dir, str):
                tex_dir = unicode(tex_dir, 'utf-8')
            sections.get(u'=================== 场景贴图路径 ===================\n', defaultdict(list))[tex_dir].append(tex_path)
            if not os.path.exists(tex_path):
                sections.get(u'=================== 场景贴图缺失 ===================\n', defaultdict(list))[tex_dir].append(tex_path)

        # 获取并检查ABC文件路径
        abc_nodes = cmds.ls(type='AlembicNode')
        for node in abc_nodes:
            abc_file_path = cmds.getAttr(node + '.abc_File')
            if isinstance(abc_file_path, str):
                abc_file_path = unicode(abc_file_path, 'utf-8')
            abc_dir = os.path.dirname(abc_file_path)
            sections.get(u'=================== ABC文件路径 ===================\n', defaultdict(list))[abc_dir].append(abc_file_path)
            if not os.path.exists(abc_file_path):
                sections.get(u'=================== 缺失ABC文件 ===================\n', defaultdict(list))[abc_dir].append(abc_file_path)

        result = []
        # 打印各个部分
        for title, paths_dict in sections.items():
            all_paths.append(title)
            for dir_path, paths in paths_dict.items():
                all_paths.append('\n' + u'————————————————————————————————————' + '\n' + dir_path +  '\n')  # 在这里添加换行
                for path in sorted(paths):
                    all_paths.append(path)

        return all_paths

    def return_udim_allfile(self, udim_fullpath):
        _list = []
        file_path = udim_fullpath.rsplit("/",1)[0]
        file_type = udim_fullpath.rsplit("/",1)[-1].rsplit("<udim>",1)[0]
        for f in os.listdir(file_path):
            if file_type in f:
                _list.append(file_path + "/" + f)
        return _list


class PathChecker(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(PathChecker, self).__init__(parent)

        self.fc = FileCheck()
        self.setWindowTitle(u"路径检查工具")
        self.resize(600, 400)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        # 创建用于放置按钮的水平布局
        self.button_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        # 创建开始检查按钮
        self.check_button = QtWidgets.QPushButton(u"开始检查")
        self.check_button.clicked.connect(self.check_paths)
        self.button_layout.addWidget(self.check_button)

        # 创建打印按钮
        self.print_button = QtWidgets.QPushButton(u"打印")
        self.print_button.clicked.connect(self.save_to_file)
        self.button_layout.addWidget(self.print_button)

    def check_paths(self):
        result = self.fc.print_all_paths()
        self.text_edit.clear()  # 清空文本框
        for line in result:
            if isinstance(line, unicode):
                line = line.encode('utf-8')
            self.text_edit.append(line)  # 将结果追加到文本框

    def save_to_file(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, u"保存文件", "", "Text Files (*.txt)")
        if file_path:
            with codecs.open(file_path, 'w', 'utf-8') as f:
                f.write(self.text_edit.toPlainText())

def CJJC_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

jc_window = PathChecker(CJJC_window())
jc_window.show()