# -*- coding: utf-8 -*-
import sys
import maya.cmds as cmds
import modelAssetInspectUI.common.utils as utils
import modelAssetInspectUI.views.detailedbackBaseWidget as detailedbackBaseWidget
import checkBase


if sys.version_info[0] == 2:
    reload(utils)
    reload(detailedbackBaseWidget)
    reload(checkBase)
elif sys.version_info[0] > 2:
    try:
        import importlib
        importlib.reload(utils)
        importlib.reload(detailedbackBaseWidget)
        importlib.reload(checkBase)
    except:
        pass



import sys
import os
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI
# reload(detailedbackBaseWidget)
try:
    from PySide2.QtWidgets import QMainWindow, QWidget
    from shiboken2 import wrapInstance

except:
    from PySide.QtGui import QMainWindow, QWidget
    from shiboken import wrapInstance
# try:
    # from EaToolBox import evalScriptFromToolBox
# except:
    # from ToolBox import evalScriptFromToolBox


try:
    import maya.app.renderSetup.model.renderSetup as renderSetup
except:
    pass


def getMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr:
        return wrapInstance(long(ptr), QMainWindow)


def flush(name, widget_type=QWidget):
    wins = getMayaWindow().findChildren(widget_type, name) or []
    for c in wins:
        try:
            c.close()
        except:
            continue
        c.deleteLater()


def _delete_(data):
    if not cmds.objExists(data):
        return True
    if cmds.referenceQuery(data, isNodeReferenced=True):
        return False
    try:
        if cmds.lockNode(data, q=True, lock=True):
            cmds.lockNode(data, lock=False)
        cmds.delete(data)
        return True
    except:
        return False


def _delete_transform_(data):
    if not cmds.objExists(data):
        return True
    if cmds.referenceQuery(data, isNodeReferenced=True):
        return False
    try:
        parent = cmds.listRelatives(data, parent=True)
        if len(parent) == 1:
            if cmds.lockNode(parent[0], q=True, lock=True):
                cmds.lockNode(parent[0], lock=False)
            cmds.delete(parent[0])
            return True
        else:
           return False
    except:
        return False


def _processing_(datas, fun):
    cannot_delete_list = []
    for data in datas:
        state = fun(data)
        if state:
            cannot_delete_list.append(data)

    return cannot_delete_list


def handleUnknownNode(datas):
    """
    删除未知节点
    :return: list 
    """
    return _processing_(datas, _delete_)


def handleRename(datas=None):
    '''
    获取检查重名
    :return: bool
    '''
    try:
        evalScriptFromToolBox(u'检查重名')
    except:
        pass
    

def handleEmptyGrp(datas=None):
    '''
    获取检查重名
    :return: bool
    '''
    return

def handleSpaceName(fun=None):
    """
    获取空间名
    :return: list
    """
    # mel.eval("NamespaceEditor;")
    uncheck_list = [":UI", ":shared"]

    namespaces = cmds.namespaceInfo(':', recurse=True, listOnlyNamespaces=True, absoluteName=True)
    for refnode in cmds.ls(references = True):
        ref_ns = cmds.referenceQuery(refnode, ns=1)
        if not ref_ns in uncheck_list:
            uncheck_list.append(ref_ns)

    values = [n for n in namespaces if n not in uncheck_list]

    values.reverse()
    for ns in values:
        cmds.namespace(mergeNamespaceWithParent=1, removeNamespace=ns)
    

def handleAnimationLayer(datas):
    """
    获取动画层
    :return: list
    """
    return _processing_(datas, _delete_)


def handleDisplayLayer(datas):
    '''
    获取显示层
    :return:
    '''
    return _processing_(datas, _delete_)


def handleExpression(datas):
    '''

    :param fun:
    :return:
    '''
    return _processing_(datas, _delete_)


def _handleFreezeTransformation(data):
    try:
        cmds.makeIdentity(data, apply=True, t=True, r=True, s=True, n=False, pn=True)
        return True
    except:
        return False


def handleFreezeTransformation(datas):
    '''
    获取未冻结transform节点
    :param transforms:
    :return:
    '''
    return _processing_(datas, _handleFreezeTransformation)


def _handleReseTransformation(data):
    try:
        cmds.makeIdentity(data, apply=False, t=True, r=True, s=True)
        return True
    except:
        return False


def handleReseTransformation(datas):
    '''
    获取没有在世界坐标中心的物体
    :param transforms:
    :return:
    '''
    return _processing_(datas, _handleReseTransformation)


def _handleKFramTransforms(data):
    anim_type = ["animCurveTL", "animCurveTA", "animCurveTT", 'animCurveTU']
    cmds.listConnections(data, s=True, d=True, type=anim_type)


def handleKFramTransforms(datas):
    '''
    获取k帧的物体
    :return:
    '''
    return _processing_(datas, _handleReseTransformation)


def handleTransformShapes(datas):
    '''
    获取shape节点2个以上的模型
    :param transforms:
    :return:
    '''
    values = list()
    if len(datas) != 1:
        return list()

    if cmds.objectType(datas[0], isType='mesh'):
        state = cmds.getAttr(datas[0] + ".intermediateObject")
        cmds.setAttr(datas[0] + ".intermediateObject", not state)
        values.append([datas[0], not state])

    return values


def _handleHideTransforms(data):
    try:
        cmds.setAttr(data + ".v", True)
        cmds.setAttr(data + ".hiddenInOutliner", False)
        shape_list = cmds.listRelatives(data, f=True, s=True)
        if shape_list:
            for each in shape_list:
                print each
                cmds.setAttr(each + ".v", True)
                cmds.setAttr(each + ".hiddenInOutliner", False)
        # refresh          
        for ui in cmds.lsUI(ed=True):
            if cmds.outlinerEditor(ui, ex=True):
                cmds.outlinerEditor(ui, e=True, rfs=True)         
        return True
    except:
        return False


def handleHideTransforms(datas):
    '''
    获取隐藏的几何体(transform)
    :param transforms:
    :return:
    '''
    return _processing_(datas, _handleHideTransforms)


def handleRenderLayer(datas):
    '''
    获取渲染层
    :return: 
    '''
    return _processing_(datas, _delete_)


def _handleRenderCallbacks(data):
    try:
        attr = data.split(".")[0]
        cmds.setAttr("defaultRenderGlobals." + attr , '', type="string")
        return True
    except:
        return False


def handleRenderCallbacks(datas):
    '''
    处理渲染回调函数值
    :return:
    '''
    return _processing_(datas, _handleRenderCallbacks)


def _handleCameras(data):
    node = data.split(".")[0]
    if not cmds.objExists(node):
        return True
    if cmds.referenceQuery(node, isNodeReferenced=True):
        return False
    try:
        cmds.setAttr(node + ".filmFit", l=False)
        cmds.setAttr(node + ".filmFit", 1)

        # 如果是默认的摄像机就不执行delete操作
        if node in utils.CAMERA_SHAPE_NAME_LIST:
            return True

        parent = cmds.listRelatives(node, parent=True)
        if len(parent) == 1:
            if cmds.lockNode(parent[0], q=True, lock=True):
                cmds.lockNode(parent[0], lock=False)
            cmds.delete(parent[0])
            return True
        else:
           return False
    except:
        return False


def handleCameras(datas):
    '''
    获取相机
    :return:
    '''
    return _processing_(datas, _handleCameras)


def handleUnusedML(datas):
    '''
    获取多余的材质
    :return:
    '''
    mel.eval("HypershadeWindow;")


def handleAovs(datas):
    '''
    获取AOvs
    :return:
    '''
    return _processing_(datas, _delete_)


def handleLights(datas):
    '''
    获取灯光
    :return: list
    '''
    return _processing_(datas, _delete_transform_)


def __handleConnections(s_attr, d_attr):
    '''
    :param s_attr:
    :param d_attr:
    :return:
    '''
    nodePlug = cmds.listConnections(d_attr, s=True, p=True)
    if nodePlug:
        if nodePlug[0] != s_attr:
            cmds.connectAttr(s_attr, d_attr, f=True)
    else:
        cmds.connectAttr(s_attr, d_attr, f=True)


def handleLightEditor(datas):
    '''
    处理灯光编辑器的显示项
    :param datas:
    :return:
    '''
    version = int(cmds.about(v=True))
    if version < 2017:
        return None

    ok_items = list()
    items = cmds.ls(type="lightItem")
    for item in items:
        inputs = cmds.listConnections(item+".light", s=True)
        if inputs:
            ok_items.append(item)

    if not cmds.objExists("lightEditor"):
        cmds.createNode("lightEditor", s=True, n="lightEditor")

    if ok_items:
        if len(ok_items) == 1:
            connections = cmds.listConnections("lightEditor.lastItem", s=True, c=True, p=True)
            if connections:
                cmds.disconnectAttr(connections[1], connections[0])

        else:
            for i in range(len(ok_items)-1):
                __handleConnections(ok_items[i] + ".next", ok_items[i+1] + ".previous")

            __handleConnections(ok_items[-1] + ".message", "lightEditor.lastItem")

        connections = cmds.listConnections(ok_items[0] + ".previous", s=True, c=True, p=True)
        if connections:
            cmds.disconnectAttr(connections[1], connections[0])

        __handleConnections(ok_items[0] + ".message", "lightEditor.firstItem")

    return _processing_(datas, _delete_)


def handleRenderSetup(datas):
    '''
    获取renderSetup信息
    :return: list
    '''
    return _processing_(datas, _delete_)


def _handleHeidMesh(data):
    try:
        cmds.setAttr(data + ".v", True)
        cmds.setAttr(data + ".intermediateObject", False)
        cmds.setAttr(data + ".hiddenInOutliner", False)
        mel.eval('AEdagNodeCommonRefreshOutliners();')
        return True
    except:
        return False


def handleHeidMesh(datas):
    '''
    获取隐藏的几何体(mesh)
    :param shapes:
    :return:
    '''
    return _processing_(datas, _handleHeidMesh)


def _handleShowColorMesh(data):
    try:
        cmds.setAttr(data + ".displayColors", False)
        return True
    except:
        return False


def handleShowColorMesh(datas):
    '''
    获取mesh顶点颜色显示
    :param shapes:
    :return:
    '''
    return _processing_(datas, _handleShowColorMesh)


def handleInstanceCopyMesh(datas=None):
    '''
    获取关联复制的shape
    :param shapes:
    :return:
    '''
    pass


def _handleDisplaySmoothMesh(data):
    cmds.displaySmoothness(data, polygonObject=0)
    return True


def handleDisplaySmoothMesh(datas):
    '''
    获取按3显示的shape
    :param shapes:
    :return:
    '''
    return _processing_(datas, _handleDisplaySmoothMesh)


def _handleHistoryMesh(data):
    if cmds.referenceQuery(data, isNodeReferenced=True):
        return False
    try:
        cmds.delete(data, ch=True)
        return True
    except:
        return False


def handleHistoryMesh(datas):
    '''
    获取有历史记录的shape
    :param shapes:
    :return:
    '''
    return _processing_(datas, _handleHistoryMesh)


def _handleRenderStatsMesh(data):
    '''
    :param name:
    :param dict:
    :return:
    '''
    state = True
    for attr in utils.SHAPE_DEFAULT_RENDER_STATS.keys():
        if cmds.objExists(data + attr):
            try:
                cmds.setAttr(data + attr, utils.SHAPE_DEFAULT_RENDER_STATS[attr])
            except:
                state = False
                return state
    return state


def handleRenderStatsMesh(datas):
    '''
    获取shape节点下的render stats是默认状态
    :param shapes:
    :return:
    '''
    return _processing_(datas, _handleRenderStatsMesh)


def handleAssignFaceShader(datas=None):
    '''
    获取按面给材质
    :return:
    '''
    try:
        evalScriptFromToolBox(u'按面给材质物体检测及修复')
    except:
        pass
    

def _handleMeshObjectPnts(data):
    if cmds.referenceQuery(data, isNodeReferenced=True):
        return False
    try:
        cmds.polyNormal(data, ch=True, normalMode=2, userNormalMode=0)
        cmds.delete(data, ch=True)
        return True
    except:
        return False


def handleMeshObjectPnts(datas):
    '''
    获取是否cv点有数据
    :return:
    '''
    return _processing_(datas, _handleMeshObjectPnts)


def handleMeshFiveSides(widget):
    '''
    获取五边面
    :return:
    '''
    name = "MeshFiveSidesUI"
    flush(name)

    datas = widget.getData()
    data = [data for data in datas if cmds.objExists(data)]
    win = detailedbackBaseWidget.DetailedbackBaseWidget(data=data, parent=widget.parent())
    win.setObjectName(name)
    win.resize(600, 800)
    return win
    

def handleMeshInfo(widget):
    '''
    获取shape信息
    :return:
    '''
    name = "shapeInfoUI"
    flush(name)

    data = widget.getData()
    win = widget.__class__(widget.parent())
    win.setData(data)
    win.setObjectName(name)
    win.setWindowTitle(u"Mesh信息")
    win.resize(600, 800)
    
    return win
    
def handleCheckTopo(datas):
    '''
    获取shape信息
    :return:
    '''
    return _processing_(datas, _handleMeshObjectPnts)



def handleNoRenderGrpSetting(datas):
    '''
    对不渲染组的模型进行修改
    :return:
    '''
    # shapes=checkBase.getNoRenderGrpSettting()
    # for shape in shapes:
    try:
        for data in datas:
            shapes = cmds.listRelatives(data, c=True, f=True)[0]
            for shape in shapes:
                for attr in utils.NORENDER_GRP_ATTRS:
                    cmds.setAttr("{}.{}".format(data,attr),0)
    except:
        pass
    return datas


def handleCheckShotStandard(select_data):
    """镜头标准
    """  
    if not select_data:
        return
    datas=checkBase.check_shot_satandard()
    if (not datas):
        return
    cmds.rename(select_data,datas[-1])


def handle_check_contains_group_cam(widget):
    nodes=cmds.ls(selection=True)
    if not nodes:
        cmds.confirmDialog(title=u'友情提示', message=u'请先选一个组，再执行此操作', button=['Yes'])
        return
    cmds.rename(nodes[0],"Cam")

def handle_update_ref_namespace(datas=None):
    # ly.update_ref_namespace()
    # scriptPath = 'Z:/Scripts/Mist/Mist_Alembic_Plugins/lib1'
    # for path in sys.path:
        # if path.count(scriptPath):
            # sys.path.remove(path)
    # sys.path.append(scriptPath)
    # import ly_maya_lib as ly_maya
    # reload(ly_maya)
    # ly_maya.update_ref_namespace()
    execfile('Z:/Scripts/Mist/Mist_Alembic_Plugins/Script/ResetAnimationNamespace.py', globals())

def handle_check_body_topo(datas=None):
    os.startfile("Z:/Resources/Mist/All/规范/资产角色流程规范/无法做BS的问题一键命令解决方法.mp4")

def handle_check_mesh_has_locked_normals(datas):
    if not datas:
        return
    cmds.undoInfo(openChunk=True)
    cmds.select(datas)
    #解除锁定发现-》设定为面，软化边-》删除历史
    cmds.polyNormalPerVertex(unFreezeNormal=True)
    cmds.polySetToFaceNormal()
    for data in datas:
        cmds.polySoftEdge(data,angle=180,constructionHistory=True)
    cmds.DeleteHistory()
    cmds.undoInfo(closeChunk=True)
    return datas

# 杨晓坤 20211116
def read_pic_in_aistandin(datas):
    execfile("Z:/Scripts/Maya/EaToolBox/maya/Tools/public/读取Maya文件Ass贴图.py")

#姜玉璐  20211215
def set_hairshape_attr(datas):
    try:
        for i in datas:
            cmds.setAttr(i + ".simulationMethod",1)
            cmds.setAttr(i + ".active",0)
    except:
        pass
    return datas
#姜玉璐  20211222
def set_shad_sg(datas):
    ref_list = []
    try:
        for i in datas:
            shading = cmds.connectionInfo(i+'.aiSurfaceShader',sfd =True).split('.')[0]
            if shading:
                spec_sg = shading + '_SG'
                if not cmds.referenceQuery(i,inr = True):
                    cmds.rename(i,spec_sg)
                    continue
                ref_list.append(i)
            else:
                shading = cmds.connectionInfo(i + '.surfaceShader', sfd=True).split('.')[0]
                spec_sg = shading + '_SG'
                if not cmds.referenceQuery(i,inr = True):
                    cmds.rename(i,spec_sg)
                    continue
                ref_list.append(i)
        if ref_list:
            cmds.confirmDialog(title=u'提示',message=u'修复完成，引用文件无法修复，请在源文件里修改',button=['Yes'], defaultButton='Yes')
    except:
        pass
    return datas

#姜玉璐  20220114
def _delete_redundant_attr(data):
    try:
        list_Attr = cmds.listAttr(data, k=True)
        for attr in list_Attr:
            if 'FBX' in attr:
                try:
                    cmds.deleteAttr(data,at=attr)
                except:
                    pass
        return True
    except:
        return False


def delete_redundant_attr(datas):
    return _processing_(datas, _delete_redundant_attr)


# 杨晓坤20220208
def rep_vertex_number(datas):
    """
    多余废点
    """
    import maya.api.OpenMaya as om_new

    error_list = []
    for shape_node in datas:
        meshName = cmds.listRelatives(shape_node, p=1, pa=1)[0]

        meshDag = om_new.MGlobal.getSelectionListByName(meshName).getDagPath(0)
        itVerts = om_new.MItMeshVertex(meshDag)
        mesh = om_new.MFnMesh(meshDag)
        vertex_num = mesh.numVertices
        weird_vertex_num = 0
        while not itVerts.isDone():
            if not itVerts.numConnectedEdges():
                cmds.delete("{}.vtx[{}]".format(shape_node, itVerts.index()))
                break
            itVerts.next()
    return datas


# 杨晓坤20220427
def delete_namespace(datas=None):
    if datas:
        for data in datas:
            cmds.namespace(data, mergeNamespaceWithParent=1, removeNamespace=1)

    pass
    return datas

# 杨晓坤20220509
def repair_multishape(datas=None):
    if datas:
        for data in datas:
            shapes = cmds.listRelatives(data, c=1, type="mesh", f=1)
            if shapes:
                for shape in shapes:
                    try:
                        if cmds.getAttr(shape + ".intermediateObject"):
                            print(shape)
                            cmds.delete(shape)
                    except:
                        pass
    return datas

def close_shapenode_attr(shape_node):
    cmds.setAttr((shape_node + ".castsShadows"), 0)
    cmds.setAttr((shape_node + ".receiveShadows"), 0)
    cmds.setAttr((shape_node + ".holdOut"), 0)
    cmds.setAttr((shape_node + ".motionBlur"), 0)
    cmds.setAttr((shape_node + ".primaryVisibility"), 0)
    cmds.setAttr((shape_node + ".smoothShading"), 0)
    cmds.setAttr((shape_node + ".visibleInReflections"), 0)
    cmds.setAttr((shape_node + ".visibleInRefractions"), 0)
    cmds.setAttr((shape_node + ".doubleSided"), 0)
    cmds.setAttr((shape_node + ".geometryAntialiasingOverride"), 0)
    cmds.setAttr((shape_node + ".aiOpaque"), 0)
    cmds.setAttr((shape_node + ".aiMatte"), 0)
    cmds.setAttr((shape_node + ".primaryVisibility"), 0)
    cmds.setAttr((shape_node + ".castsShadows"), 0)
    cmds.setAttr((shape_node + ".aiVisibleInDiffuseReflection"), 0)
    cmds.setAttr((shape_node + ".aiVisibleInSpecularReflection"), 0)
    cmds.setAttr((shape_node + ".aiVisibleInDiffuseTransmission"), 0)
    cmds.setAttr((shape_node + ".aiVisibleInSpecularTransmission"), 0)
    cmds.setAttr((shape_node + ".aiVisibleInVolume"), 0)
    cmds.setAttr((shape_node + ".aiSelfShadows"), 0)
def repair_facial_mesh(datas=None):

    body_objs = list()
    if cmds.objExists("Body_001_mo"):
        body_objs = cmds.ls("Body_001_mo")

    if len(body_objs)==1:
        if cmds.objExists("Body_Grp") and not cmds.objExists("Body_001_mo_facial"):
            copy_obj = cmds.duplicate(body_objs[0], rr=1, n="Body_001_mo_facial")
            try:
                cmds.parent(copy_obj, w=1)
            except:
                pass
            cmds.parent(copy_obj, "Body_Grp")
            cmds.setAttr((copy_obj[0] + ".visibility"), 0)
            for i in cmds.listRelatives(copy_obj, c=1, pa=1, type="mesh"):
                close_shapenode_attr(i)
        else:
            cmds.confirmDialog( title=u'Error!!',icon='critical', message=(u'请检查是否存在以下物体\nBody_Grp\nBody_001_mo_facial'), button=[u'关闭'])
    else:
        cmds.confirmDialog( title=u'Error!!',icon='critical', message=(u'以下物体存在多个\nBody_001_mo'), button=[u'关闭'])
    return datas



# 杨晓坤20220513
def set_shapenode_attr(shape_node):
    cmds.setAttr((shape_node + ".castsShadows"), 1)
    cmds.setAttr((shape_node + ".receiveShadows"), 1)
    cmds.setAttr((shape_node + ".holdOut"), 0)
    cmds.setAttr((shape_node + ".motionBlur"), 1)
    cmds.setAttr((shape_node + ".primaryVisibility"), 1)
    cmds.setAttr((shape_node + ".smoothShading"), 1)
    cmds.setAttr((shape_node + ".visibleInReflections"), 1)
    cmds.setAttr((shape_node + ".visibleInRefractions"), 1)
    cmds.setAttr((shape_node + ".doubleSided"), 1)

    cmds.setAttr((shape_node + ".primaryVisibility"), 1)
    cmds.setAttr((shape_node + ".castsShadows"), 1)
    cmds.setAttr((shape_node + ".aiVisibleInDiffuseReflection"), 1)
    cmds.setAttr((shape_node + ".aiVisibleInSpecularReflection"), 1)
    cmds.setAttr((shape_node + ".aiVisibleInDiffuseTransmission"), 1)
    cmds.setAttr((shape_node + ".aiVisibleInSpecularTransmission"), 1)
    cmds.setAttr((shape_node + ".aiVisibleInVolume"), 1)
    cmds.setAttr((shape_node + ".aiSelfShadows"), 1)

def repair_render_stats(datas=None):
    for data in datas:
        set_shapenode_attr(data)
    return datas
# 杨晓坤20220517
def repair_disrender_stats(datas=None):
    for data in datas:
        close_shapenode_attr(data)
    return datas
    
# 罗庸 20230209
def repair_shapeNameError(datas=None):
    if datas:
        for obj in datas:
            if cmds.nodeType(obj) != 'transform':
                continue
            shapes = cmds.ls(obj, type="mesh", ni=True, dag=True)
            print shapes
            if shapes:
                for shape in shapes:
                    tranName = obj.split('|')[-1]
                    try:
                        newName = '{}Shape'.format(tranName)
                        cmds.rename(shape, newName)
                    except:
                        pass
    return datas
    
# 罗庸 20230511
def convertInstanceMeshToNormalObject(datas=None):
    for each in datas:
        cmds.select(each, r=True)
        mel.eval('ConvertInstanceToObject')
    return datas
    
# 罗庸 20230515   
def repair_TransformLock(datas=None):
    for each in datas:
        for attr in 'trs':
            for axis in 'xyz':
                cmds.setAttr('{}.{}{}'.format(each, attr, axis), l=False)
    return datas
    