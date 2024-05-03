import maya.cmds as cmds

selected_nodes = cmds.ls(selection=True)

if not selected_nodes:
    print("没有选中任何节点")
else:
    for file_node in selected_nodes:

        if cmds.nodeType(file_node) != "file":
            print("选中的节点不是文件节点")
            continue  

        expression_name = "myExpression_{}".format(file_node)

        frame_extension_attr = '{}.frameExtension'.format(file_node)
        if cmds.listConnections(frame_extension_attr, source=True, destination=False):
            source_attr = cmds.listConnections(frame_extension_attr, source=True, destination=False, plugs=True)[0]
            cmds.disconnectAttr(source_attr, frame_extension_attr)

        if cmds.objExists(expression_name):
            cmds.delete(expression_name)


        start_frame = 1001
        end_frame = 1200


        expression_string = "{}.frameExtension=(frame-1)%{}+{};".format(file_node, end_frame-start_frame+1, start_frame)

        cmds.expression(s=expression_string, n=expression_name)