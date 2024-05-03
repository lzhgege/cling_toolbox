
import maya.cmds as cmds
import os

standins = cmds.ls(type='aiStandIn')
group_dict = {}

for standin in standins:
    filepath = cmds.getAttr(standin + '.dso')

    
    basename = os.path.basename(filepath)
    groupname = os.path.splitext(basename)[0]

    
    if groupname in group_dict:
        group = group_dict[groupname]
    else:
        
        group = cmds.group(em=True, name=groupname)
        group_dict[groupname] = group
    
    
    cmds.parent(standin, group)
