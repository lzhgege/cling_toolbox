# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel

def find_and_replace(*args):
    """
    获取查找和替换的字符，执行查找和替换操作
    """
    # 获取文本框中的值
    find_str = cmds.textField(find_text, query=True, text=True)
    replace_str = cmds.textField(replace_text, query=True, text=True)
    
    # 获取所有aiStandIn节点
    aiStandIn_nodes = cmds.ls(type='aiStandIn')
    
    # 遍历所有的 aiStandIn 节点
    for node in aiStandIn_nodes:
        # 获取当前节点的文件路径
        curr_path = cmds.getAttr(node + '.dso')

        # 使用 Python 的 replace() 方法来实现路径的查找和替换
        new_path = curr_path.replace(find_str, replace_str)

        # 把新的路径设定到节点上
        cmds.setAttr(node + '.dso', new_path, type='string') 

def create_window():
    """
    创建窗口
    """
    global find_text
    global replace_text
    
    # 如果窗口已经存在，删除旧的窗口
    if cmds.window('aiStandIn_win', exists=True):
        cmds.deleteUI('aiStandIn_win', window=True)

    # 创建新窗口
    my_window = cmds.window('aiStandIn_win', title="Replace AiStandIn path", widthHeight=(400, 160))
    cmds.columnLayout( adjustableColumn=True )
    
    # 添加文本框接收查找内容和替换内容
    find_text = cmds.textField(placeholderText=u'请输入查找的路径')
    replace_text = cmds.textField(placeholderText=u'请输入替换的路径')
    
    # 添加提交按钮
    cmds.button(label='Submit', command=find_and_replace)

    # 显示窗口
    cmds.showWindow(my_window)

# 创建窗口
create_window()

