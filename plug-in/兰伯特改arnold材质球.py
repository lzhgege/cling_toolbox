# 导入Maya Python API模块
import maya.cmds as cmds
import pymel.core as pm
from pymel.core import shadingNode

# 获取当前场景中所有的lambert材质节点
lamberts = cmds.ls(type='lambert')

# 遍历每一个lambert节点
for lambert in lamberts:
    # 创建aiStandardSurface材质节点
    ai_shader = shadingNode('aiStandardSurface', name=lambert + '_ai', asShader=True)

    # 获取lambert color连接
    color_connections = pm.listConnections(lambert + '.color', source=True, destination=False)
    # 连接lambert color到aiStandardSurface的baseColor
    if color_connections:
        color_texture = color_connections[0]
        pm.connectAttr(color_texture + ".outColor", ai_shader + ".baseColor")

    # 获取lambert normal连接
    normal_connections = pm.listConnections(lambert + '.normalCamera', source=True, destination=False)
    # 连接lambert normal到aiStandardSurface的normalCamera
    if normal_connections:
        normal_texture = normal_connections[0]
        pm.connectAttr(normal_texture + ".outNormal", ai_shader + ".normalCamera")   

    # 获取原来的ShadingGroup，并将aiStandardSurface连接上去
    orig_sg = pm.PyNode(cmds.listConnections(lambert, type="shadingEngine")[0])
    pm.connectAttr(ai_shader+'.outColor', orig_sg+'.surfaceShader', force=True)
