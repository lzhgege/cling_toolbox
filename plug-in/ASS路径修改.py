# -*- coding: utf-8 -*-
import maya.cmds as cmds
import os

def get_aiStandIn_nodes():
    """
    获取所有的 aiStandIn 节点列表，包括实例复制的节点
    """
    all_nodes = cmds.ls(selection=True)
    return all_nodes

def change_StandIn_path(new_path):
    """
    更改 aiStandIn 节点的路径
    """
    aiStandIn_nodes = get_aiStandIn_nodes()
    for node in aiStandIn_nodes:
        current_path = cmds.getAttr(node + '.dso')
        file_name = os.path.basename(current_path)
        new_full_path = os.path.join(new_path, file_name)
        cmds.setAttr(node + '.dso', new_full_path, type='string')

def create_ui():
    """
    创建Maya窗口UI
    """
    window_name = 'ChangePathWindow'
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    cmds.window(window_name, title=u'修改ASS路径', sizeable=False)
    cmds.columnLayout(adjustableColumn=True)
    
    cmds.text(label=u'新路径：')
    path_field = cmds.textField(text='', width=300)
    
    cmds.button(label=u'修改路径', command=lambda *args: modify_path(path_field))
    
    cmds.showWindow(window_name)

def modify_path(path_field):
    """
    从UI获取新路径并调用change_StandIn_path函数修改路径
    """
    new_path = cmds.textField(path_field, query=True, text=True)
    change_StandIn_path(new_path)

create_ui()
