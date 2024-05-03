# -*- coding: utf-8 -*-
import maya.cmds as cmds

def select_boundary_edges(*args):

    # 选择物体
    selection = cmds.ls(selection=True)

    boundary_edges = []

    # 对于每一个选择的对象
    for obj in selection:
        # 将物体转为边，并展开列表
        edges = cmds.polyListComponentConversion(obj, toEdge=True)
        edges = cmds.filterExpand(edges, selectionMask=32, expand=True)

        # 现在，对于每一条边
        for edge in edges:
            # 查找连接这条边的面的数量。
            connected_faces = cmds.polyInfo(edge, edgeToFace=True)

            # split返回的是一个字符串列表，所以我们需要计算列表长度-1来获取面的数量
            face_count = len(connected_faces[0].split()) - 2

            # 如果面的数量小于2，那么这就是一个边界边，我们将其添加到选择中
            if face_count < 2:
                boundary_edges.append(edge)

    # 切换到边模式
    cmds.selectMode(component=True)
    cmds.selectType(edge=True)

    # 选择漏洞边
    cmds.select(boundary_edges)
    

# 创建一个新的窗口
if cmds.window("boundaryEdgesWindow", exists=True):
    cmds.deleteUI("boundaryEdgesWindow")

boundaryEdgesWindow = cmds.window("boundaryEdgesWindow", title=u"一键选择漏洞", widthHeight=(300, 100))
cmds.columnLayout(adjustableColumn=True)
cmds.button(label=u"点击选择", command=select_boundary_edges)   # 删除了函数后面的括号
cmds.button(label=u"封洞", command=lambda *args: cmds.polyCloseBorder())   # 这里也采用了lambda函数


cmds.button(label=u"三角化", command=lambda *args: cmds.polyTriangulate())
# 显示窗口
cmds.showWindow(boundaryEdgesWindow)

