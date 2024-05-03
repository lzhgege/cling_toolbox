#coding:utf-8
import maya.cmds as cmds
import pymel.core as pm
import collections
import maya.mel as mel
import json
import os
from json_helper import JsonHelper

class ModelKindReadTool_CJ():
    @staticmethod
    def readJsonFile(filePath):  
        filePath = filePath.replace('\\', '/')    
        # f = open(filePath)
        # data = json.load(f,encoding='utf-8')
        # f.close()
        data = JsonHelper().load_json(filePath)   
        return data
        
    @staticmethod
    def getFileFullPath():
        cwd = os.path.abspath(__file__)
        path = cwd if os.path.isdir(cwd) else os.path.dirname(cwd)
        fileName = 'Model_Name_CJ.json'
        fileFullPath = os.path.join(path,fileName)
        return fileFullPath
    
    @staticmethod
    def getModelKindAndParentList(prefix):
        filePath = ModelKindReadTool_CJ.getFileFullPath()
        modelKindAndParentList = list()
        modelKindGrpList = ModelKindReadTool_CJ.readJsonFile(filePath)
        for modelKindGrpDict in modelKindGrpList:
            modelKindLineList = modelKindGrpDict['groups']
            for modelKindLine in modelKindLineList:
                for modelKindDict in modelKindLine:
                    par = prefix + modelKindDict['parent'] if modelKindDict['parent'] != '' else None
                    modelKindAndParentList.append((prefix + modelKindDict['name'], (par, modelKindDict['siblingBrothers'])))
        return modelKindAndParentList

    @staticmethod
    def getButDictList(prefix):
        filePath = ModelKindReadTool_CJ.getFileFullPath()
        modelKindGrpList = ModelKindReadTool_CJ.readJsonFile(filePath)
        butDictList = list()
        separatorCount = 0
        for modelKindGrp in modelKindGrpList:
        	if modelKindGrp['label'] != '':
        		modelKindLineList = modelKindGrp['groups']
        		butDict = collections.OrderedDict()
        		butLabel = modelKindGrp['label']
        		for modelKindLine in modelKindLineList:
        			totalCount = 4
        			modelKindLineCount = len(modelKindLine)
        			needSeparatorCount = totalCount - modelKindLineCount
        			for i in range(modelKindLineCount):
        				butDict[prefix + modelKindLine[i]['name']] = [prefix + modelKindLine[i]['name'],modelKindLine[i]['label'],modelKindLine[i]['siblingBrothers']]
        			if needSeparatorCount:
        				for i in range(needSeparatorCount):                          
        					butDict['separator%d'%separatorCount] = ['separator', u'']
        					separatorCount += 1
        		butDictList.append((butDict,butLabel))
        return butDictList




class ModelNameTool_CJ():
	def __init__(self):
		self.prefix = 'CJ_'

	def creatGrp_new(self,grp,grpParent):
		#print type(grp)
		if cmds.objExists(grp):
			if grpParent != None:
				if cmds.listRelatives(grp,parent=True)[0] == grpParent:
					pass
				else:
					cmds.parent(grp,grpParent)
			else:
				pass
		else:
			cmds.group(empty=True, name=grp)
			if grpParent != None:
				cmds.parent(grp,grpParent)

	def creatGrp(self,grp,grpParent):
		if grp=="CJ_Geometry":
			grp="Geometry"
		if grpParent=="CJ_Geometry":
			grpParent="Geometry"
		#print type(grp)
		if cmds.objExists(grp):
			if grpParent != None:
				parents=cmds.listRelatives(grp,p=1)
				if parents  and parents[0] == grpParent:
					pass
				else:
					cmds.parent(grp,grpParent)
		else:
			if grpParent != None: 
				cmds.group(em=1,name=grp)
				cmds.parent(grp,grpParent)
			else:
				cmds.group(em=1,name = grp)


	def creatGrps_new(self,custom_grp=None,custom_str=None):
		returnGrp=""
		grps = self.baseGrps()
		for k, v in grps.items():
			grp=str(k)
			grpParent = str(v[0])
			print(grpParent)
			#下面的一段是对自定义的进行判断，Custom是自定义的父组，找到就跳过，下面的子自定义组的要去掉自带前缀
			if custom_grp and (not returnGrp):
				if grp.find(custom_str)>-1:
						returnGrp=grp.replace(custom_str,custom_grp).replace(self.prefix+"_","")
						#防止有的有_,有的没有，替换两次
						returnGrp=returnGrp.replace(self.prefix+"_","")
						returnGrp=returnGrp.replace(self.prefix,"")
						returnGrp=returnGrp.replace("DL_","")#这里代理替换直接写死,如果json文件改了，这里也要做对应的更改
						self.creatGrp(returnGrp,grpParent)
						break
			elif (grp.find("Custom")>-1):
				continue


			for k, v in grps.items():
				# print ('k = %s,v = %s'%(k,v))
				if v[0]:
					# if v[0] != None:
					self.creatGrp(str(k), str(v[0]))
					# if has siblingBrothers
					if v[1]:
						for i in range(v[1]):
							name = str(k)
							modGrp = 'ModGrp'
							modGrpLength = len(modGrp)
							newNamePart1 = name[0:-modGrpLength]
							newName = newNamePart1 + chr(i + 97) + '_' + modGrp
							self.creatGrp(newName, str(k))

				else:
					self.creatGrp(str(k), None)
		return returnGrp

	def creatGrps(self):
		grps = self.baseGrps()
		for k, v in grps.items():
			# print ('k = %s,v = %s'%(k,v))
			if v[0]:
				# if v[0] != None:
				pass
				self.creatGrp(str(k), str(v[0]))
				# if has siblingBrothers

				if v[1]:
					for i in range(v[1]):
						name = str(k)
						modGrp = 'ModGrp'
						modGrpLength = len(modGrp)
						newNamePart1 = name[0:-modGrpLength]
						newName = newNamePart1 + chr(i + 97) + '_' + modGrp
						self.creatGrp(newName, str(k))

			else:
				self.creatGrp(str(k), None)
	def creatGrps(self):
		grps = self.baseGrps()
		for k, v in grps.items():
			#print ('k = %s,v = %s'%(k,v))
			if v[0]:
			#if v[0] != None:
				pass
				self.creatGrp(str(k),str(v[0]))
				#if has siblingBrothers
				
				if v[1]:
					for i in range(v[1]):
						name = str(k)
						modGrp = 'ModGrp'
						modGrpLength = len(modGrp)
						newNamePart1 = name[0:-modGrpLength]
						newName = newNamePart1 + chr(i + 97) + '_' + modGrp
						self.creatGrp(newName,str(k))
				
			else:
				self.creatGrp(str(k),None)
		

	def baseGrps(self):
		return collections.OrderedDict(ModelKindReadTool_CJ.getModelKindAndParentList(self.prefix))

	def createCharGrps(self):
		chardict = self.baseGrps()
		for i in chardict.keys():
			if cmds.objExists(i) != 1:
				cmds.group(em=1,name=i)
			else:
				pass
		for j in chardict.keys():
			if cmds.objExists(j):
				if chardict[j] != None:
					if cmds.listRelatives(j,p=1) is None:
						cmds.parent(j,chardict[j])
					else:
						if cmds.listRelatives(j,p=1)[0] != chardict[j]:
							cmds.parent(j, chardict[j])

	def renameChild_new(self,child = None,num=1,*args):
		if child is not None:
			if pm.listRelatives(child,s=1) is not None and \
				pm.nodeType(pm.listRelatives(child,s=1)[0]) == 'mesh' or \
				pm.nodeType(pm.listRelatives(child, s=1)) == 'aiStandIn':
				namenum = self.nameNums(num=num, pad=3)
				namePre = ''
				nameSfr = ''
				grpname = pm.listRelatives(child,p=1)[0]
				if grpname.find('_ModGrp') != -1:
					namePre = grpname.replace('_ModGrp','')
					nameSfr = '_mo'
				elif grpname.find('_NoRenderGrp') != -1:
					namePre = grpname.replace('_NoRenderGrp','')
					nameSfr = '_nrmo'
				elif grpname.find('_SetRenderGrp') != -1:
					namePre = grpname.replace('_SetRenderGrp', '')
					nameSfr = '_srmo'
				names = namePre+'_'+namenum+nameSfr
				try:
					pm.rename(child, names)
					return None
				except:
					return child

	def renameChild(self,child = None,num=1,*args):
		if child is not None:
			if pm.listRelatives(child,s=1) is not None and \
				pm.nodeType(pm.listRelatives(child,s=1)[0]) == 'mesh' or \
				pm.nodeType(pm.listRelatives(child, s=1)) == 'aiStandIn':
				namenum = self.nameNums(num=num, pad=3)
				namePre = ''
				nameSfr = ''
				grpname = pm.listRelatives(child,p=1)[0]
				if grpname.find('_ModGrp') != -1:
					namePre = grpname.replace('_ModGrp','')
					nameSfr = '_mo'
				elif grpname.find('_NoRenderGrp') != -1:
					namePre = grpname.replace('_NoRenderGrp','')
					nameSfr = '_nrmo'
				elif grpname.find('_SetRenderGrp') != -1:
					namePre = grpname.replace('_SetRenderGrp', '')
					nameSfr = '_srmo'
				names = namePre+'_'+namenum+nameSfr
				try:
					pm.rename(child, names)
					return None
				except:
					return child


	def is_mesh_or_aiStandIn(self,node):
		"""判断节点是否mesh或者aiStandIn"""
		return pm.nodeType(pm.listRelatives(node,shapes=True)) == 'mesh' or \
							pm.nodeType(pm.listRelatives(node, shapes=True)) == 'aiStandIn'


	def renameChildrenByParentName_new(self,parent=None,*args):
		errorlist = []
		if parent is not None:
			children = pm.listRelatives(parent,c=1)
			if children is not None:
				num = 1
				if type(children) is list:
					for child in children:
						if pm.listRelatives(child,shapes=True) is not None:
							if self.is_mesh_or_aiStandIn(child):
								errorc = self.renameChild_new(child=child, num=num)
								num = num+1
								if errorc is not None:
									errorlist.append(errorc)
				else:
					errorc = self.renameChild_new(child=children, num=1)#num应该是用来判断数字补位的
					if errorc is not None:
						errorlist.append(errorc)
		return errorlist


	def renameChildrenByParentName(self,parent=None,*args):
		errorlist = []
		if parent is not None:
			children = pm.listRelatives(parent,c=1)
			if children is not None:
				num = 1
				if type(children) is list:
					for child in children:
						if pm.listRelatives(child,s=1) is not None:
							if pm.nodeType(pm.listRelatives(child,s=1)) == 'mesh' or \
							pm.nodeType(pm.listRelatives(child, s=1)) == 'aiStandIn':
								errorc = self.renameChild(child=child, num=num)
								num = num+1
								if errorc is not None:
									errorlist.append(errorc)
				else:
					errorc = self.renameChild(child=children, num=1)
					if errorc is not None:
						errorlist.append(errorc)
		return errorlist

	#数字补位
	def nameNums(self,num=1,pad=3):
		pre = ''
		for p in xrange(pad):
			if num < pow(10,p):
				pre+='0'
		namenum = pre+str(num)
		return namenum

	def renameAllGrpChildren(self,parent=None,*args):
		errorlist = []
		if parent is not None:
			if type(parent) is list:
				for p in parent:
					erlist = self.renameChildrenByParentName(parent = p)
					errorlist.extend(erlist)
			else:
				errlist = self.renameChildrenByParentName(parent=parent)
				errorlist.extend(errlist)
		return errorlist
