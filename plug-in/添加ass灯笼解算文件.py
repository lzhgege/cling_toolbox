# -*- coding: utf-8 -*-
import maya.cmds as cmds
import random

class AIStandInWindow(object):
    def __init__(self):
        self.window_name = "AIStandInWindow"
        
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)
        
        cmds.window(self.window_name, title=u"添加解算ass小助手")
        
        cmds.columnLayout(adjustableColumn=True)
        
        cmds.rowLayout(numberOfColumns=2)
        self.filepath_textfield = cmds.textField(placeholderText=u'新的.ass文件路径', width=240)
        cmds.button(label=u'选择路径', command=lambda x: cmds.textField(
            self.filepath_textfield, edit=True, text=cmds.fileDialog2(fileMode=1, caption=u"选择 .ass 文件")[0]))
        cmds.setParent('..')
        
       
        
        cmds.button(label=u"确定", command=self.create_ai_standins)
        
        cmds.showWindow(self.window_name)
    
    def create_ai_standins(self, *args):
        ass_filepath = cmds.textField(self.filepath_textfield, query=True, text=True)
        
        # 获取当前选择的物体
        selection = cmds.ls(selection=True)

        if not selection:
            cmds.warning(u"请先选择一个或多个物体！")
            return

        # 遍历每个选择的物体
        for object_name in selection:
            # 生成新的节点名称
            sim_name = object_name + "_Sim"

            # 获取选择物体的位置、旋转和缩放信息
            position = cmds.xform(object_name, query=True, translation=True, worldSpace=True)
            rotation = cmds.xform(object_name, query=True, rotation=True, worldSpace=True)
            scale = cmds.xform(object_name, query=True, scale=True)

            # 创建名为"sim"的组
            if not cmds.objExists("sim"):
                cmds.group(empty=True, name="sim")

            # 创建aiStandIn节点并指定名称
            ai_standin = cmds.createNode("aiStandIn")

            # 设置Ass文件路径
            cmds.setAttr(ai_standin + ".dso", ass_filepath, type="string")

            # 将aiStandIn节点移动到选择物体的位置
            cmds.move(position[0], position[1], position[2], ai_standin, absolute=True)
            cmds.rotate(rotation[0], rotation[1], rotation[2], ai_standin, worldSpace=True)
            cmds.scale(scale[0], scale[1], scale[2], ai_standin)

            # 将新建的aiStandIn节点放入"sim"组中
            cmds.parent(ai_standin, "sim")
            cmds.rename(sim_name)

            # 输出提示信息
            cmds.select(ai_standin)
            cmds.warning(u"已在选择物体的位置上添加了名为" + sim_name + u"的aiStandIn节点，并将其放入sim组中！")
            
            # 添加表达式到aiStandIn节点
            self.add_expression(ai_standin)
    
    def add_expression(self, node):
        """
        添加表达式到 aiStandIn 节点
        """
        if cmds.listConnections(node + '.frameNumber', type='expression'):
            cmds.delete(cmds.listConnections(node + '.frameNumber', type='expression'))
        cmds.setAttr(node + '.useFrameExtension', 1)
        
        random_offset = random.randint(0, 200)
        expression = """
        int $start = 1 - {0}.frameOffset;
        int $end = 200 - {0}.frameOffset;
        int $range = 200 - 1 + 1;
        {0}.frameNumber = $start + ((frame >= $start) ? ((frame - $start + {1}) % $range) : ($range - ($start - 1 - frame) % $range) - 1);
        """.format(node, random_offset)

        cmds.expression(s=expression)
    
    def change_stand_in_path(self, new_path):
        """
        更改AI StandIn节点的路径
        """
        selection = cmds.ls(selection=True)
        
        if not selection:
            cmds.warning(u"请先选择一个或多个AI StandIn节点！")
            return
        
        for node in selection:
            if cmds.nodeType(node) == "aiStandIn":
                cmds.setAttr(node + ".dso", new_path, type="string")
                cmds.warning(u"已将节点 {} 的路径更改为 {}".format(node, new_path))

# 创建窗口实例
AIStandInWindow()
