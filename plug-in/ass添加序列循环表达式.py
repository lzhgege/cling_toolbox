# -*- coding: utf-8 -*-

import maya.cmds as cmds
import random

def create_window():
    # 如果已存在同名窗口，先删除
    if cmds.window("myWindow", exists=True):
        cmds.deleteUI("myWindow", window=True)

    # 创建新窗口
    myWindow = cmds.window("myWindow", title=u"更改aiStandIn节点路径", widthHeight=(290, 200))

    # 创建窗口布局
    cmds.columnLayout(adjustableColumn=True)

    # 创建一个文本框和一个按钮用于选择 .ass 文件路径
    cmds.rowLayout(numberOfColumns=2)
    new_path_field = cmds.textField(placeholderText=u'新的.ass文件路径', width=240)
    cmds.button(label=u'选择路径', command=lambda x: cmds.textField(
        new_path_field, edit=True, text=cmds.fileDialog2(fileMode=1, caption=u"选择 .ass 文件")[0]))
    cmds.setParent('..')

    # 创建一个按钮用于更改路径
    cmds.button(label=u'更改路径', command=lambda x: change_StandIn_path(
        cmds.textField(new_path_field, query=True, text=True)
    ))

    # 创建一个columnLayout来包含文本框和按钮，并设置对齐方式为左对齐
    cmds.columnLayout(columnAlign='left')
    start_frame_field = cmds.intFieldGrp('start_frame_field', label=u'起始帧', value1=1)
    end_frame_field = cmds.intFieldGrp('end_frame_field', label=u'结束帧', value1=200)
    cmds.button(label=u'添加表达式', command=lambda x: add_expression(
        cmds.intFieldGrp(start_frame_field, query=True, value1=True),
        cmds.intFieldGrp(end_frame_field, query=True, value1=True)
    ))
    cmds.setParent('..')

    # 显示窗口
    cmds.showWindow(myWindow)

def update_text_field(text_field):
    """
    更新文本框中的路径
    """
    file_path = cmds.fileDialog2(fileMode=1, caption=u"选择 .ass 文件")[0]
    cmds.textField(text_field, edit=True, text=file_path)

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
        cmds.setAttr(node + '.dso', new_path, type='string')

def add_expression(start_frame, end_frame):
    """
    添加表达式到 aiStandIn 节点
    """
    aiStandIn_nodes = get_aiStandIn_nodes()
    for node in aiStandIn_nodes:
        if cmds.listConnections(node + '.frameNumber', type='expression'):
            cmds.delete(cmds.listConnections(node + '.frameNumber', type='expression'))
        cmds.setAttr(node + '.useFrameExtension', 1)
        
        random_offset = random.randint(0, (end_frame - start_frame))
        
        expression = """
        int $start = {2} - {0}.frameOffset;
        int $end = {3} - {0}.frameOffset;
        int $range = {3} - {2} + 1;
        {0}.frameNumber = $start + ((frame >= $start) ? ((frame - $start + {1}) % $range) : ($range - ($start - 1 - frame) % $range) - 1);
        """.format(node, random_offset, start_frame, end_frame)

        cmds.expression(s=expression)

# 调用创建窗口函数
create_window()
