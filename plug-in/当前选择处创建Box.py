# -*- coding: utf-8 -*-
import maya.cmds as cmds

# 获取当前选择的物体
selected = cmds.ls(selection=True)

if selected:
    # 循环遍历每个选择的物体
    for obj in selected:
        # 获取选择物体的大小
        bbox = cmds.exactWorldBoundingBox(obj)
        width = bbox[3] - bbox[0]
        depth = bbox[5] - bbox[2]
        height = bbox[4] - bbox[1]  # 直接从bbox获取高度

        # 创建一个pCube并设置其大小匹配选择的物体
        cube = cmds.polyCube(w=width, h=height, d=depth)[0]

        # 计算选择物体的中心位置
        center = [(bbox[0] + bbox[3])/2, (bbox[1] + bbox[4])/2, (bbox[2] + bbox[5])/2]

        # 将立方体移动到选定物体的中心位置
        cmds.move(center[0], center[1], center[2], cube)

        # 检查名为position的组是否已经存在
        if not cmds.objExists('position'):
            # 如果不存在，则创建一个名为position的组
            cmds.group(em=True, name="position")

        # 将立方体添加到名为position的组
        cmds.parent(cube, 'position')

        # 将立方体的名字改为原物体的名字
        cmds.rename(cube, obj)

else:
    cmds.warning(u"请先选择一个物体")
