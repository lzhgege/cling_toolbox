# -*- coding: utf-8 -*-
import maya.OpenMaya as OpenMaya
import maya.cmds as cm
import time
import functools

def getMFnMesh(nameStr):
    mList = OpenMaya.MSelectionList()
    mList.add(nameStr)
    objDagPath = OpenMaya.MDagPath()
    mList.getDagPath(0,objDagPath)
    meshFn = OpenMaya.MFnMesh(objDagPath)
    return meshFn
 
#判断一个点是否在模型里面，> 0 外面，< 0 里面， == 0 在边界，算法不完美
def pointIsInsideMesh(objName,pointX,pointY,pointZ):
    meshFn = getMFnMesh(objName)
    point = OpenMaya.MPoint(pointX,pointY,pointZ)
    closestPoint = OpenMaya.MPoint()
    faceId = OpenMaya.MScriptUtil()
    faceIdPtr = faceId.asIntPtr()
    meshFn.getClosestPoint(point,closestPoint,OpenMaya.MSpace.kWorld,faceIdPtr)
    closestPointVector = OpenMaya.MVector(pointX - closestPoint.x, pointY - closestPoint.y, pointZ - closestPoint.z)
    closestPointNormal = closestPointVector.normal()
    closestFaceId = faceId.getInt(faceIdPtr)
    faceNormal = OpenMaya.MVector()
    meshFn.getPolygonNormal(closestFaceId,faceNormal,OpenMaya.MSpace.kWorld)
    return closestPointNormal * faceNormal
    
#点是不是在物体的boundingBox外面
#1:外面
#-1:里面
#0：边界
def outsideBoundingBox(objName,pointX,pointY,pointZ):
    [xmin,ymin,zmin,xmax,ymax,zmax] = cm.xform(objName,bbi = True,q = True,ws = True)
    if pointX < xmin or pointX > xmax or pointY < ymin or pointY > ymax or pointZ < zmin or pointZ > zmax:
        return 1
    elif pointX == xmin or pointX == xmax or pointY == ymin or pointY == ymax or pointZ == zmin or pointZ == zmax:
        return 0
    else:
        return -1

#判断一条(头发)曲线方向是不是反的，正：cv0在模型内，cv最后一个在模型外，反：cv0在模型外，cv最后一个在模型内
#如果在这两种情况以外，无法判断，当作没有反
def curveDirectionIsWrong(curveName,objName):
    cvCount = len(cm.getAttr('%s.controlPoints'%curveName,mi = True))
    startCVPosition = cm.xform('%s.cp[0]'%curveName,t = True,ws = True,q = True)
    endCVPosition = cm.xform('%s.cp[%d]'%(curveName,cvCount - 1),t = True,ws = True,q = True)
    
    if outsideBoundingBox(objName,startCVPosition[0],startCVPosition[1],startCVPosition[2]) == 1:
        startCVisOutside = True
    else:
        startCVisOutside = pointIsInsideMesh(objName,startCVPosition[0],startCVPosition[1],startCVPosition[2]) > 0
    if outsideBoundingBox(objName,endCVPosition[0],endCVPosition[1],endCVPosition[2]) == 1:
        endCVisInside = False
    else:
        endCVisInside = pointIsInsideMesh(objName,endCVPosition[0],endCVPosition[1],endCVPosition[2]) <= 0
    if startCVisOutside and endCVisInside:
        return True
    return False
    
#曲线基于模型的位置
#起始和结束在外
#起始和结束在内
#起始在内结束在外
#起始在外结束在内
def curvePositionState(curveName,objName):
    cvCount = len(cm.getAttr('%s.controlPoints'%curveName,mi = True))
    startCVPosition = cm.xform('%s.cp[0]'%curveName,t = True,ws = True,q = True)
    endCVPosition = cm.xform('%s.cp[%d]'%(curveName,cvCount - 1),t = True,ws = True,q = True)
    if outsideBoundingBox(objName,startCVPosition[0],startCVPosition[1],startCVPosition[2]) == 1:
        startCVisOutside = True
    else:
        startCVisOutside = pointIsInsideMesh(objName,startCVPosition[0],startCVPosition[1],startCVPosition[2]) > 0
    if outsideBoundingBox(objName,endCVPosition[0],endCVPosition[1],endCVPosition[2]) == 1:
        endCVisOutside = True
    else:
        endCVisOutside = pointIsInsideMesh(objName,endCVPosition[0],endCVPosition[1],endCVPosition[2]) > 0
    if startCVisOutside and endCVisOutside:
        return 0
    elif not startCVisOutside and not endCVisOutside:
        return 1
    elif not startCVisOutside and endCVisOutside:
        return 2
    else:#startCVisOutside and not endCVisOutside
        return 3
    

def cutHair(curve,obj,subsection):
    sList = OpenMaya.MSelectionList()
    sList.add(curve)
    sList.add(obj)
    
    curveDagPath = OpenMaya.MDagPath()
    sList.getDagPath(0,curveDagPath)
    objDagPath = OpenMaya.MDagPath()
    sList.getDagPath(1,objDagPath)
    
    curveFn = OpenMaya.MFnNurbsCurve(curveDagPath)
    p = OpenMaya.MPoint()
    
    
    objFn = OpenMaya.MFnMesh(objDagPath)
    closePoint = OpenMaya.MPoint()
    
    maxValue = cm.getAttr('%s.maxValue'%curve)
    minValue = cm.getAttr('%s.minValue'%curve)
    isReverse = False
    
    #起始和结束点都在内或者在外的，不作处理
    curvePState = curvePositionState(curve,obj)
    if curvePState == 0 or curvePState == 1:
        return 
    #方向反了 
    if curvePState == 3:
        cm.reverseCurve(curve,ch = False,rpo = True)
        isReverse = True
    
    #searchWithStart
    curveLength = curveFn.length()
    subsectionDistance = curveLength * 1.0 / subsection
    addKnot = False
    addKnotParam = 0
    for i in range(subsection + 1):
        param = minValue + (maxValue - minValue) * i / subsection
        curveFn.getPointAtParam(param,p,OpenMaya.MSpace.kWorld)
        objFn.getClosestPoint(p,closePoint,OpenMaya.MSpace.kWorld)
        if p.distanceTo(closePoint) < 0.001:
            addKnot = True
            addKnotParam = param
            addPoint = OpenMaya.MPoint(p.x,p.y,p.z)
            break
        else:
            if not addKnot:
                if p.distanceTo(closePoint) < subsectionDistance:
                    addKnot = True
                    addKnotParam = param
                    addPoint = OpenMaya.MPoint(p.x,p.y,p.z)
    if addKnot:
        cm.insertKnotCurve('%s.u[%f]'%(curve,addKnotParam),ch = False,cos = True,nk = 1,add = True,
            ib = False,rpo = True)                                        
            
        epCount = cm.getAttr('%s.spans'%curve) + 1
        for i in range(epCount):
            ep = '%s.ep[%d]'%(curve,0)
            nowP = cm.xform(ep,q = True,t = True,ws = True)
            nowP3bit = ['%.3f'%nowP[0],'%.3f'%nowP[1],'%.3f'%nowP[2]]
            p3bit = ['%.3f'%addPoint.x,'%.3f'%addPoint.y,'%.3f'%addPoint.z]
            if nowP3bit != p3bit:
                cm.delete(ep)
            else:
                break
    if isReverse:
        cm.reverseCurve(curve,ch = False,rpo = True)
        
def isTypeTransform(transform,shapeType):
    if cm.listRelatives(transform,s = True,pa = True,
                        ni = True,type = shapeType):
        return True
    return False
    
def isCurve(transform):
    return isTypeTransform(transform,'nurbsCurve')
    
def isPolygon(transform):
    return isTypeTransform(transform,'mesh')

 
def cutHiarFromSelected(optMenu, *argvs):        
    objList = cm.ls(sl = True)
    objListCount = len(objList)
    subsection = int(cm.optionMenu(optMenu,value = True,q = True))
    if objListCount <= 1:
        cm.warning(u'选择的物体太少啦')
        return
    if not isPolygon(objList[objListCount - 1]):
        cm.warning(u'有冇搞错啊，最后一个好像不是模型哦')
        return 
    for i in range(objListCount - 1):
        if not isCurve(objList[i]):
            cm.warning(u'有冇搞错啊，%s 好像不是曲线哦'%objList[i])
            return
    amount = 0

    cm.progressWindow(	title='HairCut',
					progress=amount,
					status = '',
					isInterruptable=True )
    i = 0
    doneCount = 0
    startTime = time.time()
    while i < objListCount - 1:
        if cm.progressWindow( query=True, isCancelled=True ) :
		    break
        cutHair(objList[i],objList[objListCount - 1],subsection)
        amount = int(i * 1.0 / (objListCount - 1) * 100)
        cm.progressWindow( edit=True, progress=amount,status = '')
        doneCount = i
        i = i + 1
    
    endTime = time.time()
    useTime = endTime - startTime
    cm.progressWindow(endProgress=1)
    print('')
    cm.confirmDialog(m = u'处理 %d 条曲线\n完成时间： %.3f 秒'%
                    (i,useTime),b = u'知道了',t = u'完成')
    #print('finish %d objects'%i)
    #print('all done in %.3f seconds'%useTime)
      
def eaHairCutUI():
    win = 'EAHairCutWin'
    if cm.window(win,ex = True):
        cm.deleteUI(win)
    cm.window(win,title = 'eaHairCut')
    cm.window(win,e = True,w = 200,h = 130)
    cm.columnLayout(adj = True)
    cm.text(l = u'先选曲线再选模型',h = 60)
    cm.rowLayout(nc = 2,adj = 1)
    cm.text(l = '')
    optMenu = cm.optionMenu( label=u'精确度(越高越精确)')
    cm.menuItem( label='1000' )
    cm.menuItem( label='1500' )
    cm.menuItem( label='2000' )
    cm.menuItem( label='2500' )
    cm.menuItem( label='3000' )
    cm.setParent('..')
    cm.button(h = 50,l = 'Cut',c = functools.partial(cutHiarFromSelected, optMenu))
    
    cm.showWindow(win)
    

eaHairCutUI()        
