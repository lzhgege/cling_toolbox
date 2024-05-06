# -*- coding: utf-8 -*-
import json
import os
from PySide6 import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
from shiboken6 import wrapInstance

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class JsonDataWindow(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        # 加载json数据
        with open("D:/Cling_toolbox/json/gpu_route.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        json_file_path = data.get('new_json_path')
        if not json_file_path or not os.path.isfile(json_file_path):
            raise ValueError("无法找到新的json文件或路径不正确")
        with open(json_file_path, 'r', encoding='utf-8') as file:
            self.existing_data = json.load(file)  # 将数据保存为实例变量
        super(JsonDataWindow, self).__init__(parent)

        self.setWindowTitle(u"资产库目录添加")
        self.setMinimumSize(300, 130)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # 根据默认选中的项目名更新场景下拉菜单
        self.update_scene_combo(self.project_name_combo.currentText())

    def create_widgets(self):
        # 加载json数据
        with open("D:/Cling_toolbox/json/gpu_route.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        json_file_path = data.get('new_json_path')
        if not json_file_path or not os.path.isfile(json_file_path):
            raise ValueError(u"无法找到新的json文件或路径不正确")
        with open(json_file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
        project_names = list(existing_data.keys())
        project_names.append(u'新建项目')

        self.project_name_label = QtWidgets.QLabel(u"项目名：")
        self.project_name_combo = QtWidgets.QComboBox()
        self.project_name_combo.addItems(project_names)
        self.new_project_name_field = QtWidgets.QLineEdit()
        self.new_project_name_field.setPlaceholderText(u"请输入新的项目名")
        self.new_project_name_field.setVisible(False)

        self.scene_name_label = QtWidgets.QLabel(u"场景名：")
        self.scene_name_combo = QtWidgets.QComboBox()
        self.scene_name_combo.addItem(u'新建场景')  # 添加"新建场景"选项
        self.new_scene_name_field = QtWidgets.QLineEdit()
        self.new_scene_name_field.setPlaceholderText(u"请输入新的场景名")
        self.new_scene_name_field.setVisible(False)

        self.asset_path_label = QtWidgets.QLabel(u"资产路径：")
        self.asset_path_field = QtWidgets.QLineEdit()
        self.asset_path_field.setPlaceholderText(u"请选择资产存储路径/删除不需要填写路径")
        self.asset_path_button = QtWidgets.QPushButton()
        self.asset_path_button.setIcon(QtGui.QIcon("D:/Cling_toolbox/icons/SP_DirOpenIcon.png"))

        self.add_button = QtWidgets.QPushButton(u"添加数据")
        self.add_button.setStyleSheet("background-color: green; color: white;")
        self.remove_button = QtWidgets.QPushButton(u"删除数据")
        self.remove_button.setStyleSheet("background-color: red; color: white;")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        project_layout = QtWidgets.QHBoxLayout()
        project_layout.addWidget(self.project_name_label)
        project_layout.addWidget(self.project_name_combo)
        project_layout.addWidget(self.new_project_name_field)

        scene_layout = QtWidgets.QHBoxLayout()
        scene_layout.addWidget(self.scene_name_label)
        scene_layout.addWidget(self.scene_name_combo)
        scene_layout.addWidget(self.new_scene_name_field)

        asset_path_layout = QtWidgets.QHBoxLayout()
        asset_path_layout.addWidget(self.asset_path_label)
        asset_path_layout.addWidget(self.asset_path_field)
        asset_path_layout.addWidget(self.asset_path_button)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        main_layout.addLayout(project_layout)
        main_layout.addLayout(scene_layout)
        main_layout.addLayout(asset_path_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.project_name_combo.currentTextChanged.connect(self.update_scene_combo)
        self.project_name_combo.currentTextChanged.connect(self.show_new_project_name_field)
        self.scene_name_combo.currentTextChanged.connect(self.show_new_scene_name_field)
        self.scene_name_combo.currentTextChanged.connect(self.update_asset_path_field)  # 新增
        self.asset_path_button.clicked.connect(self.select_asset_path)
        self.add_button.clicked.connect(self.add_data)
        self.remove_button.clicked.connect(self.remove_data)

        

    def show_new_project_name_field(self, text):
        self.new_project_name_field.setVisible(text == u'新建项目')

    def show_new_scene_name_field(self, text):
        self.new_scene_name_field.setVisible(text == u'新建场景')
        
    def update_scene_combo(self, project_name):
        self.scene_name_combo.clear()  # 清空场景名下拉菜单

        scenes = self.existing_data.get(project_name, {}).keys()  # 获取所选项目的所有场景名
        self.scene_name_combo.addItems(scenes)  # 将场景名添加到场景名下拉菜单

        self.scene_name_combo.addItem(u'新建场景')  # 添加"新建场景"选项

    def select_asset_path(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.asset_path_field.setText(directory)

    def add_data(self):
        project_name = self.new_project_name_field.text() if self.new_project_name_field.isVisible() else self.project_name_combo.currentText()
        scene_name = self.new_scene_name_field.text() if self.new_scene_name_field.isVisible() else self.scene_name_combo.currentText()
        asset_path = self.asset_path_field.text()

        # 检查项目名是否已存在
        if project_name in self.existing_data:
            # 如果项目已存在，检查场景名是否已存在
            if scene_name in self.existing_data[project_name]:
                # 如果场景已存在，打印错误信息并返回
                print("场景名已存在。")
                return
            else:
                # 如果场景不存在，添加新的场景
                self.existing_data[project_name][scene_name] = asset_path
        else:
            # 如果项目不存在，添加新的项目和场景
            self.existing_data[project_name] = {scene_name: asset_path}

        # 将修改后的数据写回json文件
        json_file_path = self.get_json_path()
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.existing_data, f, ensure_ascii=False, indent=4)

        self.update_project_combo()  # 在添加数据后更新项目下拉菜单


    def remove_data(self):
        project_name = self.project_name_combo.currentText()
        scene_name = self.scene_name_combo.currentText()

        if project_name in self.existing_data:
            if scene_name in self.existing_data[project_name]:
                del self.existing_data[project_name][scene_name]
                if not self.existing_data[project_name]:
                    del self.existing_data[project_name]

        # 将修改后的数据写回json文件
        json_file_path = self.get_json_path()
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.existing_data, f, ensure_ascii=False, indent=4)

        self.update_project_combo()  # 在删除数据后更新项目下拉菜单

    def update_project_combo(self):
        self.project_name_combo.clear()  # 清空项目名下拉菜单

        project_names = list(self.existing_data.keys())
        project_names.append(u'新建项目')

        self.project_name_combo.addItems(project_names)  # 将项目名添加到项目名下拉菜单
        
    def update_asset_path_field(self, scene_name):
        project_name = self.project_name_combo.currentText()

        if project_name in self.existing_data and scene_name in self.existing_data[project_name]:
            asset_path = self.existing_data[project_name][scene_name]
            self.asset_path_field.setText(asset_path)
        else:
            self.asset_path_field.clear()

    def get_json_path(self):
        # 从gpu_route.json获取路径，如果不存在，则使用默认路径
        try:
            with open("D:/Cling_toolbox/json/gpu_route.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            json_file_path = data.get('new_json_path')
            if not json_file_path or not os.path.isfile(json_file_path):
                json_file_path = "D:/Cling_toolbox/json/GPU_project.json"
        except FileNotFoundError:
            json_file_path = "D:/Cling_toolbox/json/GPU_project.json"
        return json_file_path


if __name__ == "__main__":
    try:
        json_data_win.close() # pylint: disable=E0601
        json_data_win.deleteLater()
    except:
        pass

    json_data_win = JsonDataWindow()
    json_data_win.show()
