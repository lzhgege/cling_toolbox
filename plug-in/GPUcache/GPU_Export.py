# -*- coding: utf-8 -*-
# 作者：cling
# 微信：clingkaka
# 个人主页：www.cg6i.com
# 模型下载：www.cgfml.com
# AI聊天绘画：ai.cgfml.com
# 敲码不易修改搬运请保留以上信息，感谢！！！！！
import maya.cmds as cmds
import maya.mel as mel
import os
import shutil
import json
import re
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import QPushButton, QColorDialog
import glob
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui
import maya.mel
import sys

sys.path.append('D:\\Cling_toolbox\\external_library')
from PIL import Image
import time


class MyComboBox(QtWidgets.QComboBox):
    def wheelEvent(self, event):
        # 忽略滚轮事件
        event.ignore()



class ExportWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent if parent else maya_main_window(), QtCore.Qt.WindowFlags())

        self.setWindowTitle(u"资产导出工具")


        # 创建下拉列表和文本框
        self.cmb_project = MyComboBox()
        self.cmb_scene = MyComboBox()
        self.cmb_category = MyComboBox()
        self.cmb_category.addItem(u"请选择分类")
        self.cmb_category.addItems(["Tree", "Grass", "Flower", "Bush", "Rock", "Building", "Terrain", "Water", "Other", "Assembly"])
        self.cmb_category.currentIndexChanged.connect(self.set_default_color)
        self.txt_name = QtWidgets.QLineEdit()

        self.cmb_quality = MyComboBox(self)
        self.cmb_quality.addItems(["High", "Low", "Sim", "Custom"])  # add "Sim" here
        self.cmb_quality.currentIndexChanged.connect(self.on_quality_changed)

        self.txt_custom_quality = QtWidgets.QLineEdit(self)
        self.txt_custom_quality.hide()  # 默认隐藏

        # 添加新的文本框
        self.txt_start_frame = QtWidgets.QLineEdit(self)
        self.txt_start_frame.hide()  # 默认隐藏
        self.txt_start_frame.setPlaceholderText(u"请输入开始帧")

        self.txt_end_frame = QtWidgets.QLineEdit(self)
        self.txt_end_frame.hide()  # 默认隐藏
        self.txt_end_frame.setPlaceholderText(u"请输入结束帧")

        # 创建布局并添加组件
        layout = QtWidgets.QVBoxLayout(self)

        main_layout = QtWidgets.QHBoxLayout()
       # main_layout.setContentsMargins(0, 0, 0, 0)  # 设置左边距为0
        main_layout.setSpacing(5)  # 设置小部件之间的间距为0

        # 创建第一组布局
        layout1 = QtWidgets.QHBoxLayout()
       # layout1.setContentsMargins(0, 0, 0, 0)  # 设置左边距为0
        layout1.setSpacing(5)  # 设置小部件之间的间距为0
        layout1.setAlignment(QtCore.Qt.AlignLeft)  # 设置对齐方式为左对齐
        layout1.addWidget(QtWidgets.QLabel(u"项目"))
        layout1.addWidget(self.cmb_project)

        # 创建第二组布局
        layout2 = QtWidgets.QHBoxLayout()
        #layout2.setContentsMargins(0, 0, 0, 0)  # 设置左边距为0
        layout2.setSpacing(5)  # 设置小部件之间的间距为0
        layout2.setAlignment(QtCore.Qt.AlignLeft)  # 设置对齐方式为左对齐
        layout2.addWidget(QtWidgets.QLabel(u"场景"))
        layout2.addWidget(self.cmb_scene)

        # 创建第三组布局
        layout3 = QtWidgets.QHBoxLayout()
        #layout3.setContentsMargins(0, 0, 0, 0)  # 设置左边距为0
        layout3.setSpacing(5)  # 设置小部件之间的间距为0
        layout3.setAlignment(QtCore.Qt.AlignLeft)  # 设置对齐方式为左对齐
        layout3.addWidget(QtWidgets.QLabel(u"分类"))
        layout3.addWidget(self.cmb_category)

        # 将这些布局添加到主布局中
        main_layout.addLayout(layout1)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)
        layout.addLayout(main_layout)

        # 创建文件名的水平布局
        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(QtWidgets.QLabel(u"文件名称"))
        name_layout.addWidget(self.txt_name)
        name_layout.addWidget(self.cmb_quality)
        name_layout.addWidget(self.txt_custom_quality)  # 添加这行
        name_layout.addWidget(self.txt_start_frame)  # 添加这行
        name_layout.addWidget(self.txt_end_frame)  # 添加这行

        layout.addLayout(name_layout)

        # 创建复选框水平布局
        checkbox_layout = QtWidgets.QHBoxLayout()
        self.chk_tex = QtWidgets.QCheckBox(u"贴图")
        self.chk_origin = QtWidgets.QCheckBox(u"回原点")
        self.chk_abc = QtWidgets.QCheckBox("GPU")
        self.chk_diy = QtWidgets.QCheckBox("DIY")
        self.chk_bbox = QtWidgets.QCheckBox("BBOX")
        self.chk_ass = QtWidgets.QCheckBox("ASS")
        self.chk_ma = QtWidgets.QCheckBox("MA")
        self.jietu = QtWidgets.QCheckBox(u"截图")

        # 设置默认为选中状态

        self.chk_abc.setChecked(True)
        self.chk_ass.setChecked(True)
        self.chk_ma.setChecked(True)
        self.chk_bbox.setChecked(True)
        self.jietu.setChecked(True)
        # 添加信号槽连接，当任一复选框被勾选时，调用相应的槽函数
        self.chk_abc.stateChanged.connect(self.show_color_picker)
        self.chk_bbox.stateChanged.connect(self.show_color_picker)
        self.chk_diy.stateChanged.connect(self.show_color_picker)

        # 添加到水平布局
        checkbox_layout.addWidget(self.chk_tex)
        checkbox_layout.addWidget(self.chk_origin)
        checkbox_layout.addWidget(self.chk_abc)
        checkbox_layout.addWidget(self.chk_diy)
        checkbox_layout.addWidget(self.chk_bbox)
        checkbox_layout.addWidget(self.chk_ass)
        checkbox_layout.addWidget(self.chk_ma)
        checkbox_layout.addWidget(self.jietu)

        # 添加水平布局到垂直布局
        layout.addLayout(checkbox_layout)

        self.color_picker = QPushButton(u'GPU颜色选择', self)
        self.color_picker.clicked.connect(self.open_color_dialog)


        layout.addWidget(self.color_picker)

        # 创建导出按钮
        self.btn_export = QtWidgets.QPushButton("Export")
        self.btn_export.setStyleSheet("background-color: rgb(6, 98, 106);")
        layout.addWidget(self.btn_export)

        # 进度条
        self.unt_cut = QtWidgets.QWidget()
        self.unt_cut.setObjectName("unt_cut")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.unt_cut)
        self.splitter_2 = QtWidgets.QSplitter(self.unt_cut)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.cut_progressBar = QtWidgets.QProgressBar(self.splitter_2)
        self.cut_progressBar.setMinimumSize(QtCore.QSize(0, 25))
        self.cut_progressBar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.cut_progressBar.setProperty("value", 0)
        self.cut_progressBar.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.cut_progressBar.setTextVisible(True)
        self.cut_progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.cut_progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.cut_progressBar.setObjectName("cut_progressBar")
        self.cut_progressBar.setFormat(u"%p%")
        layout.addWidget(self.cut_progressBar)

        # 连接信号和槽
        self.cmb_project.currentIndexChanged.connect(self.update_scenes)
        self.cmb_scene.currentIndexChanged.connect(self.update_export_path)
        self.txt_name.textChanged.connect(self.update_your_name)
        self.txt_name.setPlaceholderText(u"请输入文件名,为空则A001排序递增")
        self.btn_export.clicked.connect(self.export_files)

        self.export_path = ''
        self.your_name = ''

        # 初始化场景选择器
        self.refresh_data()

        # 修改窗口大小为宽度500像素、高度300像素
        self.resize(400, 100)
        self.set_default_color()

    def set_project_and_scene(self, project, scene):
        index_project = self.cmb_project.findText(project)
        if index_project >= 0:
            self.cmb_project.setCurrentIndex(index_project)

        index_scene = self.cmb_scene.findText(scene)
        if index_scene >= 0:
            self.cmb_scene.setCurrentIndex(index_scene)

    def show_color_picker(self):
        # 根据复选框的状态切换颜色选择按钮的可见性
        if self.chk_abc.isChecked() or self.chk_bbox.isChecked() or self.chk_diy.isChecked():
            self.color_picker.setVisible(True)
        else:
            self.color_picker.setVisible(False)

    def refresh_data(self):
        try:
            if not os.path.exists("D:/Cling_toolbox/json/gpu_route.json"):
                data = {'new_json_path': 'D:/Cling_toolbox/json/GPU_project.json'}
                with open("D:/Cling_toolbox/json/gpu_route.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f)
            else:
                with open("D:/Cling_toolbox/json/gpu_route.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)

            new_json_path = data.get('new_json_path')
            if not new_json_path or not os.path.isfile(new_json_path):
                raise ValueError("无法找到新的json文件或路径不正确")

            with open(new_json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except IOError as e:
            print(f"文件读取错误：{e}")
        except ValueError as e:
            print(f"无法解析JSON文件：{e}")

        # 更新项目列表
        self.cmb_project.clear()
        self.cmb_project.addItems(list(self.data.keys()))

        # 刷新场景和导出路径
        self.update_scenes()
        self.update_export_path()

    def update_scenes(self):
        self.cmb_scene.clear()
        project = self.cmb_project.currentText()
        if project:
            # 获取并排序场景名称
            sorted_scenes = sorted(list(self.data [project].keys()))
            self.cmb_scene.addItems(sorted_scenes)

    def update_export_path(self):
        project = self.cmb_project.currentText()
        scene = self.cmb_scene.currentText()

        if project and scene:
            self.export_path = self.data [project][scene]
        else:
            self.export_path = ''

    def update_your_name(self):
        self.your_name = self.txt_name.text()

    def on_quality_changed(self, index):
        if self.cmb_quality.currentText() == "Custom":
            self.txt_custom_quality.show()
            self.txt_start_frame.hide()
            self.txt_end_frame.hide()
        elif self.cmb_quality.currentText() == "Sim":
            self.txt_custom_quality.hide()
            self.txt_start_frame.show()
            self.txt_end_frame.show()
        else:
            self.txt_custom_quality.hide()
            self.txt_start_frame.hide()
            self.txt_end_frame.hide()

    def set_default_color(self):
        category = self.cmb_category.currentText()
        if category == 'Tree':
            color = (0.043, 0.286, 0.075)  # 绿色
        elif category == 'Grass':
            color = (0.533, 0.791, 0.422)  # 深绿色
        elif category == 'Flower':
            color = (0.643, 0.408, 0.612)
        elif category == 'Bush':
            color = (0.294, 0.686, 0.157)
        elif category == 'Rock':
            color = (0.624, 0.596, 0.529)
        elif category == 'Building':
            color = (0.431, 0.243, 0.129)
        elif category == 'Terrain':
            color = (0.333, 0.286, 0.169)
        elif category == 'Water':
            color = (0.106, 0.651, 0.698)
        else:
            color = (0.576, 0.569, 0.608)

        self.color_value = color
        self.color_picker.setStyleSheet(
            "background-color: rgb({},{},{})".format(int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)))



    def open_color_dialog(self, default_color=(1.0, 1.0, 1.0)):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_picker.setStyleSheet("background-color: {}".format(color.name()))
            self.color_value = color.getRgbF()[:3]  # Store the color value as a tuple

    def get_color(self):
        return self.color_value

    def file_is_open(self, file_path):
        if not os.path.exists(file_path):
            # 如果文件不存在，返回 False
            return False
        try:
            # 尝试以读写模式打开文件
            with open(file_path, 'r+'):
                pass
        except IOError:
            # 如果出现IOError，说明文件已经被其他进程打开
            return True
        # 如果没有错误，说明文件没有被其他进程打开
        return False

    def export_abc(self, directory, category, your_name, quality_suffix, selected_objects):
        self.ensure_gpu_cache_plugin_loaded()

        if self.chk_abc.isChecked():
            try:
                # 开启一个新的 undo chunk
                cmds.undoInfo(state=True, infinity=True)
                cmds.undoInfo(ock=True)
                new_material = cmds.shadingNode('lambert', asShader=True)
                color = self.get_color()
                cmds.setAttr(new_material + '.color', color[0], color[1], color[2], type='double3')
                copied_objects = []
                for obj in selected_objects:
                    copied_obj = cmds.duplicate(obj)[0]
                    copied_objects.append(copied_obj)
                    cmds.select(copied_obj)
                    cmds.hyperShade(assign=new_material)

                file_name = "{}_{}_{}_{}".format(self.cmb_scene.currentText(), category, your_name, quality_suffix)
                full_file_path = os.path.join(directory, file_name + '.abc')
                if self.file_is_open(full_file_path):
                    print(u"File {} 文件被占用, 跳过导出。".format(full_file_path))
                else:
                    cmds.select(copied_objects)

                    # 检查当前选择的质量是否为"Sim"
                    if self.cmb_quality.currentText() == "Sim":
                        start_frame = int(self.txt_start_frame.text())
                        end_frame = int(self.txt_end_frame.text())
                    else:
                        start_frame = 1
                        end_frame = 1

                    cmds.gpuCache(
                        startTime=start_frame,
                        endTime=end_frame,
                        optimize=True,
                        optimizationThreshold=4000,
                        writeMaterials=1,
                        directory=directory,
                        fileName=file_name,
                        dataFormat="ogawa",
                    )

                # 关闭 undo chunk
                cmds.undoInfo(cck=True)
                # 撤销之前的操作
                cmds.undo()
                cmds.undoInfo(state=True, infinity=False)
            except Exception as e:
                print("Error: ", e)

    def export_diy(self, directory, category, your_name, quality_suffix, selected_objects):
        self.ensure_gpu_cache_plugin_loaded()

        if self.chk_diy.isChecked():
            try:
                # 开启一个新的 undo chunk
                cmds.undoInfo(state=True, infinity=True)
                cmds.undoInfo(ock=True)
                new_material = cmds.shadingNode('lambert', asShader=True)
                color = self.get_color()
                cmds.setAttr(new_material + '.color', color[0], color[1], color[2], type='double3')
                copied_objects = []

                # 获取所有的组
                all_groups = cmds.ls(assemblies=True)
                # 通过Python的字符串函数筛选出名字包含"DIY"的组
                selected_groups = [group for group in all_groups if 'DIY' in group]

                for group in selected_groups:
                    copied_obj = cmds.duplicate(group)[0]
                    copied_objects.append(copied_obj)
                    cmds.select(copied_obj)
                    cmds.hyperShade(assign=new_material)
                file_name = "{}_{}_{}_{}".format(self.cmb_scene.currentText(), category, your_name,
                                                 quality_suffix + "_DIY")
                full_file_path = os.path.join(directory, file_name + '.abc')
                if self.file_is_open(full_file_path):
                    print(u"File {} 文件被占用, 跳过导出.".format(full_file_path))
                else:
                    cmds.select(copied_objects)
                    cmds.gpuCache(
                        startTime=1,
                        endTime=1,
                        optimize=True,
                        optimizationThreshold=4000,
                        writeMaterials=1,
                        directory=directory,
                        fileName=file_name,
                        dataFormat="ogawa",
                    )
                    # 关闭 undo chunk
                cmds.undoInfo(cck=True)
                # 撤销之前的操作
                cmds.undo()
                cmds.undoInfo(state=True, infinity=False)
            except Exception as e:
                print("Error: ", e)

    def export_bbox(self, directory, category, your_name, quality_suffix, selected_objects):
        self.ensure_gpu_cache_plugin_loaded()
        if self.chk_bbox.isChecked():
            bbox_cubes = []  # 存储创建的pCube对象
            try:
                for obj in selected_objects:
                    # 获取选择物体的大小
                    bbox = cmds.exactWorldBoundingBox(obj)
                    width = bbox[3] - bbox[0]
                    depth = bbox[5] - bbox[2]
                    height = bbox[4] - bbox[1]  # 直接从bbox获取高度

                    # 创建一个pCube并设置其大小匹配选择的物体
                    cube = cmds.polyCube(w=width, h=height, d=depth)[0]

                    # 获取选择物体的中心点坐标
                    center_x = (bbox[3] + bbox[0]) / 2
                    center_y = (bbox[4] + bbox[1]) / 2
                    center_z = (bbox[5] + bbox[2]) / 2

                    # 设置pCube的位置为选择物体的中心点
                    cmds.move(center_x, center_y, center_z, cube)

                    # Create a new lambert material
                    new_material = cmds.shadingNode('lambert', asShader=True)

                    # Get the color from the UI
                    color = self.get_color()  # Assuming there is a color picker in your UI

                    # Set the color to the new material
                    cmds.setAttr(new_material + '.color', color[0], color[1], color[2], type='double3')

                    # 将新的材质球赋予 pCube
                    cmds.select(cube)
                    cmds.hyperShade(assign=new_material)

                    bbox_cubes.append(cube)  # 添加到列表中

                file_name = "{}_{}_{}_{}".format(self.cmb_scene.currentText(), category, your_name,
                                                 quality_suffix + "_BBOX")
                full_file_path = os.path.join(directory, file_name + '.abc')
                if not self.file_is_open(full_file_path):
                    cmds.select(bbox_cubes)
                    cmds.gpuCache(
                        startTime=1,
                        endTime=1,
                        optimize=True,
                        optimizationThreshold=4000,
                        writeMaterials=True,
                        directory=directory,
                        fileName=file_name,
                        dataFormat="ogawa",
                    )
                else:
                    print(u"File {} 文件被占用, 跳过导出.".format(full_file_path))
            except Exception as e:
                print("Error: ", e)
            finally:
                cmds.delete(bbox_cubes)
    def ensure_gpu_cache_plugin_loaded(self):
        """确保 maya 插件 gpucache 已加载"""
        if not cmds.pluginInfo('gpuCache', query=True, loaded=True):
            try:
                cmds.loadPlugin('gpuCache')
                print(u'Maya 插件 gpucache 加载成功.')
            except:
                print(u'无法加载 Maya 插件 gpucache，请检查安装是否正确或者版本是否匹配')
    # 导出文件
    def copy_udim_files_to_new_path(self, new_dir_path, quality_suffix):
        if not os.path.exists(new_dir_path):
            os.makedirs(new_dir_path)

        selection = cmds.ls(sl=True)  # 获取当前选择的物体

        faces = cmds.polyListComponentConversion(selection, tf=True)  # 从物体转换到面

        shading_grps = set()  # 创建一个空的集合来存储着色组
        for face in faces:
            face_shading_grps = cmds.listSets(object=face)  # 获取每个面的着色组
            if face_shading_grps:
                shading_grps.update(face_shading_grps)  # 将着色组添加到集合中

        shaders = []
        for sg in shading_grps:
            if cmds.objExists(sg) and cmds.listConnections(sg):  # 检查着色组是否存在，以及是否有连接
                shaders.extend(cmds.ls(cmds.listConnections(sg), materials=True))  # 获取这些着色组的材质

        files = []
        for shader in shaders:
            files.extend(find_file_nodes(shader))

        total_files = len(files)  # 计算文件总数
        processed_files = 0  # 初始化已处理的文件数

        # 创建一个进度窗口
        cmds.progressWindow(title=u'复制贴图中', progress=0, status=u'复制贴图中: 0%', isInterruptable=True)

        for file_node in files:
            # 检查用户是否点击了取消按钮
            if cmds.progressWindow(query=True, isCancelled=True):
                break

            file_path = cmds.getAttr(file_node + '.fileTextureName')

            if file_path and os.path.exists(file_path):
                base_name = os.path.basename(file_path)
                dir_name = os.path.dirname(file_path)
                base_name_without_ext = os.path.splitext(base_name)[0]
                if re.search(r'\d{4}', base_name_without_ext):  # 检查是否包含四位数字，这可能是UDIM编号
                    udim_files = glob.glob(
                        os.path.join(dir_name, base_name_without_ext[:-4] + '*'))  # 找到所有相关的UDIM文件
                    for udim_file in udim_files:
                        # 获取文件的扩展名
                        _, file_extension = os.path.splitext(udim_file)
                        new_file_path = os.path.join(new_dir_path, os.path.basename(udim_file))
                        if file_extension != ".tx":  # 如果文件的扩展名不是 ".tx"，那么复制并改变该文件的大小
                            if os.path.normcase(os.path.abspath(udim_file)) != os.path.normcase(
                                    os.path.abspath(new_file_path)):  # 检查源文件和目标文件是否是同一个文件
                                shutil.copy2(udim_file, new_file_path)  # 复制文件到新路径
                            resize_image_if_needed(new_file_path, quality_suffix)  # 如果是Low则修改贴图大小
                            last_non_tx_file_path = new_file_path

                    # 设置文件节点的路径为最后一个非.tx文件的路径
                    cmds.setAttr((file_node + '.fileTextureName'), last_non_tx_file_path,
                                 type='string')  # 设置新路径

                    # 再次遍历UDIM贴图文件，这次只复制.tx文件
                    for udim_file in udim_files:
                        _, file_extension = os.path.splitext(udim_file)
                        new_file_path = os.path.join(new_dir_path, os.path.basename(udim_file))
                        if file_extension == ".tx":  # 如果文件的扩展名是 ".tx"，那么复制该文件
                            if os.path.normcase(os.path.abspath(udim_file)) != os.path.normcase(
                                    os.path.abspath(new_file_path)):  # 检查源文件和目标文件是否是同一个文件
                                shutil.copy2(udim_file, new_file_path)  # 复制文件到新路径

                    processed_files += 1
                    # 更新进度窗口
                    cmds.progressWindow(edit=True, progress=processed_files, status=(u'复制贴图中: ' + str(processed_files)))
                else:  # 非UDIM贴图
                    # 非UDIM贴图
                    new_file_path = os.path.join(new_dir_path, os.path.basename(file_path))
                    if os.path.normcase(os.path.abspath(file_path)) != os.path.normcase(
                            os.path.abspath(new_file_path)):  # 检查源文件和目标文件是否是同一个文件
                        shutil.copy2(file_path, new_file_path)  # 复制文件到新路径
                    resize_image_if_needed(new_file_path, quality_suffix)  # 如果是Low则修改贴图大小
                    cmds.setAttr((file_node + '.fileTextureName'), new_file_path, type='string')  # 设置新路径

                    # 复制同名的.TX文件
                    tx_file_path = file_path.rsplit('.', 1)[0] + '.TX'  # 获取同名的.TX文件路径
                    if os.path.exists(tx_file_path):  # 如果.TX文件存在
                        new_tx_file_path = os.path.join(new_dir_path, os.path.basename(tx_file_path))  # 定义新的.TX文件路径
                        if os.path.normcase(os.path.abspath(tx_file_path)) != os.path.normcase(
                                os.path.abspath(new_tx_file_path)):  # 检查源文件和目标文件是否是同一个文件
                            shutil.copy2(tx_file_path, new_tx_file_path)  # 复制.TX文件到新路径

                    processed_files += 1


                    cmds.progressWindow(edit=True, progress=processed_files, status=(u'复制贴图中: ' + str(processed_files)))

        # 关闭进度窗口
        cmds.progressWindow(endProgress=True)

        # 返回已处理的文件数
        return processed_files




    def export_files(self):

        # Reset progress bar
        self.cut_progressBar.setValue(0)
        self.cut_progressBar.setFormat(u"导出中...")

        # 进度条开始
        self.cut_progressBar.setMaximum(6)
        bar_num = 0

        if self.chk_diy.isChecked():  # 如果chk_diy被勾选
            # 获取所有的组
            all_groups = cmds.ls(assemblies=True)
            # 通过Python的字符串函数筛选出名字包含"DIY"的组
            selected_groups = [group for group in all_groups if 'DIY' in group]

            # 如果没有找到任何DIY组，弹出警告窗口并停止函数
            if not selected_groups:
                QtWidgets.QMessageBox.warning(self, u'警告', u'未找到名为DIY的组!')
                return

        category = self.cmb_category.currentText()
        if category == u"请选择分类":
            QtWidgets.QMessageBox.warning(self, u'警告', u'请选择分类!')
            return
        if self.cmb_quality.currentText() == "Custom":
            quality_suffix = self.txt_custom_quality.text()
        else:
            quality_suffix = self.cmb_quality.currentText()

        category_directory = os.path.join(self.export_path, category)
        if not os.path.exists(category_directory):
            os.makedirs(category_directory)

        input_name = self.txt_name.text().strip()

        if not input_name:
            name_base = 'A'
            counter = 1

            while True:
                auto_name = "{}{:03d}".format(name_base, counter)
                folder_name = "{}_{}_{}".format(self.cmb_scene.currentText(), category, auto_name)
                directory = os.path.join(category_directory, folder_name)
                if not os.path.exists(directory):
                    break
                else:
                    counter += 1
            your_name = auto_name
        else:
            your_name = input_name
            folder_name = "{}_{}_{}".format(self.cmb_scene.currentText(), category, your_name)
            directory = os.path.join(category_directory, folder_name)

        if not os.path.exists(directory):
            os.makedirs(directory)

        selected_objects = []
        selected = cmds.ls(selection=True)



        for obj in selected:
            selected_objects.append(obj)
            tex_dir = os.path.join(directory, "Tex")
            if not os.path.exists(tex_dir):
                os.makedirs(tex_dir)

            quality_folder = os.path.join(tex_dir, quality_suffix)
            if not os.path.exists(quality_folder):
                os.makedirs(quality_folder)

            if self.chk_tex.isChecked():
                processed_files = self.copy_udim_files_to_new_path(quality_folder, quality_suffix)
                # 更新进度条的值
                self.cut_progressBar.setValue(processed_files)


        # 更新进度条
        bar_num += 1
        self.cut_progressBar.setValue(bar_num)

        if self.chk_origin.isChecked():
            for obj in selected_objects:
                # 判断对象是否存在位移信息
                translation = cmds.xform(obj, query=True, worldSpace=True, translation=True)
                rotation = cmds.xform(obj, query=True, worldSpace=True, rotation=True)
                scale = cmds.xform(obj, query=True, worldSpace=True, scale=True)

                if any(translation) or any(rotation) or any([s - 1 for s in scale]):
                    # 如果存在位移，旋转或缩放，则先恢复到默认状态
                    cmds.xform(obj, worldSpace=True, translation=(0, 0, 0))
                    cmds.xform(obj, worldSpace=True, rotation=(0, 0, 0))
                    cmds.xform(obj, worldSpace=True, scale=(1, 1, 1))

            # 执行原有的操作
            mel.eval('string $obj[]=`ls-sl`; for($aObj in $obj) { move -rpr 0 0 0 $aObj; }')
            cmds.FreezeTransformations()

        if self.chk_ma.isChecked():
            scene_file = os.path.join(
                directory,
                "{}_{}_{}_{}.ma".format(self.cmb_scene.currentText(), category, your_name, quality_suffix)
            )

            # 检查该文件是否已经存在
            if os.path.exists(scene_file):
                # 如果存在，创建一个新的文件夹来存放旧的文件
                bak_folder = os.path.join(directory, "bak")
                if not os.path.exists(bak_folder):
                    os.makedirs(bak_folder)
                # 移动旧文件到新文件夹
                bak_file_path = os.path.join(bak_folder, os.path.basename(scene_file))
                if os.path.exists(bak_file_path):
                    os.remove(bak_file_path)  # 如果bak文件夹中已存在同名文件，则先删除
                os.rename(scene_file, bak_file_path)

            # 导出文件
            cmds.file(scene_file, force=True, options="v=0;", typ="mayaAscii", pr=True, es=True)

        # 更新进度条
        bar_num += 1
        self.cut_progressBar.setValue(bar_num)

        # 导出ass
        if self.chk_ass.isChecked():
            # 检查当前选择的质量是否为"Sim"
            if self.cmb_quality.currentText() == "Sim":
                # 如果是，修改ass文件的导出路径，并将其导出到一个名为"Sim"的文件夹中
                sim_directory = os.path.join(directory, "Sim")
                if not os.path.exists(sim_directory):
                    os.makedirs(sim_directory)
                # 获取开始帧和结束帧
                start_frame = int(self.txt_start_frame.text())
                end_frame = int(self.txt_end_frame.text())
                # 为每一帧生成一个ass文件
                for frame in range(start_frame, end_frame + 1):
                    # 将帧数转换为四位数字符串
                    frame_str = str(frame).zfill(4)
                    ass_file = os.path.join(
                        sim_directory,
                        "{}_{}_{}_{}.{}.ass".format(self.cmb_scene.currentText(), category, your_name, quality_suffix,
                                                    frame_str)
                    )
                    # 将ass导出改为序列导出
                    cmds.select(selected_objects)
                    cmds.currentTime(frame)  # 设置当前的时间滑块位置
                    cmds.arnoldExportAss(
                        f=ass_file, mask=255, lightLinks=1, boundingBox=1, shadowLinks=1, s=True,
                    )
            else:
                ass_file = os.path.join(
                    directory,
                    "{}_{}_{}_{}.ass".format(self.cmb_scene.currentText(), category, your_name, quality_suffix)
                )
                cmds.select(selected_objects)
                cmds.arnoldExportAss(
                    f=ass_file, mask=255, lightLinks=1, boundingBox=1, shadowLinks=1, s=True
                )
        # 更新进度条
        bar_num += 1
        self.cut_progressBar.setValue(bar_num)
        # 导出gpu
        self.export_abc(directory, category, your_name, quality_suffix, selected_objects)
        # 更新进度条
        bar_num += 1
        self.cut_progressBar.setValue(bar_num)
        # 导出diy
        self.export_diy(directory, category, your_name, quality_suffix, selected_objects)
        # 更新进度条
        bar_num += 1
        self.cut_progressBar.setValue(bar_num)
        # 导出gpu_BBOX
        self.export_bbox(directory, category, your_name, quality_suffix, selected_objects)
        # 更新进度条
        bar_num += 1
        self.cut_progressBar.setValue(bar_num)
        if self.jietu.isChecked():
            try:
                # 独立显示截图
                screenshot_file = os.path.join(
                    directory,
                    self.cmb_scene.currentText()
                    + "_"
                    + category
                    + "_"
                    + your_name
                    + "_"
                    + quality_suffix
                    + ".png",
                )


                if not os.path.exists(screenshot_file):
                    maya.mel.eval('ogs -pause;')

                    # 创建新的渲染层
                    render_layer = cmds.createRenderLayer(name='screenshot_layer', makeCurrent=True)

                    # 将选中的物体添加到新的渲染层
                    selected_and_descendants = cmds.listRelatives(selected_objects, allDescendents=True,
                                                                  fullPath=True) or []
                    selection_to_show = selected_objects + selected_and_descendants
                    cmds.editRenderLayerMembers(render_layer, selection_to_show)

                    cmds.viewFit()
                    cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
                    cmds.select(clear=True)

                    maya.mel.eval('ogs -pause;')


                    time.sleep(1)

                    cmds.playblast(
                        completeFilename=screenshot_file,
                        forceOverwrite=True,
                        format="image",
                        width=1024,
                        height=1024,
                        showOrnaments=False,
                        startTime=1,
                        endTime=1,
                        viewer=False,
                    )

                    cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')
                    cmds.delete(render_layer)
                else:
                    print(u"已存在渲染图，跳过屏幕截图: " + screenshot_file.decode('utf-8'))
            except RuntimeError as e:
                if 'textureUvTilingGeneratePreviewButton' in str(e):
                    print("Ignored error: ", e)
                else:
                    raise
            bar_num += 1
            self.cut_progressBar.setValue(bar_num)


        self.cut_progressBar.setValue(self.cut_progressBar.maximum())
        self.cut_progressBar.setValue(100)
        self.cut_progressBar.setFormat(u"完成")


def find_file_nodes(shader):
    file_nodes = []
    history = cmds.listHistory(shader, leaf=True)  # 获取材质节点的历史记录
    if history:
        for node in history:
            if cmds.nodeType(node) == 'file':  # 如果节点类型为 'file'，则添加到 file_nodes 列表
                file_nodes.append(node)
    return file_nodes


def resize_image_if_needed(file_path, quality_suffix):
    # 获取文件的扩展名
    file_extension = file_path.split('.')[-1]

    # 只处理 JPEG 和 PNG 格式的图片
    if file_extension not in ['jpeg', 'jpg', 'png']:
        print ("Image format %s is not supported. Skipping %s." % (file_extension, file_path))
        return

    if quality_suffix == "Low":
        img = Image.open(file_path)
        img = img.resize((1024, 1024), Image.ANTIALIAS)
        img.save(file_path)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


# 创建 MaterialExporter 实例并显示窗口
if __name__ == '__main__':
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    # 窗口的唯一名称
    window_name = "ExportWindow"

    # 如果窗口已存在，则删除
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)

    export_window = ExportWindow()
    export_window.setObjectName(window_name)  # 给窗口设置唯一名称
    export_window.show()

    app.exec_()