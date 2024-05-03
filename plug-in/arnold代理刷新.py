# -*- coding: utf-8 -*-

import maya.cmds as cmds

class ArnoldProxyReloaderUI():
    def __init__(self):
        self.window_name = "Arnold Proxy Reloader"
    
    def create(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        
        cmds.window(self.window_name, title="Arnold Proxy Reloader", sizeable=True)
        
        cmds.columnLayout(adjustableColumn=True)
        cmds.separator(height=20, style="none")
        
        cmds.button(label=u"刷新Arnold代理", command=self.reload_arnold_proxies)
        
        cmds.showWindow()
    
    def reload_arnold_proxies(self, *args):
        selected_nodes = cmds.ls(selection=True)
        proxy_nodes = []
        
        if selected_nodes:  # 如果有选定的物体
            for node in selected_nodes:
                standin_nodes = cmds.listRelatives(node, type='aiStandIn')  # 获取aiStandIn节点
                if standin_nodes:  # 检查是否存在aiStandIn节点
                    proxy_nodes.extend(standin_nodes)
        else:  # 如果没有选定的物体
            proxy_nodes = cmds.ls(type="aiStandIn")
        
        for node in proxy_nodes:
            file_path = cmds.getAttr(node + ".dso")
            if isinstance(file_path, list):  # 检查是否为列表
                file_path = file_path[0]  # 获取列表的第一个元素
            print("Reloading proxy: " + file_path)
            
            try:
                cmds.setAttr(node + ".dso", file_path, type="string")
            except:
                print("Failed to reload proxy: " + file_path)

ui = ArnoldProxyReloaderUI()
ui.create()
