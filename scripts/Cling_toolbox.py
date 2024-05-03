# -*- coding: utf-8 -*-
# 作者：cling
# 微信：clingkaka
# 个人主页：www.cg6i.com
# 模型下载：www.cgfml.com
# AI聊天绘画：ai.cgfml.com
# 敲码不易修改搬运请保留以上信息，感谢！！！！！
import os
import json
import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore

import sys
from importlib import reload

from maya import OpenMayaUI
import shiboken2
import maya.mel as mel
import maya.mel
import re
from collections import OrderedDict, defaultdict
from functools import partial
from PySide2.QtWidgets import QTreeWidgetItem, QTreeWidget, QListWidgetItem, QMenu, QAction, QColorDialog
from PySide2.QtCore import Qt
import arnold as ar
import maya.OpenMayaUI as omui
import codecs
import subprocess
from shiboken2 import wrapInstance
from PySide2.QtGui import QIcon, QColor
from PySide2.QtWidgets import QSplitter, QAbstractItemView, QDialog, QTextEdit, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QFileDialog
from PySide2.QtCore import QRegExp
from PySide2.QtGui import QRegExpValidator
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QThread, Signal
from PySide2.QtCore import QSettings

class LoadJsonThread(QThread):
    load_finished = Signal(dict, str)


    def run(self):
        try:
            response = requests.get('https://tool.cgfml.com/Cling_toolbox_3.0/help_document.json', timeout=5)
            gx = requests.get('https://tool.cgfml.com/Cling_toolbox_3.0/gx_document.html', timeout=5)
            response.encoding = 'utf-8'
            gx.encoding = 'utf-8'
            data = response.json()
            self.load_finished.emit(data, gx.text)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.load_finished.emit({}, "当前为离线版，更新记录，详情请访问https://www.cgfml.com/195275.html查看")



sys.path.append('D:\\Cling_toolbox\\external_library')
from PIL import Image
import requests

sys.path.append("D:/Cling_toolbox/plug-in/GPUcache")
from GPU_Export import ExportWindow
from GPU_switch_A import MayaUIWindow


class BorderDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(BorderDelegate, self).__init__(parent)
        self.color_map = {}
        self.update_color_map()

    def update_color_map(self):
        try:
            # 试图读取JSON 数据
            with open("D:/Cling_toolbox/json/collect_plugin.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
        except IOError:
            # 如果出现 IOError，那么就创建一个空的数据集
            data = []

        self.color_map = {node['name']: node.get('color', '28,28,40') for node in data}

    def paint(self, painter, option, index):
        option.rect.adjust(0, 0, -2, -2)
        painter.save()

        # 判断是否为收藏节点
        is_favorite = index.data(QtCore.Qt.UserRole + 2)
        if is_favorite:
            # 获取当前节点的标识符
            node_name = index.data()
            color_data = self.color_map.get(node_name, '28,28,40')
            r, g, b = map(int, color_data.split(','))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(r, g, b)))  # 设置收藏节点颜色
        elif index.parent().isValid():
            # 子级
            painter.setBrush(QtGui.QBrush(QtGui.QColor(28, 30, 28)))  # 设置子级颜色
        else:
            # 父级
            is_favorite_group = index.data(QtCore.Qt.UserRole + 3)
            if is_favorite_group:
                # 收藏组
                painter.setBrush(QtGui.QBrush(QtGui.QColor(25, 57, 80)))  # 设置收藏组颜色
            else:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(51, 90, 80)))  # 设置其他父级颜色

        painter.setPen(QtGui.QPen(QtCore.Qt.transparent, 2, QtCore.Qt.SolidLine))  # 设置边框颜色为透明
        painter.drawRoundedRect(option.rect, 6, 6)

        painter.restore()
        super(BorderDelegate, self).paint(painter, option, index)






class CustomDialog(QDialog):
    def __init__(self, parent=None, field_info=None):
        super(CustomDialog, self).__init__(parent)
        self.current_color = QColor()

        self.setWindowTitle(u"自定义工具")

        self.layout = QVBoxLayout()

        self.name_label = QLabel(u"工具名：")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(u"请输入工具名称")
        self.name_layout = QHBoxLayout()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_edit)

        self.paixu_label = QLabel(u"排序：")
        self.paixu_edit = QLineEdit()
        self.paixu_edit.setPlaceholderText(u"请输入数值，数值越大越靠前")
        self.color_label = QLabel(u"按钮底色：")
        self.color_edit = QPushButton(u"选择颜色")
        self.color_edit.clicked.connect(self.get_color)

        self.paixu_layout = QHBoxLayout()
        self.paixu_layout.addWidget(self.paixu_label)
        self.paixu_layout.addWidget(self.paixu_edit)
        self.paixu_layout.addWidget(self.color_label)
        self.paixu_layout.addWidget(self.color_edit)


        # 设置paixu_edit只接受数字输入
        reg = QRegExp("[0-9]+$")  # 只接受数字
        pValidator = QRegExpValidator(self)
        pValidator.setRegExp(reg)
        self.paixu_edit.setValidator(pValidator)

        self.icon_label = QLabel(u"图标路径：")
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText(u"请选择或输入图标路径")
        self.browse_icon_button = QPushButton(u"选择图标")
        self.icon_layout = QHBoxLayout()
        self.icon_layout.addWidget(self.icon_label)
        self.icon_layout.addWidget(self.icon_edit)
        self.icon_layout.addWidget(self.browse_icon_button)
        self.browse_icon_button.clicked.connect(self.browse)

        self.introduce_label = QLabel(u"工具介绍：")
        self.introduce_edit = QTextEdit()

        # 如果提供了初始字段信息，则填充文本框
        if field_info is not None:
            self.name_edit.setText(field_info.get('name', ''))
            self.icon_edit.setText(field_info.get('icon', ''))
            self.introduce_edit.setText(field_info.get('introduce', ''))
            self.paixu_edit.setText(field_info.get('sort', ''))
            color_str = field_info.get('color', '')
            if color_str:
                # 将字符串形式的颜色转换为QColor对象
                color = QColor(color_str)
                # 设置按钮的背景颜色
                self.color_edit.setStyleSheet("background-color: %s" % color.name())
                # 存储颜色值，以便在get_color中使用
                self.current_color = color

        self.ok_button = QPushButton(u"确定")

        self.layout.addLayout(self.name_layout)
        self.layout.addLayout(self.paixu_layout)
        self.layout.addLayout(self.icon_layout)
        self.layout.addWidget(self.introduce_label)
        self.layout.addWidget(self.introduce_edit)
        self.layout.addWidget(self.ok_button)

        self.ok_button.clicked.connect(self.accept)

        self.setLayout(self.layout)

    def browse(self):
        icon_path, _ = QFileDialog.getOpenFileName(self, u'选择图标', '', 'Images (*.png *.jpg *.bmp)')
        if icon_path:
            self.icon_edit.setText(icon_path)

    def get_color(self):
        color_dialog = QColorDialog(self)
        color_dialog.setCurrentColor(self.current_color)  # 设置颜色选择器的当前颜色
        if color_dialog.exec_() == QDialog.Accepted:
            color = color_dialog.currentColor()
            self.color_edit.setStyleSheet("background-color: %s" % color.name())
            self.current_color = color  # 更新当前颜色

    def get_current_color(self):
        return ','.join(map(str, (self.current_color.red(), self.current_color.green(), self.current_color.blue())))


class addDialog(QDialog):
    def __init__(self, parent=None):
        super(addDialog, self).__init__(parent)

        self.setWindowTitle(u"添加工具")

        self.layout = QVBoxLayout()

        self.name_label = QLabel(u"工具名：")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(u"请输入工具名称")
        self.name_layout = QHBoxLayout()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_edit)

        self.paixu_label = QLabel(u"排序：")
        self.paixu_edit = QLineEdit()
        self.paixu_edit.setPlaceholderText(u"请输入数值，数值越大越靠前")
        self.paixu_layout = QHBoxLayout()
        self.paixu_layout.addWidget(self.paixu_label)
        self.paixu_layout.addWidget(self.paixu_edit)
        # 设置paixu_edit只接受数字输入
        reg = QRegExp("[0-9]+$")  # 只接受数字
        pValidator = QRegExpValidator(self)
        pValidator.setRegExp(reg)
        self.paixu_edit.setValidator(pValidator)

        self.color_label = QLabel(u"按钮底色：")
        self.color_button = QPushButton(u"选择颜色")
        self.color_button.clicked.connect(self.get_color)

        self.paixu_layout = QHBoxLayout()
        self.paixu_layout.addWidget(self.paixu_label)
        self.paixu_layout.addWidget(self.paixu_edit)
        self.paixu_layout.addWidget(self.color_label)
        self.paixu_layout.addWidget(self.color_button)


        self.icon_label = QLabel(u"图标路径：")
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText(u"请选择或输入图标路径")
        self.browse_icon_button = QPushButton(u"选择图标")
        self.icon_layout = QHBoxLayout()
        self.icon_layout.addWidget(self.icon_label)
        self.icon_layout.addWidget(self.icon_edit)
        self.icon_layout.addWidget(self.browse_icon_button)

        self.path_label = QLabel(u"工具路径：")
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(u"路径或者cmds命令")
        self.browse_path_button = QPushButton(u"选择工具")
        self.path_layout = QHBoxLayout()
        self.path_layout.addWidget(self.path_label)
        self.path_layout.addWidget(self.path_edit)
        self.path_layout.addWidget(self.browse_path_button)

        self.introduce_label = QLabel(u"工具介绍：")
        self.introduce_edit = QTextEdit()
        self.introduce_edit.setPlaceholderText(u"用你能够理解的方式简洁输入工具介绍")

        self.ok_button = QPushButton(u"确定")

        self.layout.addLayout(self.name_layout)
        self.layout.addLayout(self.paixu_layout)
        self.layout.addLayout(self.icon_layout)
        self.layout.addLayout(self.path_layout)
        self.layout.addWidget(self.introduce_label)
        self.layout.addWidget(self.introduce_edit)
        self.layout.addWidget(self.ok_button)

        self.browse_icon_button.clicked.connect(self.browse_icon)
        self.browse_path_button.clicked.connect(self.browse_path)
        self.ok_button.clicked.connect(self.accept)

        self.setLayout(self.layout)

    def browse_icon(self):
        icon_path, _ = QFileDialog.getOpenFileName(self, u'选择图标', '', 'Images (*.png *.jpg *.bmp)')
        if icon_path:
            self.icon_edit.setText(icon_path)

    def browse_path(self):
        tool_path, _ = QFileDialog.getOpenFileName(self, u'选择工具', '', 'Python or Mel Files (*.py *.mel)')
        if tool_path:
            self.path_edit.setText(tool_path)

    def get_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_button.setStyleSheet("background-color: %s" % color.name())




class IconGridWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(IconGridWindow, self).__init__(parent)
        self.setWindowTitle(u"Cling_toolbox")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.transform_node_counter = 1
        self.export_window = ExportWindow()

        # 初始时，我们不显示这个窗口
        self.export_window.hide()
        self.switch_window = MayaUIWindow()
        # 初始时，我们不显示这个窗口
        self.switch_window.hide()

        workspace_control_name = "ToolboxWorkspaceControl"
        cmds.workspaceControl(workspace_control_name, e=True, minimumWidth=1, minimumHeight=1)

        if cmds.workspaceControl(workspace_control_name, q=1, exists=1):
            cmds.deleteUI(workspace_control_name)
        control = cmds.workspaceControl(
            workspace_control_name,
            label=u"Cling_toolbox",
            tabToControl=('AttributeEditor', -1),
            retain=False,
            initialWidth=450,
            initialHeight=300,
            minimumWidth=300,
            minimumHeight=200
        )

        qt_ctrl = omui.MQtUtil.findControl(control)
        widget = wrapInstance(int(qt_ctrl), QtWidgets.QWidget)
        layout = widget.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self)

        # 从JSON文件中读取配置信息
        json_file_path = 'D:/Cling_toolbox/json/Material_library.json'
        default_path = "D:\\Cling_toolbox\\Material_library"
        if not os.path.exists(json_file_path):
            self.MATERIAL_LIBRARY_PATH = default_path
        else:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.MATERIAL_LIBRARY_PATH = data.get('MATERIAL_LIBRARY_PATH', default_path)

        self.DEFAULT_MATERIAL_ICON = "D:\\Cling_toolbox\\Material_library\\Material.png"

        # 创建一个QTabWidget实例
        self.tab_widget = QtWidgets.QTabWidget(self)

        # 创建三个Page
        self.page1 = QtWidgets.QWidget()
        self.page2 = QtWidgets.QWidget()
        self.page3 = QtWidgets.QWidget()
        self.page4 = QtWidgets.QWidget()
        self.isPage3Loaded = False
        self.isPage4Loaded = False




        # 第1页
        self.myTreeWidget1 = QTreeWidget(self.page1)
        self.myTreeWidget1.setItemDelegate(BorderDelegate(self.myTreeWidget1))
        # 右键菜单
        self.myTreeWidget1.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.myTreeWidget1.customContextMenuRequested.connect(self.contextMenuEvent)

        self.myTreeWidget1.setStyleSheet("""

        QTreeView {
        selection-background-color: transparent;
        }

        QTreeView::item {
        margin-top: 1px;
        margin-bottom: 1px;
        padding: 3px; 
        }
        QTreeView::item:hover {
            background: rgb(1, 103, 149);
            color: rgb(246, 219, 104);
            border-radius: 6px;

        }

        QTreeView::item:selected {
            background: rgb(1, 103, 149);
            color: rgb(246, 219, 104);
            border-radius: 6px;
        }



}
        """)

        self.myTreeWidget1.setColumnCount(1)
        self.myTreeWidget1.setHeaderHidden(True)
        self.myTreeWidget1.setIndentation(10)  # 缩进
        self.myTreeWidget1.setFocusPolicy(Qt.NoFocus)
        self.myTreeWidget1.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.myTreeWidget1.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.search_line_edit11 = QtWidgets.QLineEdit(self.page1)
        self.search_line_edit11.setPlaceholderText(u"请输入搜索关键字")
        self.search_line_edit11.textChanged.connect(self.page1_search)
        # 创建一个垂直的 QSplitter
        splitter = QSplitter(Qt.Vertical)

        # 添加一个QTextEdit来显示工具介绍
        self.tool_intro_textedit = QTextEdit(self.page1)
        self.tool_intro_textedit.setReadOnly(True)
        # 创建 BorderDelegate 实例
        self.myBorderDelegate = BorderDelegate(self)
        # 将 delegate 设置为 QTreeWidget 的项目代理
        self.myTreeWidget1.setItemDelegate(self.myBorderDelegate)


        # 新的函数，用于显示工具介绍
        def show_introduction(item):
            # 获取工具介绍
            tool_intro = item.data(0, Qt.UserRole + 1)

            # 检查是否存在数据，如果没有则添加默认内容
            if not tool_intro:
                tool_intro = u"暂无介绍，如果你知道他的功能，你可以鼠标右键自定义添加介绍"

            # 更新工具介绍文本框的内容
            self.tool_intro_textedit.setText(tool_intro)

        def addGroupItem(tree_widget, group_name):
            item = QTreeWidgetItem(tree_widget)
            item.setText(0, group_name)
            item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            return item

        def execute_plugin(item):

            plugin_path = item.data(0, Qt.UserRole)  # 获取存储的插件路径
            exec_code = item.data(0, Qt.UserRole + 3)  # 获取存储的执行代码

            if plugin_path is None:
                return

            if exec_code is not None:
                # 如果存在执行代码，就执行它
                exec(exec_code, globals())
                return

            if plugin_path.startswith("cmds."):
                # 如果plugin_path以"cmds."开头，则认为它是一个命令，而不是一个文件路径
                from maya import cmds
                exec(plugin_path, globals())
            else:
                _, ext = os.path.splitext(plugin_path)
                if ext == '.py':
                    from maya import cmds
                    with open(plugin_path, encoding="utf-8") as file:
                        exec(file.read(), {'__file__': plugin_path, 'os': os})
                elif ext == '.mel':
                    import maya.mel as mel
                    with open(plugin_path, encoding="utf-8") as file:
                        mel.eval(file.read())
                else:
                    print("无效的插件文件类型")

        default_icon_path = "D:/Cling_toolbox/icons/icon.png"
        collect_file = "D:/Cling_toolbox/json/collect_plugin.json"
        if os.path.exists(collect_file):
            with open(collect_file, 'r', encoding='utf-8') as f:
                collect_plugins = json.load(f)
                if not collect_plugins:  # 判断是否无内容
                    collect_item = addGroupItem(self.myTreeWidget1, u'收藏')
                    collect_item.addChild(QTreeWidgetItem([u'无收藏']))
                else:

                    def get_sort_value(plugin_info):
                        try:
                            return -int(plugin_info.get("sort", 0))
                        except ValueError:
                            return 0  # 如果转换失败，返回 0
                    collect_plugins.sort(key=get_sort_value)
                    collect_item = addGroupItem(self.myTreeWidget1, u'收藏')
                    collect_item.setData(0, Qt.UserRole + 3, True)

                    for plugin_info in collect_plugins:
                        item = QTreeWidgetItem(collect_item)
                        if 'icon' in plugin_info and os.path.exists(plugin_info['icon']):
                            icon_path = plugin_info['icon']
                        else:
                            icon_path = default_icon_path
                        icon = QtGui.QIcon(icon_path)

                        item.setIcon(0, icon)
                        item.setText(0, plugin_info["name"])
                        item.setData(0, Qt.UserRole, plugin_info["path"])
                        item.setData(0, Qt.UserRole + 1, plugin_info.get("introduce", ""))
                        item.setData(0, Qt.UserRole + 2, True)
                        item.setData(0, Qt.UserRole + 3, plugin_info.get("exec_code", None))  # 存储执行代码

                    # 展开收藏项
                    self.myTreeWidget1.expandItem(collect_item)
        else:
            collect_item = addGroupItem(self.myTreeWidget1, u'收藏')
            collect_item.addChild(QTreeWidgetItem([u'无收藏']))
            # 展开收藏项
            self.myTreeWidget1.expandItem(collect_item)
        plugin_json = "D:/Cling_toolbox/json/plugin_info.json"
        with open(plugin_json, 'r', encoding='utf-8') as f:
            plugins = json.load(f)

        default_icon_path = "D:/Cling_toolbox/icons/icon.png"

        grouped_plugins = {}

        for plugin_info in plugins:
            if "group" in plugin_info:
                group_name = plugin_info["group"]
                if group_name not in grouped_plugins:
                    grouped_plugins[group_name] = []
                grouped_plugins[group_name].append(plugin_info)
            else:
                if "未分类" not in grouped_plugins:
                    grouped_plugins["未分类"] = []
                grouped_plugins["未分类"].append(plugin_info)

        for group_name, plugins_in_group in grouped_plugins.items():
            group_item = addGroupItem(self.myTreeWidget1, group_name)

            for plugin_info in plugins_in_group:
                item = QTreeWidgetItem(group_item)

                if 'icon' in plugin_info and os.path.exists(plugin_info['icon']):
                    icon_path = plugin_info['icon']
                else:
                    icon_path = default_icon_path

                icon = QtGui.QIcon(icon_path)
                item.setIcon(0, icon)
                item.setText(0, plugin_info["name"])
                item.setData(0, Qt.UserRole, plugin_info["path"])
                item.setData(0, Qt.UserRole + 1, plugin_info.get("introduce", ""))

        layout1 = QtWidgets.QVBoxLayout(self.page1)
        layout1.setSpacing(10)  # 设置控件间的间距为10像素
        layout1.addWidget(self.search_line_edit11)
        layout1.addWidget(self.myTreeWidget1)
        # 创建一个QLabel
        label = QLabel(u"工具介绍：")

        # 创建一个新的垂直布局
        layout = QVBoxLayout()

        # 将标签和文本框添加到布局中
        layout.addWidget(label)
        layout.addWidget(self.tool_intro_textedit)

        # 创建一个新的小部件来包含布局
        widget = QWidget()
        widget.setLayout(layout)

        # 将树形视图和工具介绍文本框添加到分割器中
        splitter.addWidget(self.myTreeWidget1)
        splitter.addWidget(widget)
        splitter.setSizes([450, 50])

        layout1.addWidget(splitter)  # 将分割器添加到布局中
        self.myTreeWidget1.itemClicked.connect(show_introduction)  # 当项目被点击时，执行show_introduction

        self.myTreeWidget1.itemDoubleClicked.connect(execute_plugin)

        # 第2页
        self.myListWidget2 = QtWidgets.QListWidget(self.page2)

        self.myListWidget2.setViewMode(QtWidgets.QListView.IconMode)
        self.myListWidget2.setIconSize(QtCore.QSize(60, 60))
        self.myListWidget2.setGridSize(QtCore.QSize(80, 80))
        self.myListWidget2.setSpacing(10)
        self.myListWidget2.setResizeMode(QtWidgets.QListView.Adjust)

        # 第2页功能

        # 设置右键菜单
        self.myListWidget2.setViewMode(QtWidgets.QListView.IconMode)
        self.myListWidget2.itemDoubleClicked.connect(self.import_ma)
        self.myListWidget2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.myListWidget2.customContextMenuRequested.connect(self.page2_show_context_menu)
        self.myListWidget2.setFocusPolicy(Qt.NoFocus)
        self.myListWidget2.setStyleSheet("""

                QListWidget {
                    selection-background-color: transparent;
                }

                QListWidget::item {
                    margin-top: 1px;
                    margin-bottom: 1px;
                    padding: 2px; 
                }

                QListWidget::item:hover {
                    background: rgb(1, 103, 149);
                    color: rgb(255, 255, 255);
                    border-radius: 6px;
                }

                QListWidget::item:selected {
                    background: rgb(1, 103, 149);
                    color: rgb(255, 255, 255);
                    border-radius: 6px;
                }

                """)


        # 创建搜索框
        self.search_line_edit2 = QtWidgets.QLineEdit(self.page2)
        self.search_line_edit2.setPlaceholderText(u"请输入搜索关键字")
        self.search_line_edit2.textChanged.connect(self.page2_search)

        # 创建搜索分类下拉菜单
        self.search_category_combo2 = QtWidgets.QComboBox(self.page2)
        self.search_category_combo2.addItem("All")
        self.search_category_combo2.addItems(["Metal", "Wood", "Rocks", "Ground", "Others"])
        self.search_category_combo2.currentIndexChanged.connect(self.page2_category_changed)

        # 创建图标大小滑动条
        self.icon_size_slider2 = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.page2)
        self.icon_size_slider2.setMinimum(60)
        self.icon_size_slider2.setMaximum(300)
        self.icon_size_slider2.setValue(60)
        self.icon_size_slider2.valueChanged.connect(self.page2_change_icon_size)

        # 创建水平布局并添加元素
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.search_line_edit2)
        hlayout.addWidget(self.search_category_combo2)  # 添加到布局
        hlayout.addWidget(self.icon_size_slider2)

        # 创建垂直布局
        layout = QtWidgets.QVBoxLayout(self.page2)
        layout.addLayout(hlayout)
        layout.addWidget(self.myListWidget2)

        # 添加新的按钮
        self.run_script_button = QtWidgets.QPushButton(u'导人到材质库', self.page2)
        layout.addWidget(self.run_script_button)

        # 点击按钮时执行的函数
        def run_script():
            exp_material_folder = r'D:/Cling_toolbox/plug-in/material'
            if exp_material_folder not in sys.path:
                sys.path.append(exp_material_folder)
            from exp_material import MaterialExporter, maya_main_window

            script_path = "D:/Cling_toolbox/plug-in/material/exp_material.py"
            if os.path.exists(script_path):
                app = QtWidgets.QApplication.instance()
                if not app:
                    app = QtWidgets.QApplication([])
                # 窗口的唯一名称
                window_name = "MaterialExporter"
                # 如果窗口已存在，则删除
                if cmds.window(window_name, exists=True):
                    cmds.deleteUI(window_name, window=True)
                MaterialExporter = MaterialExporter()
                MaterialExporter.setObjectName(window_name)  # 给窗口设置唯一名称
                MaterialExporter.show()

                app.exec_()
            else:
                print("Script file does not exist: ", script_path)

        self.run_script_button.clicked.connect(run_script)

        # 添加新的按钮2
        self.cj_material = QtWidgets.QPushButton(u'创建材质球', self.page2)

        # 按钮2点击函数
        def on_cj_material_clicked():
            # 添加模块的查找路径
            module_folder = r'D:/Cling_toolbox/plug-in/material/template'
            if module_folder not in sys.path:
                sys.path.append(module_folder)

            import material_dialog1
            reload(material_dialog1)  # 在Python 3中使用importlib.reload()

            # 从模块中获取CreateMaterialWindow函数并执行
            window = material_dialog1.CreateMaterialWindow()

        self.cj_material.clicked.connect(on_cj_material_clicked)  # 将按钮点击事件连接到函数

        # 创建水平布局并添加元素
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.run_script_button)  # 添加新按钮1
        button_layout.addWidget(self.cj_material)  # 添加新按钮2

        layout.addLayout(button_layout)  # 将包含两个按钮的水平布局添加到垂直布局中

        # 创建刷新按钮
        self.page2_refresh_button = QtWidgets.QPushButton(u'刷新', self.page2)
        layout.addWidget(self.page2_refresh_button)

        # 先添加按钮到布局，然后再初始化和刷新列表
        self.init_material_library()
        self.page2_refresh_button.clicked.connect(self.page2_refresh_list)

        # 第三部分功能搬到“loadPage3Content”函数中，用作点击第三页时才加载该部分，解决资产量过大初次运行速度会变慢
        # 用“on_tab_changed”函数控制点击多少页时启动

        self.page4_layout = QtWidgets.QVBoxLayout(self.page4)
        self.groupBox_5 = QtWidgets.QGroupBox(u"帮助文档")
        self.tree = QtWidgets.QTreeWidget()
        self.browser = QtWidgets.QTextBrowser()
        self.page4_layout.addWidget(self.groupBox_5)
        self.groupBox_5.setLayout(QtWidgets.QVBoxLayout())
        self.groupBox_5.layout().addWidget(self.browser)
        self.groupBox_5.layout().addWidget(self.tree)

        self.load_thread = LoadJsonThread()
        self.load_thread.load_finished.connect(self.on_load_finished)
        # self.load_thread.start()
        # 初始时不加载第四页https相关内容，而是等到点击第四页时才加载
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.groupBox_6 = QtWidgets.QGroupBox(u"作者信息")
        self.textBrowser_2 = QtWidgets.QTextBrowser()
        self.page4_layout.addWidget(self.groupBox_6)
        self.groupBox_6.setLayout(QtWidgets.QVBoxLayout())
        self.groupBox_6.layout().addWidget(self.textBrowser_2)
        self.groupBox_6.setFixedHeight(200)

        # 设置TextBrowser以在外部浏览器中打开链接
        self.textBrowser_2.setOpenExternalLinks(True)

        html_zz = u"""
                            <!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">
                            <html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">
                            p, li { white-space: pre-wrap; }
                            </style></head><body style=\" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;\">
                            <h3 style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">作者：cling</h3>
                            <h3 style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">微信：clingkaka</h3>
                            <h3 style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">工具官网：<a href=\"https://www.cgfml.com/195275.html\"><span style=\" text-decoration: underline; color:#ff8000;\">https://www.cgfml.com/195275.html</span></a></h3>
                            <h3 style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">模型下载：<a href=\"https://www.cgfml.com\"><span style=\" text-decoration: underline; color:#ff8000;\">www.cgfml.com</span></a></h3>
                            <h3 style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">AI聊天绘画：<a href=\"https://ai.cgfml.com\"><span style=\" text-decoration: underline; color:#ff8000;\">ai.cgfml.com</span></a></h3>
                            </body></html>
                            """

        # 设置作者内容
        self.textBrowser_2.setHtml(html_zz)

        # 添加到Tab Widget中
        self.tab_widget.addTab(self.page1, u'实用工具')
        self.tab_widget.addTab(self.page2, u'材质库')
        self.tab_widget.addTab(self.page3, u'资产库')
        self.tab_widget.addTab(self.page4, u'帮助')



        # 设置Tab Widget为当前窗口的central widget
        self.setCentralWidget(self.tab_widget)


    # ——————第一页搜索功能开始——————


    def page1_search(self, text):
        for i in range(self.myTreeWidget1.topLevelItemCount()):
            group_item = self.myTreeWidget1.topLevelItem(i)
            for j in range(group_item.childCount()):
                item = group_item.child(j)
                introduce = item.data(0, Qt.UserRole + 1) if item.data(0, Qt.UserRole + 1) else ""
                if text.lower() in item.text(0).lower() or text.lower() in introduce.lower():
                    self.expand_parents(item)
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def expand_parents(self, item):
        parent = item.parent()
        while parent:
            parent.setExpanded(True)
            parent = parent.parent()

    # ——————第一页搜索功能结束——————

    def contextMenuEvent(self, position):
        contextMenu = QMenu(self)
        collectAct = QAction(u'加入收藏', self)
        # 创建一个隔离线，并添加文字说明
        separator = QAction(u'以下操作仅加入收藏后生效', self)
        separator.setDisabled(True)

        customizeAct = QAction(u'自定义修改', self)
        addAct = QAction(u'添加工具', self)  # 新的操作
        customizeAct = QAction(u'自定义修改', self)
        deleteAct = QAction(u'删除该工具', self)  # 新的操作
        refreshAct = QAction(u'刷新', self)

        contextMenu.addAction(collectAct)
        # 添加隔离线到菜单中
        contextMenu.addAction(separator)

        contextMenu.addAction(addAct)
        contextMenu.addAction(customizeAct)
        contextMenu.addAction(deleteAct)
        contextMenu.addAction(refreshAct)

        collectAct.triggered.connect(self.add_to_collect)

        addAct.triggered.connect(self.add_new_item)
        customizeAct.triggered.connect(self.customize_json)
        deleteAct.triggered.connect(self.delete_item)
        refreshAct.triggered.connect(self.collectrefresh)

        contextMenu.exec_(self.myTreeWidget1.viewport().mapToGlobal(position))

    def add_new_item(self):
        # 创建一个对话框让用户输入新项目的信息
        dialog = addDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_field = dialog.name_edit.text().strip()
            icon_path = dialog.icon_edit.text().strip()
            introduce = dialog.introduce_edit.toPlainText().strip()
            path_path = dialog.path_edit.text().strip()
            paixu_sz = dialog.paixu_edit.text().strip()
            if new_field or icon_path or introduce or path_path or paixu_sz:
                # 创建一个新的插件信息
                plugin_info = {
                    "name": new_field,
                    "icon": icon_path,
                    "introduce": introduce,
                    "path": path_path,
                    "sort": paixu_sz
                }
                # 将新的插件信息保存到json文件中
                collect_file = "D:/Cling_toolbox/json/collect_plugin.json"
                if os.path.exists(collect_file):
                    with open(collect_file, 'r', encoding='utf-8') as f:
                        collect_plugins = json.load(f)
                else:
                    collect_plugins = []
                collect_plugins.append(plugin_info)
                with open(collect_file, 'w') as f:
                    json.dump(collect_plugins, f, indent=4)
                # 刷新树形控件
                self.update_tree_widget()

    def delete_item(self):
        # 获取选定的项目
        selected_items = self.myTreeWidget1.selectedItems()
        if selected_items:
            item = selected_items[0]
            plugin_name = item.text(0)
            plugin_path = item.data(0, Qt.UserRole)
            # 从json文件中删除该项目的信息
            collect_file = "D:/Cling_toolbox/json/collect_plugin.json"
            if os.path.exists(collect_file):
                with open(collect_file, 'r', encoding='utf-8') as f:
                    collect_plugins = json.load(f)
                # 找到要删除的插件信息
                for i, plugin_info in enumerate(collect_plugins):
                    if plugin_info['name'] == plugin_name and plugin_info['path'] == plugin_path:
                        del collect_plugins[i]
                        break
                # 保存修改后的json文件
                with open(collect_file, 'w') as f:
                    json.dump(collect_plugins, f, indent=4)
                # 刷新树形控件
                self.update_tree_widget()

    def customize_json(self):
        selected_items = self.myTreeWidget1.selectedItems()
        if selected_items:
            item = selected_items[0]
            field_info = self.get_field_info(item.text(0))  # 获取当前选中项的字段信息
            dialog = CustomDialog(parent=self, field_info=field_info)
            if dialog.exec_() == QDialog.Accepted:
                new_field = dialog.name_edit.text().strip()
                paixu_sz = dialog.paixu_edit.text().strip()
                icon_path = dialog.icon_edit.text().strip()
                introduce = dialog.introduce_edit.toPlainText().strip()
                color = dialog.get_current_color()  # 获取当前颜色值
                if new_field or icon_path or introduce or paixu_sz or color:
                    self.update_json_field(item.text(0), new_field, icon_path, introduce, paixu_sz, color)

    def get_field_info(self, old_field):
        collect_file = "D:/Cling_toolbox/json/collect_plugin.json"
        if os.path.exists(collect_file):
            with open(collect_file, 'r', encoding='utf-8') as f:
                collect_plugins = json.load(f)
            for plugin_info in collect_plugins:
                if plugin_info['name'] == old_field:
                    return plugin_info  # 返回匹配的插件信息
        return None

    def update_json_field(self, plugin_name, new_field, icon_path, introduce, paixu_sz, color):
        collect_file = "D:/Cling_toolbox/json/collect_plugin.json"
        if os.path.exists(collect_file):
            with open(collect_file, 'r', encoding='utf-8') as f:
                collect_plugins = json.load(f)
            for plugin_info in collect_plugins:
                if plugin_info['name'] == plugin_name:
                    if new_field:
                        plugin_info['name'] = new_field
                    if icon_path:
                        plugin_info['icon'] = icon_path
                    if introduce:
                        plugin_info['introduce'] = introduce
                    if paixu_sz:
                        plugin_info['sort'] = paixu_sz
                    if color:
                        # 如果 color 字段不存在，就添加一个新的 color 字段
                        if 'color' not in plugin_info:
                            plugin_info['color'] = color
                        else:
                            plugin_info['color'] = color
                    break
            with open(collect_file, 'w') as f:
                json.dump(collect_plugins, f, indent=4)
            self.update_tree_widget()

    def collectrefresh(self):  # 新增的槽函数
        # 这里需要重新获取json的信息并更新到myTreeWidget1中
        self.update_tree_widget()

    def update_tree_widget(self):
        # 在这个函数中，你需要重新获取json的信息并更新到myTreeWidget1中
        default_icon_path = "D:/Cling_toolbox/icons/icon.png"
        collect_file = "D:/Cling_toolbox/json/collect_plugin.json"
        if os.path.exists(collect_file):
            with open(collect_file, 'r', encoding='utf-8') as f:
                collect_plugins = json.load(f)
                # 找到名为"收藏"的子级
                collect_item = None
                for i in range(self.myTreeWidget1.topLevelItemCount()):
                    if self.myTreeWidget1.topLevelItem(i).text(0) == u'收藏':
                        collect_item = self.myTreeWidget1.topLevelItem(i)
                        break
                if collect_item is None:
                    collect_item = addGroupItem(self.myTreeWidget1, u'收藏')
                # 清空该子级的所有子项
                collect_item.takeChildren()
                if not collect_plugins:  # 判断是否无内容
                    collect_item.addChild(QTreeWidgetItem([u'无收藏']))
                else:
                    # 处理收藏的插件
                    def get_sort_value(plugin_info):
                        try:
                            return -int(plugin_info.get("sort", 0))
                        except ValueError:
                            return 0  # 如果转换失败，返回 0

                    collect_plugins.sort(key=get_sort_value)
                    for plugin_info in collect_plugins:
                        item = QTreeWidgetItem(collect_item)
                        if 'icon' in plugin_info and os.path.exists(plugin_info['icon']):
                            icon_path = plugin_info['icon']
                        else:
                            icon_path = default_icon_path
                        icon = QtGui.QIcon(icon_path)
                        item.setIcon(0, icon)
                        item.setText(0, plugin_info["name"])
                        item.setData(0, Qt.UserRole, plugin_info["path"])
                        item.setData(0, Qt.UserRole + 1, plugin_info.get("introduce", ""))
                        # 如果 color 字段存在，将颜色信息保存在项的数据中
                        if 'color' in plugin_info:
                            item.setData(0, Qt.UserRole + 2, plugin_info.get("color"))

        else:
            collect_item = addGroupItem(self.myTreeWidget1, u'收藏')
            collect_item.addChild(QTreeWidgetItem([u'无收藏']))
        self.myBorderDelegate.update_color_map()
        self.myTreeWidget1.update()  # 强制更新部件

    def add_to_collect(self):
        selected_items = self.myTreeWidget1.selectedItems()
        if selected_items:
            item = selected_items[0]
            # 如果选中的项是父级（即有子节点），则不做添加
            if item.childCount() > 0:
                return
            plugin_info = {
                "name": item.text(0),
                "path": item.data(0, Qt.UserRole),
                "introduce": item.data(0, Qt.UserRole + 1),
                "icon": item.icon(0).name() if item.icon(0) else None
            }
            collect_file = "D:/Cling_toolbox/json/collect_plugin.json"
            if os.path.exists(collect_file):
                with open(collect_file, 'r', encoding='utf-8') as f:
                    collect_plugins = json.load(f)
            else:
                collect_plugins = []

            # 检查是否已经存在
            if not any(p['name'] == plugin_info['name'] and p['path'] == plugin_info['path'] for p in collect_plugins):
                collect_plugins.append(plugin_info)
                with open(collect_file, 'w') as f:
                    json.dump(collect_plugins, f, indent=4)

            self.update_tree_widget()

    # ——————第一页右键功能结束——————

    # 第二部分函数

    def import_ma(self, item):
        name = item.text()
        if name.endswith('.ma'):
            name = name[:-3]  # 移除".ma"后缀
        print("Material name: %s" % name)  # 打印出名字以供检查

        # 获取选中的图标项的名称
        selected_item = self.myListWidget2.currentItem()
        if selected_item:
            icon_name = selected_item.text()
            if icon_name:
                # 在文件列表中匹配路径
                icon_path = next((path for path in self.ma_files if icon_name in path), None)
                if icon_path:
                    print("Icon Path: %s" % icon_path)

                    # 导入.ma文件
                    cmds.file(icon_path, i=True)

                    # 尝试使用.ma文件的名称获取新导入的shader
                    new_shader = cmds.ls(name, materials=True)

                    if new_shader:
                        new_shader = new_shader[0]

                        # 获取当前选择的模型
                        selected_objects = cmds.ls(selection=True)

                        # 创建新的shadingEngine
                        shading_engine = cmds.sets(renderable=True, noSurfaceShader=True, empty=True,
                                                   name=new_shader + 'SG')

                        # 连接新的shader和shadingEngine
                        cmds.defaultNavigation(connectToExisting=True, source=new_shader, destination=shading_engine)
                        cmds.connectAttr(new_shader + '.outColor', shading_engine + '.surfaceShader', force=True)

                        # 使用 MEL 命令将新的shader应用到当前选择的模型上
                        for obj in selected_objects:
                            mel.eval('select -r ' + obj + ' ;')
                            mel.eval('hyperShade -assign ' + new_shader + ' ;')
                else:
                    print("Could not find icon path for the selected item.")
            else:
                print("No item selected.")

    def page2_show_context_menu(self, position):
        menu = QMenu(self)
        view_action = QAction(u'查看大图', self)
        open_action = QAction(u'打开文件所在位置', self)
        menu.addAction(view_action)
        menu.addAction(open_action)

        view_action.triggered.connect(self.view_image)
        open_action.triggered.connect(self.open_location)

        menu.exec_(self.myListWidget2.viewport().mapToGlobal(position))

    def page2_search(self, text):
        for i in range(self.myListWidget2.count()):
            item = self.myListWidget2.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def get_files_in_category(self, category):
        category_path = os.path.join(self.MATERIAL_LIBRARY_PATH, category)

        if os.path.exists(category_path):
            ma_files = [os.path.join(category_path, f) for f in os.listdir(category_path) if f.endswith('.ma')]
            return ma_files
        else:
            return []

    def page2_category_changed(self, index):
        category = self.search_category_combo2.currentText().encode('utf-8')

        if category == "All":
            self.ma_files, self.png_files = self.get_files(self.MATERIAL_LIBRARY_PATH)
        else:
            category_folder = category.decode('utf-8')
            self.ma_files = self.get_files_in_category(category_folder)

            self.png_files = []
            for ma_file in self.ma_files:
                png_file = ma_file.replace('.ma', '.png')
                if os.path.exists(png_file):
                    self.png_files.append(png_file)
                else:
                    self.png_files.append(self.DEFAULT_MATERIAL_ICON)

        self.add_items_to_list()

    def init_material_library(self):
        self.ma_files, self.png_files = self.get_files(self.MATERIAL_LIBRARY_PATH)
        self.add_items_to_list()

    def get_files(self, path):
        ma_files = []
        png_files = []

        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith('.ma'):
                    ma_files.append(os.path.join(root, filename))
                    png_file = os.path.join(root, filename.replace('.ma', '.png'))
                    if os.path.exists(png_file):
                        png_files.append(png_file)
                    else:
                        png_files.append(self.DEFAULT_MATERIAL_ICON)

        return ma_files, png_files

    def add_items_to_list(self):
        self.myListWidget2.clear()
        for i in range(len(self.ma_files)):
            item = QListWidgetItem(QIcon(self.png_files[i]), os.path.basename(self.ma_files[i]))
            self.myListWidget2.addItem(item)

    def load_current_category(self):
        category = self.search_category_combo2.currentText()

        if category == "All":
            self.ma_files, self.png_files = self.get_files(self.MATERIAL_LIBRARY_PATH)
        else:
            # 在这里不需要对category进行编码或解码
            self.ma_files = self.get_files_in_category(self.MATERIAL_LIBRARY_PATH, category)

            # 更新self.png_files, 如果对应的图标不存在则使用默认图标
            self.png_files = []
            for ma_file in self.ma_files:
                png_file = ma_file.replace('.ma', '.png')
                if os.path.exists(png_file):
                    self.png_files.append(png_file)
                else:
                    self.png_files.append(self.DEFAULT_MATERIAL_ICON)

        # 更新图标列表
        self.add_items_to_list()

    def page2_refresh_list(self):
        self.load_current_category()

    def page2_show_context_menu(self, position):
        menu = QMenu(self)
        view_action = QAction(u'查看大图', self)
        open_action = QAction(u'打开文件所在位置', self)
        menu.addAction(view_action)
        menu.addAction(open_action)

        view_action.triggered.connect(self.view_image)
        open_action.triggered.connect(self.open_location)

        menu.exec_(self.myListWidget2.viewport().mapToGlobal(position))

    def view_image(self):
        current_item = self.myListWidget2.currentItem()
        if current_item:
            image_path = next(
                (png for png, ma in zip(self.png_files, self.ma_files) if os.path.basename(ma) == current_item.text()),
                None)
            if image_path:
                # 创建一个新的窗口来显示大图
                self.show_image_dialog(image_path)
            else:
                print('No corresponding image found.')

    def show_image_dialog(self, image_path):
        self.img_win = QtWidgets.QDialog(self)
        self.img_win.setWindowTitle(os.path.basename(image_path))
        layout = QtWidgets.QVBoxLayout(self.img_win)
        label = QtWidgets.QLabel(self.img_win)
        pixmap = QtGui.QPixmap(image_path)
        label.setPixmap(pixmap.scaled(1024, 1024, QtCore.Qt.KeepAspectRatio))
        layout.addWidget(label)
        self.img_win.setLayout(layout)
        self.img_win.show()

    def open_location(self):
        current_item = self.myListWidget2.currentItem()
        if current_item:
            ma_file = next((ma for ma in self.ma_files if os.path.basename(ma) == current_item.text()), None)
            if ma_file:
                folder_path = os.path.dirname(ma_file)
                self.open_folder_location(folder_path)
            else:
                print('No corresponding .ma file found.')

    def open_folder_location(self, folder_path):
        os.startfile(folder_path)

    def page2_change_icon_size(self, value):
        self.myListWidget2.setIconSize(QtCore.QSize(value, value))
        self.myListWidget2.setGridSize(QtCore.QSize(value + 20, value + 20))

    # 第三部分函数

    def loadPage3Content(self):
        # 第3页



        self.myListWidget = QtWidgets.QListWidget(self.page3)

        self.myListWidget.setViewMode(QtWidgets.QListView.IconMode)
        self.myListWidget.setIconSize(QtCore.QSize(60, 60))
        self.myListWidget.setGridSize(QtCore.QSize(80, 80))
        self.myListWidget.setSpacing(10)
        self.myListWidget.setResizeMode(QtWidgets.QListView.Adjust)
        self.myListWidget.setFocusPolicy(Qt.NoFocus)

        self.myListWidget.setStyleSheet("""

                QListWidget {
                    selection-background-color: transparent;
                }

                QListWidget::item {
                    margin-top: 1px;
                    margin-bottom: 1px;
                    padding: 2px; 
                }

                QListWidget::item:hover {
                    background: rgb(1, 103, 149);
                    color: rgb(255, 255, 255);
                    border-radius: 6px;
                }

                QListWidget::item:selected {
                    background: rgb(1, 103, 149);
                    color: rgb(255, 255, 255);
                    border-radius: 6px;
                }

                """)

        # 第3页功能


        # 设置右键菜单
        self.myListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.myListWidget.customContextMenuRequested.connect(self.show_context_menu)

        # 创建按钮USD模式和GPU+ASS模式
        button_usd = QtWidgets.QPushButton("USD模式", self.page3)
        button_gpu_ass = QtWidgets.QPushButton("GPU+ASS模式", self.page3)

        # 设置按钮的初始可点击状态
        button_usd.setCheckable(True)
        button_gpu_ass.setCheckable(True)

        # 设置按钮的点击事件，确保两个按钮不会同时被选中
        def toggle_buttons(button, other_button):
            if button.isChecked():
                other_button.setChecked(False)
            button.setChecked(True)

        button_usd.clicked.connect(lambda: toggle_buttons(button_usd, button_gpu_ass))
        button_gpu_ass.clicked.connect(lambda: toggle_buttons(button_gpu_ass, button_usd))

        # 创建一个新的水平布局来放置这两个按钮
        hlayout_buttons_top = QtWidgets.QHBoxLayout()
        hlayout_buttons_top.addWidget(button_usd)
        hlayout_buttons_top.addWidget(button_gpu_ass)

        # 设置USD模式按钮的初始状态为选中
        button_usd.setChecked(True)
        button_gpu_ass.setChecked(False)


        # 创建下拉菜单
        self.menu1 = QtWidgets.QComboBox(self.page3)
        self.menu2 = QtWidgets.QComboBox(self.page3)

        # 创建搜索框
        self.search_line_edit = QtWidgets.QLineEdit(self.page3)
        self.search_line_edit.setPlaceholderText(u"请输入搜索关键字")
        self.search_line_edit.textChanged.connect(self.search)

        # 创建搜索分类下拉菜单
        self.search_category_combo = QtWidgets.QComboBox(self.page3)

        self.search_category_combo.addItem("All")
        self.search_category_combo.addItems(
            ["Tree", "Grass", "Flower", "Bush", "Rock", "Building", "Terrain", "Water", "Other", "Assembly"])
        self.search_category_combo.currentIndexChanged.connect(self.category_changed)

        # 创建图标大小滑动条
        self.icon_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.page3)
        self.icon_size_slider.setMinimum(60)
        self.icon_size_slider.setMaximum(300)
        self.icon_size_slider.setValue(60)
        self.icon_size_slider.valueChanged.connect(self.change_icon_size)

        # 创建水平布局并添加元素
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.menu1)
        hlayout.addWidget(self.menu2)
        hlayout.addWidget(self.search_line_edit)
        hlayout.addWidget(self.search_category_combo)  # 添加到布局
        hlayout.addWidget(self.icon_size_slider)

        # 创建加入刷新按钮的垂直布局
        layout = QtWidgets.QVBoxLayout(self.page3)
        layout.insertLayout(0, hlayout_buttons_top)
        layout.addLayout(hlayout)
        layout.addWidget(self.myListWidget)


        # 在创建button1和button2，并将它们放到一个新的水平布局之后
        button1 = QtWidgets.QPushButton(u'+显示资产导出窗口', self.page3)
        button1.clicked.connect(lambda: self.toggle_new_area1(button1, button3))

        # 创建新的区域并设为默认不可见
        self.new_area1 = QtWidgets.QFrame(self.page3)
        self.new_area1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.new_area1.setVisible(False)  # 默认隐藏

        # 创建新区域的内容，这里只是一个例子，你可以根据需要添加其他内容
        new_area_layout1 = QtWidgets.QVBoxLayout(self.new_area1)
        new_area_label1 = QtWidgets.QLabel(U"导入资产到库")
        new_area_layout1.addWidget(new_area_label1)

        # 创建一个QScrollArea并设置其widget为new_area1
        self.scroll1 = QtWidgets.QScrollArea()
        self.scroll1.setWidget(self.new_area1)
        self.scroll1.setWidgetResizable(True)
        self.scroll1.setVisible(False)
        self.scroll1.setFixedHeight(200)
        self.scroll1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
       # self.scroll1.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        button3 = QtWidgets.QPushButton(u'+显示多功能切换', self.page3)
        button3.clicked.connect(lambda: self.toggle_new_area2(button3, button1))

        # 创建另一个新的区域并设为默认不可见
        self.new_area2 = QtWidgets.QFrame(self.page3)
        self.new_area2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.new_area2.setVisible(False)  # 默认隐藏

        # 创建新区域的内容，这里只是一个例子，你可以根据需要添加其他内容
        new_area_layout2 = QtWidgets.QVBoxLayout(self.new_area2)
        new_area_label2 = QtWidgets.QLabel(U"多功能切换")
        new_area_layout2.addWidget(new_area_label2)

        # 创建一个QScrollArea并设置其widget为new_area2
        self.scroll2 = QtWidgets.QScrollArea()
        self.scroll2.setWidget(self.new_area2)
        self.scroll2.setWidgetResizable(True)
        self.scroll2.setVisible(False)
        self.scroll2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.scroll2.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)



        hlayout_buttons = QtWidgets.QHBoxLayout()  # 新的水平布局
        hlayout_buttons.addWidget(button1)
        hlayout_buttons.addWidget(button3)

        # 将新的水平布局和新区域添加到垂直布局
        layout.addWidget(self.scroll1)  # 添加新区域到布局
        layout.addWidget(self.scroll2)
        layout.addLayout(hlayout_buttons)

        # 添加第二个新区域到布局

        # 再创建刷新按钮并添加到垂直布局
        self.refresh_button = QtWidgets.QPushButton(u'刷新', self.page3)
        layout.addWidget(self.refresh_button)

        # 检查文件是否存在
        if not os.path.exists("D:/Cling_toolbox/json/gpu_route.json"):
            # 文件不存在则创建并写入默认内容
            data = {'new_json_path': 'D:/Cling_toolbox/json/GPU_project.json'}
            with open("D:/Cling_toolbox/json/gpu_route.json", 'w', encoding='utf-8') as f:
                json.dump(data, f)
        else:
            # 文件存在则直接读取
            with open("D:/Cling_toolbox/json/gpu_route.json", 'r', encoding='utf-8') as f:
                data = json.load(f)

        # 获取新的json文件路径
        new_json_path = data.get('new_json_path')
        if not new_json_path or not os.path.isfile(new_json_path):
            raise ValueError(u"无法找到新的json文件或路径不正确")

        try:
            # 尝试从新的json文件中加载数据
            with open(new_json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except IOError:
            print(u"文件未找到，请添加资产目录。")
        except ValueError:
            print(u"无法解析JSON文件，请检查资产目录中的文件。")

        # 对 self.data 的键（key）进行字母顺序排序
        sorted_keys = sorted(self.data.keys()) if self.data else [u'请在菜单中添加资产目录']

        # 填充下拉菜单
        self.menu1.addItems(sorted_keys)

        if self.data:
            self.menu2.addItems(sorted(self.data[self.menu1.currentText()].keys()))
        else:
            self.menu2.addItems([u'请在菜单中添加资产目录'])

        # 连接信号和槽
        self.menu1.currentIndexChanged.connect(self.on_menu1_changed)
        self.menu2.currentIndexChanged.connect(self.on_menu2_changed)
        # 连接双击事件
        self.myListWidget.itemDoubleClicked.connect(self.on_item_double_clicked)
        # 连接刷新按钮
        self.refresh_button.clicked.connect(self.page3_refresh_list)
        # 手动触发 menu1 下拉菜单选项改变的事件
        self.menu1.currentIndexChanged.emit(self.menu1.currentIndex())

    # 在类的其他部分添加新的插槽函数
    # 在类的其他部分添加新的插槽函数
    def toggle_new_area1(self, button1=None, button3=None):
        if self.new_area1.isVisible():
            self.new_area1.setVisible(False)
            self.scroll1.setVisible(False)
            # 移除 ExportWindow
            self.new_area1.layout().removeWidget(self.export_window)
            self.export_window.hide()
            if button1:
                button1.setText(u'+显示资产导出窗口')
        else:
            self.new_area1.setVisible(True)
            self.scroll1.setVisible(True)
            if self.new_area2.isVisible():
                self.new_area2.setVisible(False)
                self.scroll2.setVisible(False)
                # 移除另一个窗口
                self.new_area2.layout().removeWidget(self.switch_window)
                self.switch_window.hide()
                if button3:
                    button3.setText(u'+显示多功能切换')
            # 添加 ExportWindow
            self.new_area1.layout().addWidget(self.export_window)
            # 在这里获取 menu1 和 menu2 的当前选项，并设置到 ExportWindow 中
            current_project = self.menu1.currentText()
            current_scene = self.menu2.currentText()
            self.export_window.set_project_and_scene(current_project, current_scene)
            self.export_window.show()
            if button1:
                button1.setText(u'-关闭资产导出窗口')

    def toggle_new_area2(self, button3, button1):
        if self.new_area2.isVisible():
            self.new_area2.setVisible(False)
            self.scroll2.setVisible(False)
            # 移除 ExportWindow
            self.new_area2.layout().removeWidget(self.switch_window)
            self.switch_window.hide()
            button3.setText(u'+显示多功能切换')
        else:
            self.new_area2.setVisible(True)
            self.scroll2.setVisible(True)
            self.new_area1.setVisible(False)
            self.scroll1.setVisible(False)
            # 添加 ExportWindow
            self.new_area2.layout().addWidget(self.switch_window)
            self.switch_window.show()
            button3.setText(u'-关闭多功能切换')
            button1.setText(u'+显示资产导出窗口')  # 关闭其他区域时，改变其他按钮的文本

    def GPU_convert(self):

        GPU_switch_folder = r'D:/Cling_toolbox/plug-in/GPUcache'
        if GPU_switch_folder not in sys.path:
            sys.path.append(GPU_switch_folder)
        import GPU_switch_A
        from GPU_switch_A import MayaUIWindow
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication([])

        # 窗口的唯一名称
        window_name = "MayaUIWindow"

        # 如果窗口已存在，则删除
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)

        export_window = MayaUIWindow()
        export_window.setObjectName(window_name)  # 给窗口设置唯一名称
        export_window.show()

        export_window.showUI()
        app.exec_()

    def show_context_menu(self, position):
        menu = QtWidgets.QMenu()
        reference_action = QtWidgets.QAction(u'引用ma文件', self)
        import_action = QtWidgets.QAction(u'导入ma文件', self)
        open_folder_action = QtWidgets.QAction(u'打开所在文件夹', self)
        view_large_image_action = QtWidgets.QAction(u'查看大图', self)
        fill_export_info_action = QtWidgets.QAction(u'重新导出', self)

        reference_action.triggered.connect(self.reference_ma_file)
        import_action.triggered.connect(self.import_ma_file)
        open_folder_action.triggered.connect(self.open_folder)
        view_large_image_action.triggered.connect(self.view_large_image)
        fill_export_info_action.triggered.connect(self.fill_export_information)

        menu.addAction(reference_action)
        menu.addAction(import_action)
        menu.addAction(open_folder_action)
        menu.addAction(view_large_image_action)
        menu.addAction(fill_export_info_action)

        menu.exec_(self.myListWidget.mapToGlobal(position))

    def fill_export_information(self):
        item = self.myListWidget.currentItem()
        if item:
            icon_name = item.text()
            parts = icon_name.split('_')
            if len(parts) >= 3:
                # 检查最后一个部分是否为 'High' 或 'Low'
                if parts[-1] in ["High", "Low"]:
                    self.export_window.cmb_quality.setCurrentText(parts[-1])
                else:
                    # 如果不是 'High' 或 'Low'，则设置为 'Custom' 并在 txt_custom_quality 中显示
                    self.export_window.cmb_quality.setCurrentText("Custom")
                    self.export_window.txt_custom_quality.setText(parts[-1])

                self.export_window.txt_name.setText(parts[-2])
                self.export_window.cmb_category.setCurrentText(parts[-3])

            current_project = self.menu1.currentText()
            current_scene = self.menu2.currentText()
            self.export_window.set_project_and_scene(current_project, current_scene)

            # 只有当 new_area1 是隐藏的时候才调用 toggle_new_area1 函数
            if not self.new_area1.isVisible():
                self.toggle_new_area1()

    def reference_ma_file(self):
        # 获取当前选择的项
        item = self.myListWidget.currentItem()
        if item:
            full_path = item.data(QtCore.Qt.UserRole)
            base_name = os.path.splitext(os.path.basename(full_path))[0]
            ma_file = os.path.join(os.path.dirname(full_path), '{}.ma'.format(base_name))
            # 如果存在同名 ma 文件，则引用该 ma 文件
            if os.path.exists(ma_file):
                ma_file = os.path.normpath(ma_file).replace("\\", "/")
                mel.eval('file -reference -namespace "{}" "{}";'.format(base_name, ma_file))

    def import_ma_file(self):
        # 获取当前选择的项
        item = self.myListWidget.currentItem()
        if item:
            full_path = item.data(QtCore.Qt.UserRole)
            base_name = os.path.splitext(os.path.basename(full_path))[0]
            ma_file = os.path.join(os.path.dirname(full_path), '{}.ma'.format(base_name))
            # 如果存在同名 ma 文件，则导入该 ma 文件
            if os.path.exists(ma_file):
                ma_file = os.path.normpath(ma_file).replace("\\", "/")
                mel.eval('file -import -type "mayaAscii" -ignoreVersion -ra true \
                          -mergeNamespacesOnClash false -namespace "{}" -options "v=0" \
                          -pr -importTimeRange "override" "{}";'.format(base_name, ma_file))

    def change_icon_size(self, value):
        self.myListWidget.setIconSize(QtCore.QSize(value, value))
        self.myListWidget.setGridSize(QtCore.QSize(value + 20, value + 20))

    def category_changed(self):
        self.search(self.search_line_edit.text())

    def search(self, text):
        # 获取当前选择的分类
        category = self.search_category_combo.currentText()

        # 遍历所有的项目，隐藏不匹配的项目
        for i in range(self.myListWidget.count()):
            item = self.myListWidget.item(i)
            if category == "All" or category in item.text():
                if text.lower() in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)
            else:
                item.setHidden(True)

    def open_folder(self):
        # 获取当前选中的项
        item = self.myListWidget.currentItem()
        if item:
            full_path = item.data(QtCore.Qt.UserRole)
            folder = os.path.dirname(full_path)
            # 打开文件夹
            os.startfile(folder)

    def view_large_image(self):
        # 获取当前选中的项
        item = self.myListWidget.currentItem()
        if item:
            full_path = item.data(QtCore.Qt.UserRole)
            # 修改文件路径，使其指向png格式的图片
            base_path, ext = os.path.splitext(full_path)
            png_path = base_path + '.png'
            # 创建一个新的窗口来显示大图
            self.img_win = QtWidgets.QDialog(self)
            self.img_win.setWindowTitle(item.text())
            layout = QtWidgets.QVBoxLayout(self.img_win)
            label = QtWidgets.QLabel(self.img_win)
            # 将pixmap的输入文件从full_path修改为png_path
            pixmap = QtGui.QPixmap(png_path)
            label.setPixmap(pixmap.scaled(1024, 1024, QtCore.Qt.KeepAspectRatio))
            layout.addWidget(label)
            self.img_win.setLayout(layout)
            self.img_win.show()

    def sort_items(self):
        items = []
        # 将所有项目添加到items列表中
        for i in range(self.myListWidget.count()):
            item = self.myListWidget.item(i)
            items.append(item)

        # 自定义排序函数，将字符串中的数字部分和非数字部分分开处理
        def sort_key(item):
            parts = re.split('(\d+)', item.text())
            return [int(part) if part.isdigit() else part for part in parts]

        # 使用自定义排序函数进行排序
        items.sort(key=sort_key)

        # 清空列表并重新添加排序后的项目
        self.myListWidget.clear()
        for item in items:
            self.myListWidget.addItem(item)

    def populate_menu1(self):

        sorted_menu1_keys = sorted(self.data.keys())
        self.menu1.addItems(sorted_menu1_keys)

    def on_menu1_changed(self, index):
        # 清除第二个菜单的内容
        self.menu2.clear()

        # 检索并按字母顺序排序键
        sorted_keys = sorted(self.data[self.menu1.currentText()].keys())

        # 将排序后的键添加到第二个菜单
        self.menu2.addItems(sorted_keys)

    def on_menu2_changed(self, index):

        menu1_text = self.menu1.currentText()
        menu2_text = self.menu2.currentText()

        if not menu1_text or not menu2_text:
            return

        path = self.data[menu1_text][menu2_text]
        self.load_icons_from_path(path)

    def load_icons_from_path(self, path):
        try:
            with open(os.path.join(path, 'cache.json'), 'r', encoding='utf-8') as f:
                cache = json.load(f, object_pairs_hook=OrderedDict)
        except FileNotFoundError:
            self.create_cache(path)
            with open(os.path.join(path, 'cache.json'), 'r', encoding='utf-8') as f:
                cache = json.load(f, object_pairs_hook=OrderedDict)

        # 自定义排序函数，将字符串中的数字部分和非数字部分分开处理
        def sort_key(item):
            parts = re.split('(\d+)', item[0])
            return [int(part) if part.isdigit() else part for part in parts]

        # 使用自定义排序函数进行排序
        sorted_cache = sorted(cache.items(), key=sort_key)

        self.myListWidget.clear()
        for file_name, full_path in sorted_cache:
            item = QtWidgets.QListWidgetItem(QtGui.QIcon(full_path), os.path.splitext(file_name)[0])
            item.setData(QtCore.Qt.UserRole, full_path)

            # 根据文件名设置文字颜色
            icon_text = os.path.splitext(file_name)[0]
            if "High" in icon_text:
                item.setForeground(QtGui.QColor("red"))
            elif "Low" in icon_text:
                item.setForeground(QtGui.QColor("green"))
            else:
                item.setForeground(QtGui.QColor("yellow"))

            # 设置鼠标悬停时显示的全名
            item.setToolTip(icon_text)

            self.myListWidget.addItem(item)

    def create_cache(self, path):
        cache = {}

        for root, dirs, files in os.walk(path):
            # 创建一个新列表，其中包含 dirs 中除了 'textures' 和 'tex' 以外的所有元素，不区分大小写
            dirs[:] = [d for d in dirs if d.lower() not in ['textures', 'tex', 'Sim']]

            for file_name in files:
                if file_name.endswith(".png"):
                    png_path = os.path.join(root, file_name)
                    ico_filename = os.path.splitext(file_name)[0] + '.ico'
                    ico_path = os.path.join(root, ico_filename)

                    # 检查ico文件是否存在以及比较修改时间
                    if not os.path.exists(ico_path) or os.path.getmtime(png_path) > os.path.getmtime(ico_path):
                        self.png_to_ico(png_path, 8)

                    cache[file_name] = ico_path  # 存储ico路径到字典中

        with open(os.path.join(path, 'cache.json'), 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=4, sort_keys=True)

    def png_to_ico(self, file_path, color_depth=8):
        if isinstance(color_depth, str):
            try:
                color_depth = int(color_depth)
            except ValueError:
                raise ValueError("color_depth参数必须是整数类型")

        img = Image.open(file_path)
        img = img.convert('RGBA')

        # 根据原比例调整尺寸...
        width, height = img.size
        new_size = (128, int(128 * height / width)) if width > height else (int(128 * width / height), 128)
        img = img.resize(new_size, Image.LANCZOS)  # 使用LANCZOS方法进行抗锯齿处理

        if color_depth < 24:
            img = img.quantize(colors=2 ** (color_depth))
            img = img.convert('RGBA')

        ico_path = os.path.splitext(file_path)[0] + '.ico'
        img.save(ico_path, format='ICO', sizes=[new_size])

        return ico_path

    def ensure_gpu_cache_plugin_loaded(self):
        """确保 maya 插件 gpucache 已加载"""
        if not cmds.pluginInfo('gpuCache', query=True, loaded=True):
            try:
                cmds.loadPlugin('gpuCache')
                print(u'Maya 插件 gpucache 加载成功.')
            except:
                print(u'无法加载 Maya 插件 gpucache，请检查安装是否正确或者版本是否匹配')

    def create_cube(self, obj):
        # 获取选择物体的大小
        bbox = cmds.exactWorldBoundingBox(obj)
        width = bbox[3] - bbox[0]
        depth = bbox[5] - bbox[2]
        height = bbox[4] - bbox[1]  # 直接从bbox获取高度
        # 创建一个pCube并设置其大小匹配选择的物体
        cube = cmds.polyCube(w=width, h=height, d=depth)[0]
        # 计算选择物体的中心位置
        center = [(bbox[0] + bbox[3]) / 2, (bbox[1] + bbox[4]) / 2, (bbox[2] + bbox[5]) / 2]
        # 将立方体移动到选定物体的中心位置
        cmds.move(center[0], center[1], center[2], cube)
        # 删除立方体
        cmds.delete(cube)
        return center

    def get_unique_name(self, base_name):
        """
        生成一个唯一的节点名称，如果场景中已经存在，则添加数值后缀。
        """
        suffix = 1
        unique_name = "{}{:01d}".format(base_name, suffix)
        while cmds.objExists(unique_name):
            suffix += 1
            unique_name = "{}{:01d}".format(base_name, suffix)
        return unique_name
    def on_item_double_clicked(self, item):
        self.ensure_gpu_cache_plugin_loaded()

        base_name = os.path.splitext(item.text())[0]
        folder = os.path.dirname(item.data(QtCore.Qt.UserRole))

        # add condition for "_Sim" in base_name
        if base_name.endswith('_Sim'):
            # assuming the sequence files are named as base_name + sequence number
            ass_file = os.path.join(folder, 'Sim', '{}.0001.ass'.format(base_name))
        else:
            ass_file = os.path.join(folder, '{}.ass'.format(base_name))
        abc_file = os.path.join(folder, '{}.abc'.format(base_name))

        selected_objects = cmds.ls(selection=True)

        import imp
        external_module = imp.load_source("external_module", r"D:\Cling_toolbox\plug-in\GPUcache\GPU_switch_A.py")

        # 创建 MayaUIWindow 类的实例
        maya_ui = external_module.MayaUIWindow()

        if not selected_objects:
            # 如果没有选中 transform 节点，创建一个位于原点的 transform 节点
            node_name = "{}_{:03d}_mo".format(base_name, self.transform_node_counter)
            transform_node = cmds.createNode('transform', name=node_name)
            self.transform_node_counter += 1
            cmds.setAttr('{}.translateX'.format(transform_node), 0)
            cmds.setAttr('{}.translateY'.format(transform_node), 0)
            cmds.setAttr('{}.translateZ'.format(transform_node), 0)
            cmds.setAttr('{}.rotateX'.format(transform_node), 0)
            cmds.setAttr('{}.rotateY'.format(transform_node), 0)
            cmds.setAttr('{}.rotateZ'.format(transform_node), 0)
            cmds.setAttr('{}.scaleX'.format(transform_node), 1)
            cmds.setAttr('{}.scaleY'.format(transform_node), 1)
            cmds.setAttr('{}.scaleZ'.format(transform_node), 1)

            gpu_node_name = self.get_unique_name("GPU_" + base_name + "Shape")
            gpu_node = cmds.createNode('gpuCache', name=gpu_node_name, parent=transform_node)
            cmds.setAttr('{}.cacheFileName'.format(gpu_node), abc_file, type='string')

            standin_node = cmds.createNode('aiStandIn', name="ASS_" + base_name + "Shape", parent=transform_node)
            cmds.setAttr('{}.dso'.format(standin_node), ass_file, type='string')

            # if base_name ends with "_Sim", set useFrameExtension to 1
            if base_name.endswith('_Sim'):
                cmds.setAttr('{}.useFrameExtension'.format(standin_node), 1)

            # 关闭渲染属性
            maya_ui.set_gpucache_attr(gpu_node, False)

            cmds.showHidden(transform_node)


            group_name = base_name + "_ModGrp"
            upper_level_group = "CJ_DL_Grp"
            top_level_group = "Geometry"

            # 检查顶级组是否存在，若不存在，则创建
            if not cmds.objExists(top_level_group):
                cmds.group(empty=True, name=top_level_group)

            # 检查上一级组是否存在，若不存在，则创建并置于顶级组下
            if not cmds.objExists(upper_level_group):
                cmds.group(empty=True, name=upper_level_group, parent=top_level_group)


            if cmds.objExists(group_name):
                cmds.parent(transform_node, group_name)
            else:
                cmds.group(transform_node, name=group_name, parent=upper_level_group)

            # 确保目标组在正确的位置
            if not cmds.listRelatives(group_name, parent=True)[0] == upper_level_group:
                cmds.parent(group_name, upper_level_group)



        else:

            for obj in selected_objects:
                # 获取选中物体的移动、旋转和缩放值
                transform_values = [cmds.getAttr('{}.translateX'.format(obj)),
                                    cmds.getAttr('{}.translateY'.format(obj)),
                                    cmds.getAttr('{}.translateZ'.format(obj)),
                                    cmds.getAttr('{}.rotateX'.format(obj)),
                                    cmds.getAttr('{}.rotateY'.format(obj)),
                                    cmds.getAttr('{}.rotateZ'.format(obj)),
                                    cmds.getAttr('{}.scaleX'.format(obj)),
                                    cmds.getAttr('{}.scaleY'.format(obj)),
                                    cmds.getAttr('{}.scaleZ'.format(obj))]

                # 检查物体是否有移动、旋转和缩放都是默认值
                if all([v == 0 for v in transform_values[:6]]) and all([v == 1 for v in transform_values[6:]]):
                    # 如果是默认值则运行 create_cube 函数并获取 cube 的位移
                    center = self.create_cube(obj)
                    transform_values[:3] = center
                node_name = "{}_{:03d}_mo".format(base_name, self.transform_node_counter)
                transform_node = cmds.createNode('transform', name=node_name)
                self.transform_node_counter += 1
                gpu_node_name = self.get_unique_name("GPU_" + base_name + "Shape")
                gpu_node = cmds.createNode('gpuCache', name=gpu_node_name, parent=transform_node)
                cmds.setAttr('{}.cacheFileName'.format(gpu_node), abc_file, type='string')
                standin_node = cmds.createNode('aiStandIn', name="ASS_" + base_name + "Shape", parent=transform_node)
                cmds.setAttr('{}.dso'.format(standin_node), ass_file, type='string')

                if base_name.endswith('_Sim'):
                    cmds.setAttr('{}.useFrameExtension'.format(standin_node), 1)
                # 关闭渲染属性
                maya_ui.set_gpucache_attr(gpu_node, False)

                cmds.showHidden(transform_node)

                # 将选中物体的移动、旋转和缩放值赋给新建的 transform 节点
                cmds.setAttr('{}.translate'.format(transform_node), transform_values[0], transform_values[1],
                             transform_values[2])
                cmds.setAttr('{}.rotate'.format(transform_node), transform_values[3], transform_values[4],
                             transform_values[5])
                cmds.setAttr('{}.scale'.format(transform_node), transform_values[6], transform_values[7],
                             transform_values[8])

                # 假定 'base_name' 是已定义的变量
                group_name = base_name + "_ModGrp"
                upper_level_group = "CJ_DL_Grp"
                top_level_group = "Geometry"

                # 检查顶级组是否存在，若不存在，则创建
                if not cmds.objExists(top_level_group):
                    cmds.group(empty=True, name=top_level_group)

                # 检查上一级组是否存在，若不存在，则创建并置于顶级组下
                if not cmds.objExists(upper_level_group):
                    cmds.group(empty=True, name=upper_level_group, parent=top_level_group)

                # 检查目标组是否存在，如果存在，将 transform_node 添加到该组中
                # 如果不存在，创建新的组，并将其放在 upper_level_group 下
                if cmds.objExists(group_name):
                    cmds.parent(transform_node, group_name)
                else:
                    cmds.group(transform_node, name=group_name, parent=upper_level_group)

                # 确保目标组在正确的位置
                if not cmds.listRelatives(group_name, parent=True)[0] == upper_level_group:
                    cmds.parent(group_name, upper_level_group)

        cmds.select(transform_node)
        try:

            # 调用 多功能切换 中的添加属性
            maya_ui.refresh_transform_node()

        except Exception as e:
            cmds.warning("Error executing refresh_transform_node: {}".format(str(e)))

    def page3_refresh_list(self):
        path = self.data[self.menu1.currentText()][self.menu2.currentText()]
        self.create_cache(path)
        self.load_icons_from_path(path)


    # 第四页
    def on_load_finished(self, data, html):
        self.fill_item(self.tree.invisibleRootItem(), data)
        self.browser.setHtml(html)
    # 检查当前是第几页
    def on_tab_changed(self, index):
        # 处理第三页的加载
        if index == 2 and not self.isPage3Loaded:  # 检查是否是第三页且未加载过
            self.loadPage3Content()  # 加载第三页内容的方法
            self.isPage3Loaded = True

        # 处理第四页的加载
        if index == 3 and not self.isPage4Loaded:  # 检查是否是第四页且未加载过
            self.load_thread = LoadJsonThread()  # 创建线程
            self.load_thread.load_finished.connect(self.on_load_finished)  # 连接信号和槽
            self.load_thread.start()  # 启动线程
            self.isPage4Loaded = True

    def fill_item(self, item, value):
        item.setExpanded(True)
        if isinstance(value, dict):
            for key, val in sorted(value.items()):
                child = QtWidgets.QTreeWidgetItem()
                child.setText(0, str(key))
                item.addChild(child)
                self.fill_item(child, val)
        elif isinstance(value, list):
            for val in value:
                child = QtWidgets.QTreeWidgetItem()
                item.addChild(child)
                if isinstance(val, dict):
                    child.setText(0, '[dict]')
                    self.fill_item(child, val)
                elif isinstance(val, list):
                    child.setText(0, '[list]')
                    self.fill_item(child, val)
                else:
                    child.setText(0, str(val))
        else:
            child = QtWidgets.QTreeWidgetItem()
            child.setText(0, str(value))
            item.addChild(child)


# 创建一个全局变量来存储窗口对象
global win


def main():
    # 创建一个全局变量来存储窗口对象
    global win
    workspace_control_name = "ToolboxWorkspaceControl"
    if cmds.workspaceControl(workspace_control_name, q=1, exists=1):
        cmds.deleteUI(workspace_control_name)
    control = cmds.workspaceControl(
        workspace_control_name,
        label=u"Cling_toolbox",
        tabToControl=('AttributeEditor', -1),
        retain=False,
        initialWidth=450,
        initialHeight=300,
        minimumWidth=200,
        minimumHeight=300
    )
    # 获取Maya窗口
    win_ptr = omui.MQtUtil.findControl(workspace_control_name)
    win_widget = wrapInstance(int(win_ptr), QtWidgets.QWidget)

    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    global win
    win = IconGridWindow(win_widget)
    win.resize(450, 300)
    win.show()
    cmds.workspaceControl(workspace_control_name, edit=1, restore=True)


if __name__ == '__main__':
    main()
