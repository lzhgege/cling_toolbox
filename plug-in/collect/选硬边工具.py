import maya.cmds as cmds
cmds.polySelectConstraint(m = 3, t = 0x8000, sm = 1)
sels = cmds.ls(sl = 1)
cmds.polySelectConstraint(sm = 0) #复原选择模式，不然在view中只能选择硬边
cmds.select(sels)