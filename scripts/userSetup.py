# -*- coding: utf-8 -*-
import sys
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken6 import wrapInstance
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
import maya.utils

# 设置环境变量的函数
def set_env_variable(path, env_var_name):
    if path not in os.environ.get(env_var_name, ''):
        os.environ[env_var_name] = path + ';' + os.environ.get(env_var_name, '')

# PIL模块路径设置
pil_module_path = r'D:\Cling_toolbox\external_library'
set_env_variable(pil_module_path, 'PYTHONPATH')

# Maya插件路径设置
maya_plug_path = r'D:/Cling_toolbox/plug-ins'
set_env_variable(maya_plug_path, 'MAYA_PLUG_IN_PATH')

# Maya脚本路径设置
maya_script_path = r'D:/Cling_toolbox/scripts'
set_env_variable(maya_script_path, 'MAYA_SCRIPT_PATH')

# Maya图标路径设置
xbmlangpath = r'D:/Cling_toolbox/icons'
set_env_variable(xbmlangpath, 'XBMLANGPATH')

# 定义程序名称
program_name = u'Cling_toolbox'

get_program_path = 'D:/Cling_toolbox'
get_script_dir = get_program_path

if get_script_dir not in sys.path:
    sys.path.append(get_script_dir)

def setup_program():
    # 检查并删除现有的UI元素
    if cmds.iconTextButton(program_name, ex=True):
        cmds.deleteUI(program_name)

    if cmds.menu('MayaWindow|MyToolboxMenu', ex=True):
        cmds.deleteUI('MayaWindow|MyToolboxMenu')

    # 创建iconTextButton
    cmds.iconTextButton(program_name, i=os.path.join(get_program_path, 'icons/button.png'),
                        c='exec(open("' + os.path.join(get_script_dir, 'scripts/Cling_toolbox.py') + '", encoding="utf-8").read())',
                        stp='python', hi=os.path.join(get_program_path, 'icons/button_hover.png'),
                        p=cmds.iconTextButton('statusFieldButton', q=True, p=True))

    create_toolbox_menu()

def create_toolbox_menu():
    menu_name = 'MyToolboxMenu'  # 选择一个唯一的菜单名称
    if cmds.menu(menu_name, exists=True):
        cmds.deleteUI(menu_name)  # 如果菜单已存在，则删除

    menu_item = cmds.menu(menu_name, label=u'Cling_toolbox', parent='MayaWindow')

    # 菜单项设置，确保执行Python脚本
    cmds.menuItem(label=u'打开工具箱',
                  command='exec(open("' + os.path.join(get_program_path, 'scripts/Cling_toolbox.py') + '", encoding="utf-8").read())', parent=menu_item)

    cmds.menuItem(label=u'添加资产目录',
                  command='exec(open("' + os.path.join(get_program_path, 'download/create_project.py') + '", encoding="utf-8").read())',
                  parent=menu_item)

    cmds.menuItem(label=u'资产库目录共享',
                  command='exec(open("' + os.path.join(get_program_path, 'download/project_renew.py') + '", encoding="utf-8").read())',
                  parent=menu_item)

    cmds.menuItem(label=u'材质库路径修改',
                  command='exec(open("' + os.path.join(get_program_path, 'download/Material_library_modify.py') + '", encoding="utf-8").read())',
                  parent=menu_item)

    cmds.menuItem(label=u'更新工具架',
                  command='exec(open("' + os.path.join(get_program_path, 'download/new.py') + '", encoding="utf-8").read())',
                  parent=menu_item)



if __name__ == "__main__":
    maya.utils.executeDeferred(setup_program)
