#*- coding: utf-8 -*-
#Script Name:Ass Convert Geometry
#Create Data:2020-5-22
#     E-mail: junvfx@foxmail.com


import maya.cmds as mc
from functools import partial
import os,subprocess

class JunProxyConvertGeometry():
	def __init__(self):
		self._version = 1.0
		self._width = 250
		self._height = 300
		self._objectName = "jpcgUI"

	def mainUI(self):
		if mc.window(self._objectName, exists=True):
			mc.deleteUI(self._objectName)

		mc.window(self._objectName,title="Proxy Convert Geometry v%s  by luojun"%self._version,
					width = self._width,height = self._height)
		mc.rowColumnLayout("JPCG_layout1",nc=1)
		label_text = u"1、 选择代理物体，ass\n"
		label_text+= u"2、 点击转换\n"
		label_text+= u"3、 完成之后，自动创建两个显示层\n"
		label_text+= u"4、代理物体层-->old_ass_object\n"
		label_text+= u"5、实体模型层-->new_geometry_object\n\n"
		label_text+= "create:	  2020-5-22\n"
		mc.text(label=label_text, al="left")
		mc.button(label = u"转换",height=40,width=250,c=partial(self.convertGeometry))

		mc.showWindow(self._objectName)
		mc.window(self._objectName,edit = True,width = self._width,height = self._height)

	def convertGeometry(self, Obj= None):
		sel_ass_list = mc.ls(sl=True)
		if len(sel_ass_list) != 0:
			mc.select(cl=True)
			displayLayer = mc.ls(type="displayLayer")
			if "old_ass_objectj" not in displayLayer:
				mc.createDisplayLayer(name='old_ass_objectj')
			if "new_geometry_objectj" not in displayLayer:
				mc.createDisplayLayer(name='new_geometry_objectj')
			path = os.environ["TMP"]
			i=0.0
			mc.progressWindow(title='Progressing',
			progress=0,
			status='Stats: 0%',
			isInterruptable=True )
			for ass in sel_ass_list:
				mc.select(ass,r=True)
				mc.editDisplayLayerMembers("old_ass_objectj",cmds.ls(sl=True),noRecurse=True)
				ass_path = "%s/%s.obj"%(path,ass)
				mc.arnoldBakeGeo(f= ass_path)
				i+=1.0
				#mc.warning("export:%d/%d"%(i,len(sel_ass_list)))
				mc.progressWindow(edit = True,progress=i/len(sel_ass_list)*100, status=("Stats: %s %%"%str(int(i/len(sel_ass_list)*100))))
				mc.refresh(currentView=True)
				import_mesh = mc.file(ass_path,i=True,returnNewNodes=True)
				mc.select(import_mesh,r=True)
				mc.editDisplayLayerMembers("new_geometry_objectj",import_mesh,noRecurse=True)
			mc.progressWindow(endProgress=1)
			cmd_script = "del %s\\*.obj"%path.replace("/","\\")
			os.system( cmd_script )#clear obj file

def showWindow():
	app = JunProxyConvertGeometry()
	app.mainUI()

showWindow()