import maya.cmds
mllName = 'ziSpread_'+maya.cmds.about(v=True)[:4]

if not maya.cmds.pluginInfo(mllName, q=True, loaded=True):
    maya.cmds.loadPlugin(mllName)

maya.cmds.setToolTo(maya.cmds.ziSpreadContext())