# -*- coding: utf-8 -*-
# 作者：cling
# 微信：clingkaka
# 个人主页：www.cg6i.com
# 模型下载：www.cgfml.com
# AI聊天绘画：ai.cgfml.com
# 此处部分功能借鉴HyperScene场景管理工具
# 敲码不易修改搬运请保留以上信息，感谢！！！！！
import os, datetime
import maya.OpenMayaUI as omui
import shiboken6
from shiboken6 import wrapInstance
import maya.cmds as cmds
from PySide6 import QtWidgets, QtGui, QtCore
import functools

import maya.OpenMayaUI as mui


def get_related_gpu_node(transform_node):
    related_nodes = cmds.listRelatives(transform_node, children=True, fullPath=True)
    if related_nodes:
        for node in related_nodes:
            if cmds.nodeType(node) == "gpuCache":
                return node
    return None

def get_related_standin_node(transform_node):
    related_nodes = cmds.listRelatives(transform_node, children=True, fullPath=True)
    if related_nodes:
        for node in related_nodes:
            if cmds.nodeType(node) == "aiStandIn":
                return node
    return None





class MayaUIWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MayaUIWindow, self).__init__()

        self.setWindowTitle(u"多功能切换")


        # 获取Maya主窗口
        main_window_ptr = mui.MQtUtil.mainWindow()
        main_window = shiboken6.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

        # 设置窗口大小和位置
        self.setGeometry(main_window.frameGeometry().width() // 2, main_window.frameGeometry().height() // 2, 400, 300)

        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)



        # 添加 sel_mod_selections 和 sel_mod_childs 勾选框
        sel_mod_layout = QtWidgets.QHBoxLayout()
        self.sel_mod_selections = QtWidgets.QCheckBox(u"选择物体", self)
        self.sel_mod_childs = QtWidgets.QCheckBox(u"包含子物体", self)
        self.sel_mod_all = QtWidgets.QCheckBox(u"all", self)
        self.sel_mod_childs.setEnabled(False)

        sel_mod_layout.addWidget(self.sel_mod_selections)
        sel_mod_layout.addWidget(self.sel_mod_childs)
        sel_mod_layout.addWidget(self.sel_mod_all)
        main_layout.addLayout(sel_mod_layout)

        # 初始化 unt_attr_dic 字典
        self.unt_attr_dic = {'ass': 'assShapePath',
                             'gpu': 'gpuShapePath',
                             'diy': 'gpuDIYPath',
                             'bbox': 'gpuBBoxPath',
                             'ma': 'maPath',
                             'usd': 'usdPath,'}

        # 创建与删除部分
        gpu_refacto_layout = QtWidgets.QHBoxLayout()  # 将布局改为垂直布局

        self.gpu_refacto_unt_tex = QtWidgets.QLabel(u"MA")
        self.gpu_refacto_refresh_but = QtWidgets.QPushButton(u"属性添加")
        self.gpu_refacto_ma_ref = QtWidgets.QPushButton(u"引用MA")
        self.gpu_refacto_ma_remove = QtWidgets.QPushButton(u"删除引用")

        self.gpu_refacto_refresh_but.clicked.connect(self.refresh_transform_node)
        self.gpu_refacto_ma_ref.clicked.connect(self.add_ref_maya)
        self.gpu_refacto_ma_remove.clicked.connect(self.del_ref_maya)

        gpu_refacto_layout.addWidget(self.gpu_refacto_unt_tex)
        gpu_refacto_layout.addWidget(self.gpu_refacto_refresh_but)
        gpu_refacto_layout.addWidget(self.gpu_refacto_ma_ref)
        gpu_refacto_layout.addWidget(self.gpu_refacto_ma_remove)

        self.gpu_refacto_grp = QtWidgets.QGroupBox(u"添加与删除")
        self.gpu_refacto_grp.setLayout(gpu_refacto_layout)

        main_layout.addWidget(self.gpu_refacto_grp)

        # 引用abc与删除部分
        abc_refacto_layout = QtWidgets.QHBoxLayout()  # 将布局改为水平布局

        self.abc_refacto_unt_tex = QtWidgets.QLabel(u"ABC")
        self.abc_refresh_bbox = QtWidgets.QPushButton(u"引用bbox")
        self.abc_refresh_diy = QtWidgets.QPushButton(u"引用diy")

        # 创建复选框
        self.gpu_refacto_checkbox = QtWidgets.QCheckBox(u"引用时删除GPU")
        self.ass_refacto_checkbox = QtWidgets.QCheckBox(u"删除ASS")

        abc_refacto_layout.addWidget(self.abc_refacto_unt_tex)
        abc_refacto_layout.addWidget(self.gpu_refacto_checkbox)
        abc_refacto_layout.addWidget(self.ass_refacto_checkbox)
        abc_refacto_layout.addWidget(self.abc_refresh_bbox)
        abc_refacto_layout.addWidget(self.abc_refresh_diy)


        abc_refacto_grp = QtWidgets.QGroupBox(u"")
        abc_refacto_grp.setLayout(abc_refacto_layout)

        self.abc_refresh_bbox.clicked.connect(self.add_ref_bbox)
        self.abc_refresh_diy.clicked.connect(self.add_ref_diy)



        # GPUcache操作部分
        gpu_refacto_layout_gpu = QtWidgets.QHBoxLayout()  # 将布局改为垂直布局
        self.gpu_refacto_gpu_tex = QtWidgets.QLabel(u"GPUcache ")
        self.gpu_refacto_gpu_add_bbox = QtWidgets.QPushButton(u"添加GPUcache(BBox形态优先)")
        self.gpu_refacto_gpu_add_bbox.clicked.connect(self.add_gpu_bbox_diy_gpu)
        self.gpu_refacto_gpu_del = QtWidgets.QPushButton(u"删除GPUcache")
        self.gpu_refacto_gpu_del.clicked.connect(self.del_gpucache_node)

        gpu_refacto_layout_gpu.addWidget(self.gpu_refacto_gpu_tex)
        gpu_refacto_layout_gpu.addWidget(self.gpu_refacto_gpu_add_bbox)
        gpu_refacto_layout_gpu.addWidget(self.gpu_refacto_gpu_del)

        gpu_refacto_grp_gpu = QtWidgets.QGroupBox(u"")
        gpu_refacto_grp_gpu.setLayout(gpu_refacto_layout_gpu)

        # ASS操作部分
        gpu_refacto_layout_ass = QtWidgets.QHBoxLayout()  # 将布局改为垂直布局
        self.gpu_refacto_ass_tex = QtWidgets.QLabel(u"ASS ")
        self.gpu_refacto_ass_add = QtWidgets.QPushButton(u"添加ASS节点(BBox线框形态)")
        self.gpu_refacto_ass_add.clicked.connect(self.add_ass_node)
        self.gpu_refacto_ass_del = QtWidgets.QPushButton(u"删除ASS节点")
        self.gpu_refacto_ass_del.clicked.connect(self.del_ass_node)

        gpu_refacto_layout_ass.addWidget(self.gpu_refacto_ass_tex)
        gpu_refacto_layout_ass.addWidget(self.gpu_refacto_ass_add)
        gpu_refacto_layout_ass.addWidget(self.gpu_refacto_ass_del)

        gpu_refacto_grp_ass = QtWidgets.QGroupBox(u"")
        gpu_refacto_grp_ass.setLayout(gpu_refacto_layout_ass)

        # 将上述三个部分放到一个水平布局中
        horizontal_layout = QtWidgets.QVBoxLayout()
        horizontal_layout.addWidget(self.gpu_refacto_grp)
        horizontal_layout.addWidget(abc_refacto_grp)
        horizontal_layout.addWidget(gpu_refacto_grp_gpu)
        horizontal_layout.addWidget(gpu_refacto_grp_ass)

        # 最后将水平布局添加到主布局中
        main_layout.addLayout(horizontal_layout)

        # Unt视口显示切换部分
        unt_display_change_layout = QtWidgets.QHBoxLayout()
        self.unt_display_change_grp = QtWidgets.QGroupBox(u"显示切换")
        self.cut_to = QtWidgets.QLabel(u"GPU形态切换")
        self.gpu_bbox = QtWidgets.QPushButton(u"GPUcache_BBox")
        self.gpu_diy = QtWidgets.QPushButton(u"GPUcache_DIY")
        self.gpu_geo = QtWidgets.QPushButton(u"GPUcache高模")

        self.gpu_bbox.clicked.connect(functools.partial(self.change_gpu_display, "bbox"))
        self.gpu_diy.clicked.connect(functools.partial(self.change_gpu_display, "diy"))
        self.gpu_geo.clicked.connect(functools.partial(self.change_gpu_display, "gpu"))

        unt_display_change_layout.addWidget(self.cut_to)
        unt_display_change_layout.addWidget(self.gpu_bbox)
        unt_display_change_layout.addWidget(self.gpu_diy)
        unt_display_change_layout.addWidget(self.gpu_geo)

        self.unt_display_change_grp.setLayout(unt_display_change_layout)
        main_layout.addWidget(self.unt_display_change_grp)

        # 添加版本切换的布局和控件
        version_frame = QtWidgets.QGroupBox(u"版本切换")
        version_layout = QtWidgets.QVBoxLayout(version_frame)

        self.suffix_text_field = QtWidgets.QLineEdit()
        self.suffix_text_field.setPlaceholderText(u"自定义版本后缀")

        self.suffix_dropdown = QtWidgets.QComboBox()
        self.suffix_dropdown.addItem(u"请选择版本后缀:")
        preset_suffixes = ["Low", "High", "Sim"]
        for suffix in preset_suffixes:
            self.suffix_dropdown.addItem(suffix)

        # 使用 lambda 函数创建一个带参数的函数并将其连接到按钮的点击事件
        switch_button = QtWidgets.QPushButton(u"版本切换")
        # 使用 functools.partial 创建一个带参数的函数并将其连接到按钮的点击事件
        switch_button.clicked.connect(functools.partial(self.switch_files, self))

        version_layout.addWidget(self.suffix_text_field)
        version_layout.addWidget(self.suffix_dropdown)
        version_layout.addWidget(switch_button)

        main_layout.addWidget(version_frame)
        self.setLayout(main_layout)

    def switch_files(self, *args):
        custom_suffix = self.suffix_text_field.text()
        preset_suffix = self.suffix_dropdown.currentText()

        if custom_suffix:
            suffix = custom_suffix
            if suffix not in [self.suffix_dropdown.itemText(i) for i in range(self.suffix_dropdown.count())]:
                self.suffix_dropdown.addItem(suffix)
            self.suffix_text_field.clear()
        else:
            suffix = preset_suffix

        selected_nodes = cmds.ls(selection=True)
        if not selected_nodes:
            cmds.warning(u"请选择一个变换节点来切换文件。")
            return
        self.gpu_geo.click()

        error_list = []
        for transform_node in selected_nodes:
            file_exists = False

            gpu_node = get_related_gpu_node(transform_node)
            standin_node = get_related_standin_node(transform_node)

            if gpu_node:
                current_file_path = cmds.getAttr('{}.cacheFileName'.format(gpu_node))
                base_name, file_extension = os.path.splitext(os.path.basename(current_file_path))
                base_name_parts = base_name.split("_")

                if suffix == "BBOX" or suffix == "diy":
                    base_name_parts[-2] = suffix
                else:
                    base_name_parts[-1] = suffix

                new_base_name = "_".join(base_name_parts)
                new_file_path = os.path.join(os.path.dirname(current_file_path), new_base_name + file_extension)

                if os.path.exists(new_file_path):
                    cmds.setAttr('{}.cacheFileName'.format(gpu_node), new_file_path, type='string')
                    file_exists = True
                else:
                    error_list.append(transform_node)

            if standin_node:
                current_file_path = cmds.getAttr('{}.dso'.format(standin_node))
                file_in_Sim_folder = "/Sim/" in current_file_path
                # If the file is inside the /Sim/ folder, we will not use sequence
                if file_in_Sim_folder or not current_file_path.endswith(".ass"):
                    base_name, file_extension = os.path.splitext(os.path.basename(current_file_path))
                else:
                    # The file is a sequence
                    base_name = os.path.basename(current_file_path).rsplit('.', 2)[0]

                base_name_parts = base_name.split("_")

                if suffix == "BBOX" or suffix == "diy":
                    base_name_parts[-2] = suffix
                else:
                    base_name_parts[-1] = suffix

                new_base_name = "_".join(base_name_parts)

                if file_in_Sim_folder or not current_file_path.endswith(".ass"):
                    new_file_name = new_base_name + file_extension
                else:
                    new_file_name = new_base_name + '.0001.ass'

                new_file_path = os.path.join(os.path.dirname(current_file_path), new_file_name)

                # Check if the file path already contains the "/Sim/" subdirectory
                if file_in_Sim_folder:
                    parent_folder_path = os.path.dirname(os.path.dirname(current_file_path))
                    upper_level_file_path = os.path.join(parent_folder_path, new_file_name)
                    additional_check_path = upper_level_file_path
                else:
                    sim_folder_path = os.path.join(os.path.dirname(current_file_path), "Sim",
                                                   new_file_name)
                    additional_check_path = sim_folder_path

                if os.path.exists(new_file_path):
                    cmds.setAttr('{}.dso'.format(standin_node), new_file_path, type='string')
                    file_exists = True
                elif os.path.exists(additional_check_path):
                    cmds.setAttr('{}.dso'.format(standin_node), additional_check_path, type='string')
                    file_exists = True
                    if file_in_Sim_folder:
                        cmds.setAttr('{}.useFrameExtension'.format(standin_node), 1)
                else:
                    if transform_node not in error_list:
                        error_list.append(transform_node)

            if file_exists:
                current_name = cmds.ls(transform_node, int=True)[-1].split('|')[-1]
                name_parts = current_name.split('_')
                name_parts[-3] = suffix
                new_name = '_'.join(name_parts)
                cmds.rename(transform_node, new_name)

        self.refresh_transform_node()
        self.gpu_bbox.click()

        if error_list:
            # 只获取前三条错误信息
            limited_error_list = error_list[:3]
            message = '\n'.join(limited_error_list)

            # 计算实际错误数量
            error_count = len(error_list)
            if cmds.confirmDialog(title=u'警告!!', icon='question',
                                  message=u"以下{}个物体切换失败\n{}".format(error_count, message),
                                  button=[u'选择出错物体', u'关闭']) == u'选择出错物体':
                cmds.select(error_list, r=1)



    def return_select_obj(self, objtype):
        # 如果选择了物体，自动切换为所选
        if cmds.ls(sl=1):
            self.sel_mod_selections.setChecked(True)
            self.sel_mod_childs.setEnabled(True)
        aimobj_list = []
        if self.sel_mod_selections.isChecked():  # 选择的物体
            # 是否包含子物体
            if self.sel_mod_childs.isChecked():
                cmds.select(hi=1)
            for item in cmds.ls(sl=1, l=1):
                if cmds.objectType(item) == objtype:
                    if not item in aimobj_list:
                        aimobj_list.append(item)
                child_list = cmds.listRelatives(item, c=1, pa=1, f=1)
                if child_list:
                    for ite in child_list:
                        if cmds.objectType(ite) == objtype:
                            if not ite in aimobj_list:
                                aimobj_list.append(ite)
        elif self.sel_mod_all.isChecked():  # 所有物体
            aimobj_list = cmds.ls(l=1, type=objtype)

        # cmds.select(cl=1)
        return aimobj_list

    def refresh_transform_node(self):
        # 开始时间
        begin = datetime.datetime.now()

        sel_trs_nodes = self.return_select_obj("transform")

        if sel_trs_nodes:
            if len(sel_trs_nodes) > 2000:
                if cmds.confirmDialog(title=u'警告!!', icon='question',
                                      message=u'操作队列超过2000个物体，\n需要等待时间大于50秒，\n是否继续？',
                                      button=[u'继续', u'取消']) == u'取消':
                    return

            for sel_node in sel_trs_nodes:
                if cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache"):
                    gpunode = cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache")
                    if len(gpunode) == 1:
                        gpu_path = cmds.getAttr(gpunode[0] + ".cacheFileName")
                        file_dic = self.return_unt_fullpath(gpu_path)
                        # 删除有属性
                        self.del_refresh_unt_attr(sel_node)
                        # 添加属性
                        self.add_refresh_unt_attr(sel_node, file_dic)
                        # 颜色
                        color = self.return_unt_color(file_dic)
                        self.set_object_outline_color(sel_node, color)

            # 运行时间
            end = datetime.datetime.now()


    def add_ref_maya(self):
        if self.gpu_refacto_checkbox.isChecked():
            self.del_gpucache_node()
        if self.ass_refacto_checkbox.isChecked():
            self.del_ass_node()
        if self.sel_mod_all.isChecked():
            cmds.confirmDialog(title=u'警告!!', icon='question', message=u"禁止选择All，添加ma文件",
                               button=[u'关闭'])
            return
        else:
            sel_obj_list = self.return_select_obj("transform")
            unt_list = []
            for i in sel_obj_list:
                if self.return_unt_bool(i):
                    unt_list.append(i)

            for selobj in unt_list:

                print (u"添加ref Maya文件", selobj)

                try:
                    # 获取属性
                    ma_path = cmds.getAttr(selobj + "." + self.unt_attr_dic['ma'])
                    print (u"----->>开始Ref Maya文件", ma_path)

                    if os.path.exists(ma_path):  # 文件是否存在
                        ns = ma_path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                        grp_name = selobj.rsplit("|", 1)[-1] + "_ma"
                        refnode = cmds.file(ma_path, r=1, type="mayaAscii", mergeNamespacesOnClash=False,
                                            namespace=ns,
                                            gr=1, gn=grp_name)
                        grp_name = cmds.ls(sl=1, l=1)[0]
                        # 设置xform
                        cmds.xform(selobj, rp=[0, 0, 0])
                        cmds.xform(selobj, sp=[0, 0, 0])
                        cmds.xform(grp_name, rp=[0, 0, 0])
                        cmds.xform(grp_name, sp=[0, 0, 0])
                        # 锁定属性
                        cmds.setAttr((grp_name + ".tx"), l=1)
                        cmds.setAttr((grp_name + ".ty"), l=1)
                        cmds.setAttr((grp_name + ".tz"), l=1)
                        cmds.setAttr((grp_name + ".rx"), l=1)
                        cmds.setAttr((grp_name + ".ry"), l=1)
                        cmds.setAttr((grp_name + ".rz"), l=1)
                        cmds.setAttr((grp_name + ".sx"), l=1)
                        cmds.setAttr((grp_name + ".sy"), l=1)
                        cmds.setAttr((grp_name + ".sz"), l=1)
                        cmds.setAttr((grp_name + ".v"), l=1)
                        try:
                            if not cmds.listRelatives(selobj, c=1, pa=1, f=1):
                                cmds.setAttr((cmds.createNode("transform", n=self.return_new_shapename("loc_pos"),
                                                              p=selobj) + ".visibility"), 0)
                            cmds.parent(grp_name, selobj)
                        except:
                            print (u"{}:----->>移动失败，开始remove".format(datetime.datetime.now()))

                            cmds.file(refnode, rr=1)

                    else:
                        print (u"----->>maya文件不存在{}".format(ma_path))

                except:
                    print (u"----->>获取maPath属性失败")

    def add_ref_bbox(self):
        if self.gpu_refacto_checkbox.isChecked():
            self.del_gpucache_node()
        if self.ass_refacto_checkbox.isChecked():
            self.del_ass_node()
        if self.sel_mod_all.isChecked():
            cmds.confirmDialog(title=u'警告!!', icon='question', message=u"禁止选择All，添加abc文件",
                               button=[u'关闭'])
            return
        else:
            sel_obj_list = self.return_select_obj("transform")
            unt_list = []
            for i in sel_obj_list:
                if self.return_unt_bool(i):
                    unt_list.append(i)

            for selobj in unt_list:

                print(u"添加ref Alembic文件", selobj)

                try:
                    # 获取属性
                    abc_path = cmds.getAttr(selobj + "." + self.unt_attr_dic['bbox'])
                    print(u"----->>开始Ref Alembic文件", abc_path)

                    if os.path.exists(abc_path):  # 文件是否存在
                        ns = abc_path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                        grp_name = selobj.rsplit("|", 1)[-1] + "_BBOX"
                        refnode = cmds.file(abc_path, r=1, type="Alembic", mergeNamespacesOnClash=False,
                                            namespace=ns,
                                            gr=1, gn=grp_name)
                        grp_name = cmds.ls(sl=1, l=1)[0]
                        # 设置xform
                        cmds.xform(selobj, rp=[0, 0, 0])
                        cmds.xform(selobj, sp=[0, 0, 0])
                        cmds.xform(grp_name, rp=[0, 0, 0])
                        cmds.xform(grp_name, sp=[0, 0, 0])
                        # 锁定属性
                        cmds.setAttr((grp_name + ".tx"), l=1)
                        cmds.setAttr((grp_name + ".ty"), l=1)
                        cmds.setAttr((grp_name + ".tz"), l=1)
                        cmds.setAttr((grp_name + ".rx"), l=1)
                        cmds.setAttr((grp_name + ".ry"), l=1)
                        cmds.setAttr((grp_name + ".rz"), l=1)
                        cmds.setAttr((grp_name + ".sx"), l=1)
                        cmds.setAttr((grp_name + ".sy"), l=1)
                        cmds.setAttr((grp_name + ".sz"), l=1)
                        cmds.setAttr((grp_name + ".v"), l=1)
                        try:
                            if not cmds.listRelatives(selobj, c=1, pa=1, f=1):
                                cmds.setAttr((cmds.createNode("transform", n=self.return_new_shapename("loc_pos"),
                                                              p=selobj) + ".visibility"), 0)
                            cmds.parent(grp_name, selobj)
                        except:
                            print
                            (u"{}:----->>移动失败，开始remove".format(datetime.datetime.now()))

                            cmds.file(refnode, rr=1)

                    else:
                        print
                        (u"----->>maya文件不存在{}".format(ma_path))

                except:
                    print
                    (u"----->>获取maPath属性失败")

    def add_ref_diy(self):
        if self.gpu_refacto_checkbox.isChecked():
            self.del_gpucache_node()
        if self.ass_refacto_checkbox.isChecked():
            self.del_ass_node()
        if self.sel_mod_all.isChecked():
            cmds.confirmDialog(title=u'警告!!', icon='question', message=u"禁止选择All，添加abc文件",
                               button=[u'关闭'])
            return
        else:
            sel_obj_list = self.return_select_obj("transform")
            unt_list = []
            for i in sel_obj_list:
                if self.return_unt_bool(i):
                    unt_list.append(i)

            for selobj in unt_list:

                print(u"添加ref Alembic文件", selobj)

                try:
                    # 获取属性
                    abc_path = cmds.getAttr(selobj + "." + self.unt_attr_dic['diy'])
                    print(u"----->>开始Ref Alembic文件", abc_path)

                    if os.path.exists(abc_path):  # 文件是否存在
                        ns = abc_path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                        grp_name = selobj.rsplit("|", 1)[-1] + "_diy"
                        refnode = cmds.file(abc_path, r=1, type="Alembic", mergeNamespacesOnClash=False,
                                            namespace=ns,
                                            gr=1, gn=grp_name)
                        grp_name = cmds.ls(sl=1, l=1)[0]
                        # 设置xform
                        cmds.xform(selobj, rp=[0, 0, 0])
                        cmds.xform(selobj, sp=[0, 0, 0])
                        cmds.xform(grp_name, rp=[0, 0, 0])
                        cmds.xform(grp_name, sp=[0, 0, 0])
                        # 锁定属性
                        cmds.setAttr((grp_name + ".tx"), l=1)
                        cmds.setAttr((grp_name + ".ty"), l=1)
                        cmds.setAttr((grp_name + ".tz"), l=1)
                        cmds.setAttr((grp_name + ".rx"), l=1)
                        cmds.setAttr((grp_name + ".ry"), l=1)
                        cmds.setAttr((grp_name + ".rz"), l=1)
                        cmds.setAttr((grp_name + ".sx"), l=1)
                        cmds.setAttr((grp_name + ".sy"), l=1)
                        cmds.setAttr((grp_name + ".sz"), l=1)
                        cmds.setAttr((grp_name + ".v"), l=1)
                        try:
                            if not cmds.listRelatives(selobj, c=1, pa=1, f=1):
                                cmds.setAttr((cmds.createNode("transform", n=self.return_new_shapename("loc_pos"),
                                                              p=selobj) + ".visibility"), 0)
                            cmds.parent(grp_name, selobj)
                        except:
                            print
                            (u"{}:----->>移动失败，开始remove".format(datetime.datetime.now()))

                            cmds.file(refnode, rr=1)

                    else:
                        print
                        (u"----->>maya文件不存在{}".format(ma_path))

                except:
                    print
                    (u"----->>获取maPath属性失败")

    def return_unt_bool(self, transform_node):
        return_list = []
        for obj_atter in self.unt_attr_dic.values():
            try:
                if cmds.getAttr(transform_node + "." + obj_atter) != "":
                    return_list.append(True)
            except:
                return_list.append(False)
        if True in return_list:
            return True
        else:
            return False

    def del_ref_maya(self):
        if self.sel_mod_all.isChecked():
            cmds.confirmDialog(title=u'警告!!', icon='question', message=u"禁止选择All，添加ma文件",
                               button=[u'关闭'])
            return
        else:
            try:
                sel_obj = self.return_select_obj("transform")
                refnode_list = []
                for i in sel_obj:
                    ref_node = cmds.referenceQuery(i, rfn=1)
                    if not ref_node in refnode_list:
                        refnode_list.append(ref_node)
                for refnode in refnode_list:
                    filepath = cmds.referenceQuery(refnode, f=1)
                    cmds.file(filepath, rr=1, f=1)
            except:
                cmds.confirmDialog(title=u'警告!!', icon='question', message=u"选择的节点不是ref节点",
                                   button=[u'关闭'])
                return

    def add_gpu_bbox_diy_gpu(self):
        begin = datetime.datetime.now()

        # 获取选择物体
        return_sel = cmds.ls(sl=1, l=1)
        select_node_list = self.return_select_obj('transform')
        # 过滤unt
        new_list = []
        if select_node_list:
            for sel_node in select_node_list:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        select_node_list = new_list
        # 增加节点
        if select_node_list:

            for sel_node in select_node_list:
                print (sel_node)

                gpu_shape_path = ""
                try:
                    gpu_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic['bbox'])
                except:
                    try:
                        gpu_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic['diy'])
                    except:
                        try:
                            gpu_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic['gpu'])
                        except:
                            print (u"----->>获取gpuShapePath属性失败")

                            continue
                # 获取属性
                if not cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache"):
                    if os.path.exists(gpu_shape_path):  # abc文件是否存在
                        short_name = gpu_shape_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]
                        # 创建GPUcache节点
                        gpu_node = cmds.createNode("gpuCache", p=sel_node)
                        # 设置路径
                        cmds.setAttr((gpu_node + ".cacheFileName"), gpu_shape_path, type="string")
                        cmds.setAttr((gpu_node + ".cacheGeomPath"), "|", type="string")
                        # 设置属性
                        self.set_gpucache_attr(gpu_node, False)
                        # 设置顺序
                        if len(cmds.listRelatives(sel_node, c=1, pa=1, s=1)) > 1:
                            cmds.reorder(gpu_node, f=1)
                        # 重命名shape节点
                        shapename = "GPU_" + ''.join(filter(str.isalnum, str(short_name + 'Shape')))
                        new_name = self.return_new_shapename(shapename)
                        gpuNod = cmds.rename(gpu_node, new_name)
                    else:
                        print (u"----->>删除失败{}".format(gpu_shape_path))

                else:
                    print (u"----->>已经存在gpuCache")

        # 维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print (end - begin)

    ####返回一个场景中没有重名的名字
    def return_new_shapename(self, shapename):
        int_list = [0]
        for i in cmds.ls(shapename + "__*"):
            try:
                int_list.append(int(i.rsplit("_", 1)[-1]))
            except:
                pass
        new_list = sorted(int_list)
        return '''{}__{}'''.format(shapename, (new_list[-1] + 1))

    def add_gpucache_node(self, gpu_type):
        begin = datetime.datetime.now()

        # 获取选择物体
        return_sel = cmds.ls(sl=1, l=1)
        select_node_list = self.return_select_obj('transform')
        # 过滤unt
        new_list = []
        if select_node_list:
            for sel_node in select_node_list:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        select_node_list = new_list
        # 增加节点
        if select_node_list:

            for sel_node in select_node_list:
                print (sel_node)

                gpu_shape_path = ""
                try:
                    # 获取属性
                    gpu_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic[gpu_type])
                    if not cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache"):
                        if os.path.exists(gpu_shape_path):  # abc文件是否存在
                            short_name = gpu_shape_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]
                            # 创建GPUcache节点
                            gpu_node = cmds.createNode("gpuCache", p=sel_node)
                            # 设置路径
                            cmds.setAttr((gpu_node + ".cacheFileName"), gpu_shape_path, type="string")
                            cmds.setAttr((gpu_node + ".cacheGeomPath"), "|", type="string")
                            # 设置属性
                            self.set_gpucache_attr(gpu_node, False)
                            # 设置顺序
                            if len(cmds.listRelatives(sel_node, c=1, pa=1, s=1)) > 1:
                                cmds.reorder(gpu_node, f=1)
                            # 重命名shape节点
                            shapename = "GPU_" + ''.join(filter(str.isalnum, str(short_name + 'Shape')))
                            new_name = self.return_new_shapename(shapename)
                            gpuNod = cmds.rename(gpu_node, new_name)
                        else:
                            print (u"----->>未找到文件{}".format(gpu_shape_path))

                    else:
                        print (u"----->>已经存在gpuCache")

                except:
                    print (u"----->>获取gpuShapePath属性失败")

        # 维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print (end - begin)

    def set_gpucache_attr(self, gpu_shape_node, on_off):
        if on_off:
            cmds.setAttr((gpu_shape_node + ".castsShadows"), 1)
            cmds.setAttr((gpu_shape_node + ".receiveShadows"), 1)
            cmds.setAttr((gpu_shape_node + ".motionBlur"), 1)
            cmds.setAttr((gpu_shape_node + ".primaryVisibility"), 1)
            cmds.setAttr((gpu_shape_node + ".smoothShading"), 1)
            cmds.setAttr((gpu_shape_node + ".visibleInReflections"), 0)
            cmds.setAttr((gpu_shape_node + ".visibleInRefractions"), 0)
            cmds.setAttr((gpu_shape_node + ".doubleSided"), 1)
            cmds.setAttr((gpu_shape_node + ".geometryAntialiasingOverride"), 0)

            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseReflection"), 1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularReflection"), 1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseTransmission"), 1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularTransmission"), 1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInVolume"), 1)
        else:
            cmds.setAttr((gpu_shape_node + ".castsShadows"), 0)
            cmds.setAttr((gpu_shape_node + ".receiveShadows"), 0)
            cmds.setAttr((gpu_shape_node + ".motionBlur"), 0)
            cmds.setAttr((gpu_shape_node + ".primaryVisibility"), 0)
            cmds.setAttr((gpu_shape_node + ".smoothShading"), 0)
            cmds.setAttr((gpu_shape_node + ".visibleInReflections"), 0)
            cmds.setAttr((gpu_shape_node + ".visibleInRefractions"), 0)
            cmds.setAttr((gpu_shape_node + ".doubleSided"), 0)
            cmds.setAttr((gpu_shape_node + ".geometryAntialiasingOverride"), 0)

            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseReflection"), 0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularReflection"), 0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseTransmission"), 0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularTransmission"), 0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInVolume"), 0)

    def del_gpucache_node(self):
        begin = datetime.datetime.now()
        delete_list = []

        # 获取选择物体
        return_sel = cmds.ls(sl=1, l=1)
        gpucachelist = self.return_select_obj('transform')
        # 过滤unt
        new_list = []
        if gpucachelist:
            for sel_node in gpucachelist:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        gpucachelist = new_list
        # 删除有属性的节点
        if gpucachelist:

            for item in gpucachelist:
                print (item)

                if self.return_unt_bool(item):
                    _c = cmds.listRelatives(item, c=1, pa=1, f=1, type="gpuCache")
                    if _c:
                        delete_list = (delete_list + _c)
                else:
                    print (u"----->>不是组件")

        cmds.delete(delete_list)
        # 维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print (end - begin)

    def add_ass_node(self):
        begin = datetime.datetime.now()
        # 获取选择物体
        return_sel = cmds.ls(sl=1, l=1)
        error_list = []
        select_node_list = self.return_select_obj('transform')
        # 过滤unt
        new_list = []
        if select_node_list:
            for sel_node in select_node_list:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        select_node_list = new_list
        # 增加节点
        if select_node_list:

            for sel_node in select_node_list:
                print (sel_node)

                ass_shape_path = ""
                try:
                    # 获取属性
                    ass_shape_path = cmds.getAttr(sel_node + ".assShapePath")
                    if not cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="aiStandIn"):
                        if os.path.exists(ass_shape_path):  # abc文件是否存在
                            short_name = ass_shape_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]
                            # 创建Asscache节点
                            ass_node = cmds.createNode("aiStandIn", p=sel_node)
                            # 设置属性
                            cmds.setAttr((ass_node + ".standInDrawOverride"), 0)
                            # 设置路径
                            cmds.setAttr((ass_node + ".dso"), ass_shape_path, type="string")
                            # rename node
                            #
                            shapename = "ASS_" + ''.join(filter(str.isalnum, str(short_name + 'Shape')))
                            new_name = self.return_new_shapename(shapename)
                            assNod = cmds.rename(ass_node, new_name)
                        else:
                            print (u"----->>未找到文件{}".format(ass_shape_path))

                    else:
                        print (u"----->>已经存在aiStandIn")

                except:
                    print (u"----->>获取assShapePath属性失败")

        # 维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print (end - begin)

    def del_ass_node(self):
        begin = datetime.datetime.now()
        delete_list = []

        # 获取选择物体
        return_sel = cmds.ls(sl=1, l=1)
        asscachelist = self.return_select_obj('transform')
        # 过滤unt
        new_list = []
        if asscachelist:
            for sel_node in asscachelist:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        asscachelist = new_list
        # 删除有属性的节点
        if asscachelist:

            for item in asscachelist:
                print (item)

                if self.return_unt_bool(item):
                    _c = cmds.listRelatives(item, c=1, pa=1, f=1, type="aiStandIn")
                    if _c:
                        delete_list = (delete_list + _c)
                else:
                    print (u"----->>不是组件")

        cmds.delete(delete_list)
        # 维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print (end - begin)

    def change_gpu_display(self, gpu_type):
        return_sel = cmds.ls(sl=1, l=1)
        # 获取选择物体
        sel_transform_list = self.return_select_obj('transform')
        error_list = []
        errpr_obj = []
        # 设置属性

        for sel_node in sel_transform_list:

            if not self.return_unt_bool(sel_node):
                continue
            try:
                # 获取属性
                file_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic[gpu_type])
                gpu_shape = cmds.listRelatives(sel_node, c=1, f=1, type="gpuCache")
                if os.path.exists(file_path):
                    if gpu_shape:
                        cmds.setAttr((gpu_shape[0] + ".cacheFileName"), file_path, type="string")
                    else:
                        error_list.append((sel_node + u"未发现GPU节点"))

                        errpr_obj.append(sel_node)
                else:
                    error_list.append((sel_node + u"文件不存在"))

                    errpr_obj.append(sel_node)
            except:
                error_list.append((sel_node + u"未找到属性" + self.unt_attr_dic[gpu_type]))

                errpr_obj.append(sel_node)

        if error_list:
            message = ""
            if len(error_list) > 3:
                for i in range(3):
                    message += (error_list[i] + "\n")
            else:
                for i in error_list:
                    message += (i + "\n")
            message += "\n ......"
            if cmds.confirmDialog(title=u'警告!!', icon='question',
                                  message=u"以下{}个物体切换失败\n{}".format(len(error_list), message),
                                  button=[u'选择出错物体', u'关闭']) == u'选择出错物体':
                cmds.select(errpr_obj, r=1)
                return

        # 维持选择
        cmds.select(return_sel, r=1)

    def return_unt_fullpath(self, filepath):
        filepath_dic = {}
        if filepath.endswith("_BBox.abc") or filepath.endswith("_DIY.abc"):
            gpu_path = filepath.rsplit("_", 1)[0] + ".abc"
            ass_path = filepath.rsplit("_", 1)[0] + ".ass"
            bbox_path = filepath.rsplit("_", 1)[0] + "_BBox.abc"
            diy_path = filepath.rsplit("_", 1)[0] + "_DIY.abc"
            ma_path = filepath.rsplit("_", 1)[0] + ".ma"
            if os.path.exists(gpu_path):
                filepath_dic["gpu"] = gpu_path
            if os.path.exists(ass_path):
                filepath_dic["ass"] = ass_path
            if os.path.exists(bbox_path):
                filepath_dic["bbox"] = bbox_path
            if os.path.exists(diy_path):
                filepath_dic["diy"] = diy_path
            if os.path.exists(ma_path):
                filepath_dic["ma"] = ma_path
            return filepath_dic
        else:
            gpu_path = filepath.rsplit(".", 1)[0] + ".abc"
            ass_path = filepath.rsplit(".", 1)[0] + ".ass"
            bbox_path = filepath.rsplit(".", 1)[0] + "_BBox.abc"
            diy_path = filepath.rsplit(".", 1)[0] + "_DIY.abc"
            ma_path = filepath.rsplit(".", 1)[0] + ".ma"
            if os.path.exists(gpu_path):
                filepath_dic["gpu"] = gpu_path
            if os.path.exists(ass_path):
                filepath_dic["ass"] = ass_path
            if os.path.exists(bbox_path):
                filepath_dic["bbox"] = bbox_path
            if os.path.exists(diy_path):
                filepath_dic["diy"] = diy_path
            if os.path.exists(ma_path):
                filepath_dic["ma"] = ma_path
        return filepath_dic

    def del_refresh_unt_attr(self, sel_node):
        for del_attr in self.unt_attr_dic.values():
            try:
                cmds.setAttr((sel_node + "." + del_attr), l=0)
                cmds.deleteAttr(sel_node, attribute=del_attr)
            except:
                print (u"----->>{}---未找到".format(sel_node + "." + del_attr))

    def set_object_outline_color(self, obj, color_list):
        cmds.setAttr((obj + ".useOutlinerColor"), 1)
        cmds.setAttr((obj + ".outlinerColor"), color_list[0], color_list[1], color_list[2])

    def add_refresh_unt_attr(self, sel_node, file_dic):
        for attr, filepath in file_dic.items():
            try:
                # 获取属性
                ass_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic[attr])
                print (u"----->>检测到属性{}".format(self.unt_attr_dic[attr]))

                # 如果文件路径与属性路径不通，更新属性路径
                if filepath != ass_shape_path:
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]), l=0)
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]), filepath, type="string")
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]), l=1)
                    print (u"----->>更新属性{}".format(self.unt_attr_dic[attr]))

                else:
                    print (u"{}:----->>{}属性正确".format(datetime.datetime.now(), self.unt_attr_dic[attr]))

                    # 锁定属性
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]), l=1)
            except:
                # 没有属性，创建
                try:
                    cmds.addAttr(sel_node, longName=self.unt_attr_dic[attr], dataType='string')
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]), filepath, type="string")
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]), l=1)
                    print (u"----->>添加属性{}".format(self.unt_attr_dic[attr]))

                except:
                    print (u"----->>{}添加失败".format(self.unt_attr_dic[attr]))

    def return_unt_color(self, file_dic):
        if len(file_dic) == 3 and "ass" in file_dic and "gpu" in file_dic and "bbox" in file_dic:
            return [0.74, 1, 1]
        elif len(file_dic) == 4 and "ass" in file_dic and "gpu" in file_dic and "bbox" in file_dic and "ma" in file_dic:
            return [0.91, 1, 0.91]
        elif len(
                file_dic) == 5 and "ass" in file_dic and "gpu" in file_dic and "bbox" in file_dic and "diy" in file_dic and "ma" in file_dic:
            return [0.91, 0.85, 1]
        else:
            return [1, 0.91, 0.91]

    def showUI(self):
        # Maya中的窗口常常需要这样处理，确保不会重复创建
        if cmds.window("MayaUIExample", exists=True):
            cmds.deleteUI("MayaUIExample", window=True)

        # 将这个QWidget转换为Maya窗口
        ptr = mui.MQtUtil.mainWindow()
        main_window = shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)
        self.setParent(main_window, QtCore.Qt.Window)

        # 显示窗口
        self.show()


# 创建 MaterialExporter 实例并显示窗口
if __name__ == '__main__':
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

