# -*- coding: utf-8 -*-
import maya.cmds as cmds
import random

class ExporterWindow:
    def __init__(self):
        self.window_name = 'ExporterWindow'
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)

        self.window_name = cmds.window(self.window_name, title=u"GPU Cache导出工具", widthHeight=(200, 200))
        cmds.columnLayout(adjustableColumn=True)
        self.color_picker = cmds.colorSliderGrp(label=u'颜色选择', rgb=(1, 0, 0))
        self.file_text_field = cmds.textFieldButtonGrp(label=u'文件名', buttonLabel=u'浏览..')
        self.path_text_field = cmds.textFieldButtonGrp(label=u'路径', buttonLabel=u'浏览..')

        cmds.button(label=u'导出', command=self.export_selection)
        cmds.showWindow(self.window_name)

    def export_selection(self, *args):
        color_rgb = cmds.colorSliderGrp(self.color_picker, query=True, rgbValue=True)
        file_name = cmds.textFieldButtonGrp(self.file_text_field, query=True, text=True)
        path_dir = cmds.textFieldButtonGrp(self.path_text_field, query=True, text=True)

        selected_objects = cmds.ls(selection=True)
        for obj in selected_objects:
            shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
            lambert = cmds.shadingNode('lambert', asShader=True)
            cmds.setAttr(lambert + '.color', color_rgb[0], color_rgb[1], color_rgb[2], type='double3') 
            cmds.connectAttr(lambert + ".outColor", shading_group + ".surfaceShader", force=True)
            cmds.sets(obj, edit=True, forceElement=shading_group)

            # 导出设置gpu cache
            cmds.gpuCache(obj, startTime=1, endTime=1, optimize=True, optimizationThreshold=4000,
                          writeMaterials=True, directory=path_dir, fileName=file_name, dataFormat="ogawa")

ExporterWindow()