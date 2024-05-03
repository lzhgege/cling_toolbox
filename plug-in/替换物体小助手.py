# -*- coding: utf-8 -*-
import maya.cmds as cmds

class AIStandInWindow(object):
    def __init__(self):
        self.window_name = "AIStandInWindow"
        
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)
            
        cmds.window(self.window_name, title=u"替换物体小助手")
        
        cmds.columnLayout(adjustableColumn=True)

        cmds.rowLayout(numberOfColumns=2)
        self.object_textfield = cmds.textField(placeholderText=u'物体名称（多个随机）留空则自动创建一个box', width=240)
        cmds.button(label=u'添加物体', command=self.load_selected_object)
        cmds.setParent('..')
        
        cmds.rowLayout(numberOfColumns=2)
        self.group_textfield = cmds.textField(text=u'position', width=240)
        cmds.setParent('..')
        
        cmds.button(label=u"确定", command=self.copy_objects_to_selection)
        
        cmds.showWindow(self.window_name)
    
    def load_selected_object(self, *args):
        selection = cmds.ls(selection=True)
        if not selection:
            return
        object_names = " ".join(selection)
        cmds.textField(self.object_textfield, edit=True, text=object_names)
    
    def copy_objects_to_selection(self, *args):
        object_names = cmds.textField(self.object_textfield, query=True, text=True).split()
        group_name = cmds.textField(self.group_textfield, query=True, text=True)
        
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning(u"请先选择一个或多个物体！")
            return
        
        if not cmds.objExists(group_name):
            group_name = cmds.group(empty=True, name=group_name)

        if not object_names:
            box = cmds.polyCube(n='box')[0]
            object_names.append(box)
            
        for target_object in selection:
            position = cmds.xform(target_object, query=True, translation=True, worldSpace=True)
            rotation = cmds.xform(target_object, query=True, rotation=True, worldSpace=True)
            scale = cmds.xform(target_object, query=True, scale=True)

            for object_name in object_names:
                if not cmds.objExists(object_name):
                    continue
                new_object = cmds.duplicate(object_name)[0]
                cmds.parent(new_object, group_name)
                new_object = cmds.rename(new_object, target_object)
                
                cmds.move(position[0], position[1], position[2], new_object, absolute=True)
                cmds.rotate(rotation[0], rotation[1], rotation[2], new_object, worldSpace=True)
                cmds.scale(scale[0], scale[1], scale[2], new_object)
        
        if 'box' in object_names:
            cmds.delete(box)

# 创建窗口实例
AIStandInWindow()
