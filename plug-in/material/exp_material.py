# -*- coding: utf-8 -*-
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
from PySide2 import QtWidgets
import json
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class MaterialExporter(QtWidgets.QDialog):
    WINDOW_TITLE = "Material Exporter"

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent if parent else maya_main_window())
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setObjectName(self.WINDOW_TITLE)  # set object name for later check
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    @staticmethod
    def show_window():
        # If the window already exists, delete it
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(widget, MaterialExporter):
                widget.deleteLater()

        # Create a new instance of the window
        material_exporter = MaterialExporter()
        material_exporter.show()


    def create_widgets(self):
        self.name_le = QtWidgets.QLineEdit()
        self.directory_cb = QtWidgets.QComboBox()
        self.directory_cb.addItems(["Metal", "Wood", "Rocks", "Ground", "Others"])
        self.export_btn = QtWidgets.QPushButton('Export')

    def create_layouts(self):
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.name_le)
        input_layout.addWidget(self.directory_cb)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.export_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(input_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.export_btn.clicked.connect(self.export_materials)

    def export_materials(self):
        custom_name = self.name_le.text()
        directory = self.directory_cb.currentText()
        selected_materials_from_objects = get_materials_from_selected_objects()
        selected_materials = get_selected_materials()
        all_materials_to_export = list(set(selected_materials_from_objects + selected_materials))
        for index, material in enumerate(all_materials_to_export):
            print('Exporting: ' + material)
            export_material(material, custom_name + '_' + str(index + 1), directory)


def export_material(material, custom_name, directory):
    json_file_path = 'D:/Cling_toolbox/json/Material_library.json'
    default_path = "D:\\Cling_toolbox\\Material_library"
    if not os.path.exists(json_file_path):
        output_dir = os.path.join(default_path, directory)
    else:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        output_dir = os.path.join(data['MATERIAL_LIBRARY_PATH'], directory)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, custom_name + '.ma')

    # Rename material before exporting
    cmds.rename(material, custom_name)
    cmds.select(custom_name)
    cmds.file(output_path, force=True, options="v=0;", typ="mayaAscii", pr=True, es=True)



def get_materials_from_selected_objects():
    selected_objects = cmds.ls(selection=True)
    materials = []
    for obj in selected_objects:
        shading_groups = cmds.listConnections(obj, type='shadingEngine')
        if shading_groups is None:
            continue
        for sg in shading_groups:
            conns = cmds.listConnections(sg + ".surfaceShader")
            if conns is None:
                continue
            materials.extend(conns)
    return list(set(materials))  # remove duplicates

def get_selected_materials():
    selected_nodes = cmds.ls(selection=True)
    materials = []
    for node in selected_nodes:
        if cmds.nodeType(node) in ["lambert", "blinn", "phong", "surfaceShader"]:
            materials.append(node)
    return materials


# 创建 MaterialExporter 实例并显示窗口
if __name__ == '__main__':
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