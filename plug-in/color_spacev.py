# -*- coding: utf-8 -*-
# 作者：cling
# 微信：clingkaka
# 个人主页：www.cg6i.com
# 模型下载：www.cgfml.com
# AI聊天绘画：ai.cgfml.com
# 敲码不易修改搬运请保留以上信息，感谢！！！！！

import maya.cmds as mc

raw_space = 'Utility - Raw'
sRGB_space = 'Utility - sRGB - Texture'
default_raw_space = 'Raw'
default_sRGB_space = 'sRGB'
normal_space = 'Utility - Linear - sRGB'
displacement_space = 'Utility - sRGB - Texture'


def set_color_space(material, attribute, color_space):
    node = mc.listConnections(material + '.' + attribute, source=True, destination=False)
    if node and mc.nodeType(node[0]) == 'file':
        mc.setAttr(node[0] + '.colorSpace', color_space, type='string')
        mc.setAttr(node[0] + '.ignoreColorSpaceFileRules', 1)
        
        textures = mc.ls(type='file')
        for tex in textures:
            tex_name = mc.getAttr(tex + '.fileTextureName').lower()
            mc.setAttr(tex + '.ignoreColorSpaceFileRules', 1)
            if 'roughness' in tex_name or 'ao' in tex_name or 'displacement' in tex_name or 'height' in tex_name or 'metalness' in tex_name or 'normal' in tex_name or 'opacity' in tex_name: mc.setAttr(tex + '.alphaIsLuminance', 1)
            if 'basecolor' in tex_name or 'albedo' in tex_name or 'opacity' in tex_name:
                mc.setAttr(tex + '.colorSpace', sRGB_space, type='string')
            elif 'normal' in tex_name:
                mc.setAttr(tex + '.colorSpace', normal_space, type='string')
            elif 'roughness' in tex_name or 'ao' in tex_name or 'height' in tex_name or 'metalness' in tex_name:
                mc.setAttr(tex + '.colorSpace', raw_space, type='string')
            elif 'displacement' in tex_name:
                mc.setAttr(tex + '.colorSpace', displacement_space, type='string')

                
                
def set_normal_map_color_space_aces(material):
    normal_map_nodes = mc.listConnections(material + ".normalCamera", type="aiNormalMap")
    if normal_map_nodes:
        for nm_node in normal_map_nodes:
            if raw_space == default_raw_space:
                set_color_space(nm_node, 'input', raw_space)
            else:
                set_color_space(nm_node, 'input', 'Utility - Linear - sRGB')


def set_bump_map_color_space(material):
    bump_map_nodes = mc.listConnections(material + ".normalCamera", type="bump2d")
    if bump_map_nodes:
        for bm_node in bump_map_nodes:
            set_color_space(bm_node, 'bumpValue', raw_space)


def set_baseColor_map_color_space(material):
    baseColor_map_nodes = mc.listConnections(material + ".baseColor", type="aiColorCorrect")
    if baseColor_map_nodes:
        for color_node in baseColor_map_nodes:
            set_color_space(color_node, 'input', sRGB_space)


def set_displacement_map_color_space_aces(material):
    sg_nodes = mc.listConnections(material, type="shadingEngine")
    if sg_nodes:
        for sg_node in sg_nodes:
            displacement_map_nodes = mc.listConnections(sg_node + ".displacementShader", type="displacementShader")
            if displacement_map_nodes:
                for dm_node in displacement_map_nodes:
                    if raw_space == default_raw_space:
                        set_color_space(dm_node, 'displacement', raw_space) 
                    else: # ACES workflow
                        set_color_space(dm_node, 'displacement', 'Utility - sRGB - Texture') 


def apply_color_spaces():
    all_materials = mc.ls(mat=True)
    for material in all_materials:
        if mc.nodeType(material) != 'aiStandardSurface':
            continue
        set_color_space(material, 'specularRoughness', raw_space)
        set_color_space(material, 'baseColor', sRGB_space)
        set_color_space(material, 'metalness', raw_space)
        set_color_space(material, 'emissionColor', sRGB_space)
        set_color_space(material, 'opacity', sRGB_space)
        set_color_space(material, 'subsurfaceColor', sRGB_space)
        set_normal_map_color_space_aces(material) 
        set_bump_map_color_space(material)
        set_baseColor_map_color_space(material)
        set_displacement_map_color_space_aces(material) 
    mc.confirmDialog(title=u'执行结果', message=u'已在所有材质中应用色彩空间设置', button=['OK'], defaultButton='OK')


def set_simplified_color_space():
    global raw_space, sRGB_space, normal_space, displacement_space
    raw_space = default_raw_space
    sRGB_space = default_sRGB_space
    normal_space = default_raw_space
    displacement_space = default_raw_space 
    color_space = default_sRGB_space 
    apply_color_spaces()
def set_default_color_space():
    global raw_space, sRGB_space, normal_space, displacement_space
    raw_space = 'Utility - Raw'
    sRGB_space = 'Utility - sRGB - Texture'
    normal_space = 'Utility - Linear - sRGB'
    displacement_space = 'Utility - sRGB - Texture' 
    color_space = 'Utility - sRGB - Texture' 
    apply_color_spaces()


window = mc.window(title=u'一键贴图色彩空间修改v2.0', widthHeight=(320, 150))
mc.columnLayout()
mc.text(label=u'点击所需色彩空间即可一键更改当前maya所有贴图色彩空间', width=320)
mc.separator(height=10)
mc.rowLayout(numberOfColumns=2)
mc.separator(width=30)
mc.rowLayout(numberOfColumns=2, columnWidth2=[130, 130]) 
mc.button(label='sRGB', width=130, command=lambda x: set_simplified_color_space())
mc.button(label='ACES', width=130, command=lambda x: set_default_color_space())
mc.setParent('..') 
mc.setParent('..')
mc.separator(height=10)
mc.text(label=u'作者：cling', width=320)
mc.text(label=u'qq交流群：872491740', width=320)
mc.text(label=u'<a href="https://www.cgfml.com/194946.html">更多详情访问：https://www.cgfml.com/194946.html</a>', width=320)


mc.showWindow(window)


