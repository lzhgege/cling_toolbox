# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.mel as mel
from PySide2 import QtWidgets


class ParameterEditor(object):
    def __init__(self):
        # 创建控件
        self.window = cmds.window(title=u'批量属性修改', widthHeight=(400, 200))
        self.column_layout = cmds.columnLayout(adjustableColumn=True)
        self.preset_label = cmds.text(label=u'预设参数:')
        self.preset_optionmenu = cmds.optionMenu()
        cmds.menuItem(label=u'选择预设参数后点击加载按钮')
        cmds.menuItem(label=u'Aronld模型透明')
        cmds.menuItem(label=u'Aronld模型细分')

        self.load_button = cmds.button(label=u'加载', command=self.load_preset)
        cmds.setParent(self.column_layout)
        cmds.separator(height=10, style='single')
        cmds.setParent(self.column_layout)
        self.parameter_label = cmds.text(label=u'参数:')
        self.parameter_lineedit = cmds.textField()
        self.value_label = cmds.text(label=u'值:')
        self.value_spinbox = cmds.floatField(min=-100000.0, max=100000.0, step=0.1, value=1.0)
        self.apply_button = cmds.button(label=u'修改', command=self.apply_parameters)
        cmds.setParent(self.column_layout)
        cmds.separator(height=10, style='single')
        cmds.setParent(self.column_layout)
        self.info_label = cmds.text(label=u'打开脚本编辑器然后修改一下需要修改的物体参数并在脚本编辑器插件参数名')
        self.info_label = cmds.text(label=u'如Arnold的模型透明参数为aiOpaque,注意是小数点后面的名称')
        self.info_label = cmds.text(label=u'若是复选框的话值 1 就是开 0 就是关')
        cmds.showWindow(self.window)

    def load_preset(self, *args):
        preset = cmds.optionMenu(self.preset_optionmenu, q=True, value=True)
        if preset == u'选择预设参数后点击加载按钮':
            cmds.textField(self.parameter_lineedit, e=True, text='')
        elif preset == u'Aronld模型透明':
            cmds.textField(self.parameter_lineedit, e=True, text='aiOpaque')
        elif preset == u'Aronld模型细分':
            cmds.textField(self.parameter_lineedit, e=True, text='aiSubdivType')


    def apply_parameters(self, *args):
        parameter = cmds.textField(self.parameter_lineedit, q=True, text=True)
        value = cmds.floatField(self.value_spinbox, q=True, value=True)
        selected_objects = cmds.ls(selection=True)
        for obj in selected_objects:
            cmds.setAttr(obj + '.' + parameter, value)

        message = "{} objects updated with parameter: {}".format(len(selected_objects), parameter)
        cmds.text(self.info_label, e=True, label=message)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


if __name__ == '__main__':
    pe = ParameterEditor()