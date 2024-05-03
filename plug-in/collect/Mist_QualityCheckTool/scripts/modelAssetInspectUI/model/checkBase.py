# -*- coding: utf-8 -*-

import sys
from modelAssetInspectUI.common import util_helper

if sys.version_info[0] == 2:
    reload(util_helper)
elif sys.version_info[0] > 2:
    try: 
        import importlib
        importlib.reload(util_helper)
    except:
        pass

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import modelAssetInspectUI.common.utils as utils
import maya.mel as mel
# import pymel.core as pm
import re,os
import struct
import arnold as ar
try:
    try:
        import tool_box_library.modeling.checkRename as checkRename
        import tool_box_library.modeling.checkAssignFaceShader as checkAssignFaceShader
    except:
        import toolbox_library.modeling.checkRename as checkRename
        import toolbox_library.modeling.checkAssignFaceShader as checkAssignFaceShader
except:
    import checkRename
    import checkAssignFaceShader    
try:
    import maya.app.renderSetup.model.renderSetup as renderSetup
except:
    pass


def getCheckUnknownNode(fun=None):
    """
    获取未知节点
    :return: list 
    """
    if fun:
        fun()

    values = cmds.ls(type=['unknown', 'unknownTransform', "blindDataTemplate", "polyBlindData", "poseInterpolatorManager", "shapeEditorManager"])
    # 过滤掉Non-deletable
    _values = []
    for node in values:
        if not cmds.ls(node, ud=True):
            _values.append(node)
    values = _values        
    # 面材质，过滤groupId
    for grpid in cmds.ls(type="groupId"):
        if not cmds.listConnections(grpid, s=0, d=1):
            values.append(grpid)
    # 绑定，过滤groupParts
    for grpid in cmds.ls(type="groupParts"):
        if not cmds.listConnections(grpid, s=0, d=1):
            values.append(grpid)

    return values


def getCheckRename(fun=None):
    '''
    获取检查重名
    :return: bool
    '''
    value = checkRename.getFirstAllSameNameList(1, 1)

    return value
    
 

def getCheckEmptyGrp(fun=None):
    '''
    获取检查重名
    :return: bool
    '''
    value = []
    def checkEmpty(dag):
        
        if cmds.nodeType(dag) != 'transform':
            return False
            
        isEmpty = True    
        child = cmds.listRelatives(dag, c=True, f=True)
        if child:
            
            for each in child:
                if cmds.nodeType(each) == 'transform':
                    status = checkEmpty(each)
                else:
                    status = False
                isEmpty &= status
                if not isEmpty:
                    break     
        return isEmpty    

    for grp in cmds.ls(tr=True, l=True):
        status = checkEmpty(grp)
        if status:
            value.append(grp)
        
    return value    

def getCheckSpaceName(fun=None):
    """
    获取空间名
    :return: list
    """
    if fun:
        fun()
    
    uncheck_list = [":UI", ":shared"]

    namespaces = cmds.namespaceInfo(':', recurse=True, listOnlyNamespaces=True, absoluteName=True)

    refList = cmds.ls(references = True)
    allReferenceNodeList = list()
    objList = list()
    for ref in refList:
        try:
            if cmds.referenceQuery(ref,isLoaded = True) or not cmds.referenceQuery(ref,isLoaded = True):
                if cmds.referenceQuery( ref, filename=True, parent=True ):
                    allReferenceNodeList.append(ref)
        except:
            pass
    
    
    for refnode in allReferenceNodeList:
        ref_ns = cmds.referenceQuery(refnode, ns=1)
        if not ref_ns in uncheck_list:
            uncheck_list.append(ref_ns)

    
    values = [n for n in namespaces if n not in uncheck_list]

    return values


def getCheckAnimationLayer(fun=None):
    """
    获取动画层
    :return: list
    """
    if fun:
        fun()

    values =[layer for layer in cmds.ls(type='animLayer')]
    return values


def getCheckDisplayLayer(fun=None):
    '''
    获取显示层
    :return:
    '''
    if fun:
        fun()
    result=list()
    render_layers=cmds.ls(type='displayLayer')
    for render in render_layers:
        #以default为结尾的以及引用文件格式的不以数字结尾的就跳过
        if  render.endswith(utils.DEFAULT_LAYER) or render == 'jointLayer':
            continue
        result.append(render)
    return result


def getCheckExpression(fun=None):
    '''

    :param fun:
    :return:
    '''
    if fun:
        fun()
    return cmds.ls(type=["expression", "script"])


def getCheckFileRoot(fun=None):
    '''
    获取Geometry组
    :return: list
    '''
    if fun:
        fun()

    top_level_list = [i for i in cmds.ls(assemblies=True) if i not in utils.CAMERA_NAME_LIST]
    if utils.GEOMETRY in top_level_list:
        top_level_list.remove(utils.GEOMETRY)
        return top_level_list
    else:
        return top_level_list


def getSecneAllTransform():
    '''

    :return:
    '''
    values = [i for i in cmds.ls(type='transform') if i not in utils.CAMERA_NAME_LIST]
    return values


def getCheckNodeAttr(name, attr_dict):
    '''
    :param name:
    :param dict:
    :return:
    '''
    for attr in attr_dict.keys():
        if cmds.objExists(name + attr):
            value = cmds.getAttr(name + attr)
            if round(value, 6) != attr_dict[attr]:
                return name


def getCheckFilter(datas):
    pass


def getCheckFreezeTransformation(fun=None):
    '''
    获取未冻结transform节点
    :param transforms:
    :return:
    '''
    transforms = []
    unfrozen_list = list()
    meshs = cmds.ls(type='mesh')
    for i in meshs:
        trans = cmds.listRelatives(i, p=True,f = True)[0]
        if trans not in transforms:
            transforms.append(trans)
    num = len(transforms)
    for name in transforms:
        if fun:
            state = fun(name, num)
            if not state:
                return

        value = getCheckNodeAttr(name, utils.TRANSFORM_ATTR_DICT)
        if value:
            unfrozen_list.append(value)

    return unfrozen_list


def getCheckReseTransformation(fun=None):
    '''
    获取没有在世界坐标中心的物体
    :param transforms:
    :return:
    '''
    transform = []
    unrese_list = list()
    meshs = cmds.ls(type='mesh')
    for mesh in meshs:
        trans = cmds.listRelatives(mesh, p=True,f = True)[0]
        if trans not in transform:
            transform.append(trans)

    num = len(transform)
    for name in transform:
        if fun:
            state = fun(name, num)
            if not state:
                return

        values = cmds.xform(name, q=True, ws=True, rp=True)
        values_sp = cmds.xform(name, q=True, ws=True, sp=True)
        values.extend(values_sp)
        for v in values:
            if round(v, 6) != 0:
                if name not in unrese_list:
                    unrese_list.append(name)

    return unrese_list


def getCheckKFramTransforms(fun=None):
    '''
    获取k帧的物体
    :return:
    '''
    kfram_list = list()
    animCurves = cmds.ls(type=["animCurveTL", "animCurveTA", "animCurveTT", 'animCurveTU'])

    num = len(animCurves)
    for anim in animCurves:
        if fun:
            state = fun(anim, num)
            if not state:
                return

        nodes = cmds.listConnections(anim, s=False, d=True)
        if nodes:
            for node in nodes:
                if node not in kfram_list:
                    if getCheckNodeAttr(node,utils.TRANSFORM_ATTR_DICT):
                        kfram_list.append(node)

    return kfram_list


def getCheckTransformShapes(fun=None):
    '''
    获取shape节点2个以上的模型
    :param transforms:
    :return:
    '''
    transforms = getSecneAllTransform()
    shapes_list = list()
    trans_list = []
    for name in transforms:
        if cmds.keyframe(name, q=True):
            trans_list.append(name)
    num = len(trans_list)
    for name in trans_list:
        if fun:
            state = fun(name, num)
            if not state:
                return
        if cmds.nodeType(name) != "nurbsCurve":
            values = cmds.listRelatives(name, s=True, f=True)
            if values:
                if len(values) > 1:
                    tem_list = list()
                    for value in values:
                        value_long = cmds.ls(value, long=False)[0]
                        tem_list.append(value_long)
                    shapes_list.append([name, tem_list])

    return shapes_list


def getIntermediateObjectDatas(datas):
    '''
    获取shape节点2个以上的模型的中间模型
    :param datas: 
    :return: 
    '''
    mesh_datas = list()
    for data in datas:
        if isinstance(data, list):
            for i in data[1]:
                if cmds.objectType(i, isType='mesh'):
                    value = cmds.getAttr(i+".intermediateObject")
                    mesh_datas.append([i, value])

    return mesh_datas


def getCheckHideTransforms(fun=None):
    '''
    获取隐藏的几何体(transform)
    :param transforms:
    :return:
    '''
    transforms = getSecneAllTransform()
    hide_list = list()

    num = len(transforms)
    for name in transforms:
        if fun:
            state = fun(name, num)
            if not state:
                return
        if cmds.nodeType(name) not in ["joint","nurbsCurve"]:
            value = cmds.getAttr(name+".v")
            if not value:
                hide_list.append(name)

    return hide_list


def getCheckRenderLayer(fun=None):
    '''
    获取渲染层
    :return: 
    '''
    if fun:
        fun()
    result=list()
    render_layers=cmds.ls(type='renderLayer')
    ref_node=cmds.ls(type="reference") 
    for render in render_layers:
        #以default为结尾的以及引用文件格式的不以数字结尾的就跳过
        print(render)
        if  render.endswith(utils.DEFAULT_RENDER_LAYER) or re.match(".*?:.*(?!\d+)$",render):
            if render.split(':',1)[0]+'RN' in ref_node:
                continue
            elif render == 'defaultRenderLayer':
                continue
            else:
                result.append(render)
        else:
            result.append(render)
    return result


def getCheckRenderCallbacks(fun=None):
    '''
    获取渲染回调函数值
    :return:
    '''
    if fun:
        fun()

    attr_list = list()
    for attr in utils.RENDERING_ATTR_LIST:
        value = cmds.getAttr('defaultRenderGlobals.'+ attr)
        if value:
            attr_list.append("{0}.({1})".format(attr, value))

    return attr_list


def getCheckCameras(fun=None):
    '''
    获取相机
    :return:
    '''
    cameras = list()
    scene_cameras = cmds.ls(type='camera')

    num = len(scene_cameras)
    for c in scene_cameras:
        if fun:
            state = fun(c, num)
            if not state:
                return

        if c in utils.CAMERA_SHAPE_NAME_LIST:
            if cmds.getAttr(c+".filmFit") != 1:
                cameras.append(c+u".(相机不是默认参数(filmFit))")
        else:
            cameras.append(c+u".(多余的相机)")
    return cameras


def getCheckConnect(name):
    state = True
    try:
        cons = cmds.listConnections(name, shapes=True, connections=True, source=False)
        if cons:
            for con_a, con_b in zip(cons[::2], cons[1::2]):
                thirdPartyPreventDeletions = cmds.callbacks(name, con_b, con_a, executeCallbacks=True,
                                                            hook="preventMaterialDeletionFromCleanUpSceneCommand")
                for deletionPrevented in thirdPartyPreventDeletions:
                    if deletionPrevented:
                        state = False
                        return state

        return state
    except:
        return False


def getCheckUnusedML(fun=None):
    '''
    获取多余的材质
    :return:
    '''
    if fun:
        fun()

    values = list()

    UnusedML_list = list()
    sets = cmds.ls(sets=True)
    for set_name in sets:
        if mel.eval('shadingGroupUnused("{}")'.format(set_name)):
            state = getCheckConnect(set_name)
            if state:
                if set_name not in utils.DEFAULT_SET:
                    UnusedML_list.append(set_name)

    shader_list = list()
    materials = cmds.ls(long=True, mat=True)
    for material in materials:
        try:
            shouldDelete = True
            cons = cmds.listConnections(material, shapes=True, connections=True, source=False)
            if cons:
                for con_a, con_b in zip(cons[::2], cons[1::2]):
                    if con_a != material+".message":
                        shouldDelete = False
                        break
                    else:
                        se = cmds.listConnections(con_a, type="shadingEngine")
                        thirdPartyPreventDeletions = cmds.callbacks(material, con_b, con_a, executeCallbacks=True,
                                                                    hook="preventMaterialDeletionFromCleanUpSceneCommand")
                        thirdPartyPreventsDeletion = False
                        for deletionPrevented in thirdPartyPreventDeletions:
                            if deletionPrevented:
                                thirdPartyPreventsDeletion = True
                                break
                        if se:
                            shouldDelete = False
                            break
                        elif thirdPartyPreventsDeletion:
                            shouldDelete = False
                            break
                        else:
                            shouldDelete = True

            if shouldDelete:
                if material != 'standardSurface1':
                    shader_list.append(material)
        except:
            pass

    values.extend(UnusedML_list)
    values.extend(shader_list)
    return values


# def getCheckAovs(fun=None):
    # '''
    # 获取AOvs
    # :return:
    # '''
    # if fun:
        # fun()
    # try:
        # import mtoa.aovs as aovs
        # renderOption = aovs.AOVInterface()
        # AOVs = renderOption.getAOVs()
        # values = [AOV.node for AOV in AOVs]
        # return values
    # except:
        # return []

# 罗庸 20230626
def getCheckAovs(fun=None):
    '''
    获取AOvs
    :return:
    '''
    if fun:
        fun()
    
    invalid_aov_list = []
    if cmds.objExists('defaultArnoldRenderOptions'):
        aov_list = cmds.ls(type='aiAOV')
        active_aov_list = cmds.listConnections('defaultArnoldRenderOptions.aovList', s=True, d=False, type='aiAOV')
        for aov in aov_list:
            if not aov in active_aov_list and not aov in invalid_aov_list:
                invalid_aov_list.append(aov)
    return invalid_aov_list        


def getCheckLights(fun=None):
    '''
    获取灯光
    :return: list
    '''
    if fun:
        fun()

    types = cmds.listNodeTypes("light")

    # renderSetup类型节点去掉
    renderSetup_list = [u'lightItem', u'lightGroup', u'lightEditor']

    types = [i for i in types if i not in renderSetup_list]

    return cmds.ls(type=types)


def getCheckLightEditor(fun=None):
    '''
    获取灯光编辑器的显示项
    :return:
    '''
    if fun:
        fun()

    error_items = list()
    items = cmds.ls(type="lightItem")
    for item in items:
        inputs = cmds.listConnections(item+".light", s=True)
        if not inputs:
            error_items.append(item)

    return error_items


def getCheckRenderSetup(fun=None):
    '''
    获取renderSetup信息
    :return: list
    '''
    if fun:
        fun()
    try:
        rs = renderSetup.instance()
        values = [r.name() for r in rs.getRenderLayers()]
        return values
    except:
        return list()


def getSceneMesh():
    '''
    :return:
    '''
    shapes = cmds.ls(type=['mesh', 'nurbsCurve'])
    return shapes


def getCheckHeidMesh(fun=None):
    '''
    获取隐藏的几何体(mesh)
    :param shapes:
    :return:
    '''
    shapes = cmds.ls(type='mesh',l = 1)
    heidMesh_list = list()

    num = len(shapes)
    for shape in shapes:
        if fun:
            state = fun(shape, num)
            if not state:
                return

        value = cmds.getAttr(shape+".v")
        value1 = cmds.getAttr(shape+".hiddenInOutliner")
        value2 = cmds.getAttr(shape+".intermediateObject")
        if not value or value1 or value2:
            heidMesh_list.append(shape)
    return heidMesh_list


def getCheckShowColorMesh(fun=None):
    '''
    获取mesh顶点颜色显示
    :param shapes:
    :return:
    '''
    shapes = getSceneMesh()
    heidMesh_list = list()

    num = len(shapes)
    for shape in shapes:
        if fun:
            state = fun(shape, num)
            if not state:
                return

        if cmds.objExists(shape+".displayColors"):
            value = cmds.getAttr(shape+".displayColors")
            if value:
                trans = cmds.listRelatives(shape, p=1)
                if trans not in heidMesh_list:
                    heidMesh_list.append(trans)
    return heidMesh_list


def getCheckInstanceCopyMesh(fun=None):
    '''
    获取关联复制的shape
    :param shapes:
    :return:
    '''
    shapes = cmds.ls(type='mesh', l=True)
    if not shapes:
        return
    mesh_list = list()

    num = len(shapes)
    for shape in shapes:
        print(shape)
        longname=shape
        shortname=shape.split('|')[-1]
        is_skip=False
        for skip in utils.CHECK_MESH_SKIP_SOME_NAME:
            if skip in longname:
                is_skip=True
                break
        if is_skip:
            continue
        if fun:   
            state = fun(shortname, num)
            if not state:
                return
        values = cmds.listRelatives(shape, allParents=True, path=True)
        if len(values) > 1:
            mesh_list.extend(values)
    return mesh_list
    

def getCheckDisplaySmoothMesh(fun=None):
    '''
    获取按3显示的shape
    :param shapes:
    :return:
    '''
    shapes = getSceneMesh()
    mesh_list = list()

    num = len(shapes)
    for shape in shapes:
        if fun:
            state = fun(shape, num)
            if not state:
                return

        values = cmds.displaySmoothness(shape, q=True, polygonObject=True)
        if values:
            if int(values[0]) == 3:
                mesh_list.append(shape)
            if int(values[0]) == 2:
                mesh_list.append(shape)

    return mesh_list


def getCheckHistoryMesh(fun=None):
    '''
    获取有历史记录的shape
    :param shapes:
    :return:
    '''
    shapes = getSceneMesh()
    mesh_list = list()

    num = len(shapes)
    for shape in shapes:
        if fun:
            state = fun(shape, num)
            if not state:
                return

        values = cmds.listHistory(shape, il=2)
        value_state = False
        if not values:
            continue
        for v in values:
            if v == shape:
                continue
            if v == shape.split("|")[-1]:
                continue
            try:
                if cmds.objectType(v) not in ["displayLayer", "renderLayer", "renderLayerManager", 'shadingEngine', "file", "place2dTexture"]:
                    value_state = True
                    break
            except:
                pass
        if value_state:
            mesh_list.append(shape)

    return mesh_list


def getCheckRenderStatsMesh(fun=None):
    '''
    获取shape节点下的render stats是默认状态
    :param shapes:
    :return:
    '''
    shapes = cmds.ls(type='mesh')
    mesh_list = list()

    num = len(shapes)
    for shape in shapes:
        if fun:
            state = fun(shape, num)
            if not state:
                return

        value = getCheckNodeAttr(shape, utils.SHAPE_DEFAULT_RENDER_STATS)
        if value:
            trans = cmds.listRelatives(shape, p=1)
            if trans not in mesh_list:
                mesh_list.append(trans)

    return mesh_list


def getCheckAssignFaceShader(fun=None):
    '''
    获取按面给材质
    :return:
    '''
    value=list()
    can_fix,cant_fix = checkAssignFaceShader.getAssignFaceShaderTypeListFromAll()
    if can_fix:
        value.extend(can_fix)
    if cant_fix:
        value.extend(cant_fix)
    return value



def _meshObjectPnts(mesh):
    '''
    :param mesh:
    :return:
    '''
    try:
        vertices = cmds.getAttr(mesh + '.pnts[*]')
        for v in vertices:
            v = [round(i, 6) for i in v]
            if v != [0.0, 0.0, 0.0]:
                return mesh

        return None
    except:
        return None


def getCheckMeshObjectPnts(fun=None):
    '''
    获取是否cv点有数据
    :return:
    '''
    values = list()
    mesh_list = cmds.ls(type='mesh')

    num = len(mesh_list)
    for mesh in mesh_list:
        trans = cmds.listRelatives(mesh, p=True, type='transform')[0]
        if fun:
            state = fun(mesh, num)
            if not state:
                return

        value = _meshObjectPnts(mesh)
        if value:
            values.append(trans)

    return values


def _meshFiveSides(mesh):
    '''
    :param mesh:
    :return:
    '''
    numFaces = cmds.polyEvaluate(mesh, f=True)
    for i in xrange(numFaces):
        info = cmds.polyInfo(mesh + ".f[" + str(i) + "]", fv=True)[0]
        if len(info.split()[2:]) >= 5:
            return mesh
    return None


# def getCheckMeshFiveSides(fun=None):
#     '''
#     获取五边面
#     :return:
#     '''
#     values = list()
#     mesh_list = cmds.ls(type='mesh')
#
#     num = len(mesh_list)
#     for mesh in mesh_list:
#         if fun:
#             state = fun(mesh, num)
#             if not state:
#                 return
#
#         value = _meshFiveSides(mesh)
#         if value:
#             values.append(value)
#     return values
#姜玉璐20210121
# def getCheckMeshFiveSides(fun=None):
#     values = []
#     face_list = []
#     shapes = cmds.ls(type='mesh')
#     transform = cmds.listRelatives(shapes, p=1, f=1)
#     num = len(list(set(transform)))
#     for trans in list(set(transform)):
#         if fun:
#             state = fun(trans, num)
#             if not state:
#                 return
#         mobj = pm.PyNode(trans).__apimobject__()
#         mitfaceiter = OpenMaya.MItMeshPolygon(mobj)
#         while not mitfaceiter.isDone():
#             edges = OpenMaya.MIntArray()
#             mitfaceiter.getEdges(edges)
#             if edges.length() >= 5:
#                 face = trans+".f[{0}]".format(str(mitfaceiter.index()))
#                 if trans not in values:
#                     values.append(trans)
#                 face_list.append(face)
#             mitfaceiter.next()
#     cmds.select(face_list,r = 1)
#     return values


def getCheckMeshFiveSides(fun=None):
    values = []
    tree_list = []
    shapes = cmds.ls(type='mesh')
    num = len(list(set(shapes)))
    for trans in list(set(shapes)):
        face_list = []
        if fun:
            state = fun(trans, num)
            if not state:
                return
        # mobj = pm.PyNode(trans).__apimobject__()
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(trans)
        dag_path = OpenMaya.MDagPath()
        selectionList.getDagPath(0, dag_path)
        
        try:
            mitfaceiter = OpenMaya.MItMeshPolygon(dag_path)
        except:
            values.append([trans, []])
            continue
        
        while not mitfaceiter.isDone():
            edges = OpenMaya.MIntArray()
            mitfaceiter.getEdges(edges)
            if edges.length() >= 5:
                face = trans+".f[{0}]".format(str(mitfaceiter.index()))
                face_list.append(face)
            mitfaceiter.next()
        if face_list:
            values.append([trans, face_list])

    return values


def _getMeshFiveSides(mesh):
    '''
    :param mesh:
    :return:
    '''
    value = list()
    num = cmds.polyEvaluate(mesh, f=True)
    for i in xrange(num):
        face = mesh + ".f[" + str(i) + "]"
        info = cmds.polyInfo(face, fv=True)[0]
        if len(info.split()[2:]) >= 5:
            value.append(face)
    return value


def getCheckDetailedMeshFiveSides(datas=None, fun=None):
    '''
    获取详细五边面信息
    :return:
    '''
    values = list()

    if datas is None:
        datas = cmds.ls(type='mesh')

    if not isinstance(datas, list):
        raise ValueError("({})Value is not of type list".format(datas))

    num = len(datas)
    for data in datas:
        if fun:
            state = fun(data, num)
            if not state:
                return

        value = _getMeshFiveSides(data)
        if value:
            values.append([data, value])
    return values


def getCheckMeshInfo(fun=None):
    '''
    获取shape信息
    :return:
    '''
    values = list()
    mesh_list = cmds.ls(type='mesh')

    num = len(mesh_list)
    for mesh in mesh_list:
        if fun:
            state = fun(mesh, num)
            if not state:
                return

        datas = list()
        value = getShapVolume(mesh)
        face_value = cmds.polyEvaluate(mesh, f=True)

        datas.append(mesh)
        datas.append(str(round(face_value/10000.0, 2)))
        datas.append(str(round(value/10000, 2)))

        values.append(datas)

    new_values = sorted(values, key=lambda data: float(data[1]), reverse=True)
    return new_values


def getCheckZeroVEF(fun=None):
    '''
    检查0点0线0面
    :return:
    '''
    value = list()
    source = cmds.ls(type='mesh')
    if source is []:
        return value
    for src in source:
        print(src)
        transforms=cmds.listRelatives(src,type="transform",p=True)
        if transforms:
            face_count = cmds.polyEvaluate(src, f=True)
            edge_count = cmds.polyEvaluate(src, e=True)
            point_count = cmds.polyEvaluate(src, v=True)
            if (face_count * edge_count * point_count) is 0:
                value.append(src)
    return value

def getCheckBodyTopo(fun=None):
    '''
    compare mesh
    :return:
    '''
    value = list()
    source = cmds.ls(u'Body*_mo')
    target = cmds.ls(u'body*_NoRd')
    if source is []:
        value.append(u'找不到\'Body mo\'')
        return value

    if target is []:
        value.append(u'找不到\'body NoRd\'')
        return value
    num = len(source)
    for src in source:
        if fun:
            state = fun(src, num)
            if not state:
                return
        tgt = src.split(u'_mo')[0] + u'_NoRd'
        tgt = tgt.replace("Body",'body')
        if not cmds.objExists(tgt):
            value.append(u'\'' + tgt + u'\'  模型缺失 ')
            continue
        status = True
        sourcefacecount = cmds.polyEvaluate(src, f=True)
        targetfacecount = cmds.polyEvaluate(tgt, f=True)
        sourceedgecount = cmds.polyEvaluate(src, e=True)
        targetedgecount = cmds.polyEvaluate(tgt, e=True)
        sourcepointcount = cmds.polyEvaluate(src, v=True)
        targetpointcount = cmds.polyEvaluate(tgt, v=True)
    
        status &= (sourcefacecount == targetfacecount)
        status &= (sourceedgecount == targetedgecount)  
        status &= (sourcepointcount == sourcepointcount)    
        if status is False:
            value.append(u'\'' + src + u'\' 跟 \'' + tgt + u'\' 拓扑不一致 ')
    
    
    return value


def getNoRenderGrpSettting(fun=None):
    result=list()
    grp_name="NoRender_Grp"
    if not cmds.objExists(grp_name):
        return result
    # transforms= cmds.listRelatives(grp_name,allDescendents=True)
    shapes=cmds.ls(grp_name,l=1,dag = 1,et=['mesh'])
    if not shapes:
        return result
    for shape in shapes:
        for attr in utils.NORENDER_GRP_ATTRS:
            attr_value=cmds.getAttr("{}.{}".format(shape,attr))
            if attr_value:
                trans = cmds.listRelatives(shape,p = True,f = True)[0]
                if trans not in result and not "NoRd" in trans:
                    result.append(trans)
                break
    return result


def getCheckMeshWithSameName(fun=None):
    '''
    check mesh name
    :return:
    '''
    value = list()
    shapes = cmds.ls(type='mesh')
    # check shape
    if shapes is []:
        value.append(u'场景中找不到任何模型')
        return value

    for each in shapes:
        if each.count('|') > 0:
            value.append(each)

    # check transform
    transforms = cmds.listRelatives(shapes, p=True, type='transform')
    lTransfroms = cmds.ls(transforms)
    for each in lTransfroms:
        if each.count('|') > 0:
            value.append(each)

    value = list(set(value))
    return value

def checkAllPolygonSameName(fun=None):
    '''
    检查所有polygon相同名称
    '''
    error_list = checkRename.getAllPolygonSameNameList(True,True)
    for i in cmds.ls(type="transform"):
        if len(cmds.ls(i.rsplit(":",1)[-1],r=1)) >1:
            error_list.append(i)
        
        
    for i in cmds.ls(type="mesh"):
        if len(cmds.ls(i.rsplit(":",1)[-1],r=1)) >1:
            error_list.append(i)

    return error_list
# def checkAllPolygonSameName(fun=None):
#     value = []
#     shapes = cmds.ls(type='mesh')
#
#     for each in shapes:
#         if each.count('|') > 0:
#             value.append(each)
#     return value


def checkAllSameName(fun=None):
    '''
    检查所有dagObject
    '''
    return checkRename.getAllSameNameList(True,True)
# def checkAllSameName(fun=None):
#     value = list()
#     dagObjects = cmds.ls(dag=1)
#
#     for each in dagObjects:
#         if each.count('|') > 0:
#             value.append(each)
#     return value

def checkMoreThanOneUvSet(func=None):
    """检查超过一个uvset
    """    
    result=list()
    meshes=cmds.ls(type="mesh")
    if not meshes:
        return result
    transforms = cmds.listRelatives(meshes, f=True, p=True, type='transform')
    for tran in transforms:
        indices=cmds.polyUVSet(tran,query=True,allUVSets=True)
        if indices and len(indices)>1:
            result.append(tran)
    return result

def getShapVolume(mesh):
    '''
    :param mesh: 
    :return: 
    '''
    values = cmds.polyEvaluate(mesh, b=True)
    datas = [abs(v[0]-v[1]) for v in values]
    return datas[0]*datas[1]*datas[2]

def check_mesh_has_locked_normals(func=None):
    """检查模型有锁定法线
    """    
    result=list()
    meshes=cmds.ls(type="mesh", l=True)
    if not meshes:
        return result
    result_temp=list()
    for mesh in meshes:
        longname=mesh
        contains=False
        for skip in utils.CHECK_MESH_SKIP_SOME_NAME:
            if skip in longname:
                contains=True
                break
        if contains:
            continue
        mesh_vertexface = cmds.polyListComponentConversion(mesh, toVertexFace=True)
        if not mesh_vertexface:
            continue
        locked_normals = cmds.polyNormalPerVertex(mesh_vertexface, q=1, freezeNormal=True)
        if any(locked_normals):
            result_temp.append(mesh)
    transform=cmds.listRelatives(result_temp,f=True, parent=True)
    if transform:
        for i in transform:
            result.append(i)
    return result


def check_file_name_is_shot(func=None):
    location=cmds.file(query=True,location=True)
    file_name=util_helper.UtilFileHelper.get_file_name_without_ext(location)
    value=[]
    if "shot" not in file_name:
        value.append("当前项目文件名没有shot")
    return value

def check_contains_group_cam(func=None):
    #检查包含Cam组
    value=list()
    node=cmds.ls("CAM")
    if not node:
        value.append("没有找到CAM组,请规范一下组名")
    return value

def check_shot_satandard(func=None):
    value=list()
     #检查镜头名称
    location=cmds.file(query=True,location=True)
    file_name=util_helper.UtilFileHelper.get_file_name_without_ext(location)
   
    cams=cmds.ls(type="camera")
    transforms=cmds.listRelatives(cams,f=True, parent=True,type="transform")
    shots=[]
    for i in transforms:
        if i in utils.CAMERA_NAME_LIST:
            continue
        shots.append(i)
    if not shots:
        value.append("没有发现有效摄像机")
        return value

    start_frame=int(cmds.playbackOptions(query=True,minTime=True))
    end_frame=int(cmds.playbackOptions(query=True,maxTime=True))
        
    standard_shot_name_regex=""
    prefix="CAM"
    if "SC" not in file_name:
        prefix="cam"
    standard_shot_name_regex="{}_{}_{}_{}".format(prefix,file_name,start_frame,end_frame)
    replace_strs=["_final","_char","_LAY","_ANI"]
    for replace_str in replace_strs:
        standard_shot_name_regex=standard_shot_name_regex.replace(replace_str,"")
    for shot in shots:
        shot_name=shot
        if re.match(standard_shot_name_regex,shot_name):
            return value
    for shot in shots:
        shot_name=shot
        value.append(shot_name)
    value.append("选中要改的镜头改成")
    value.append(standard_shot_name_regex)
    return value 


def check_is_chars_ex(func=None):
    """检查角色Ex档
    """
    chars=u"chars"
    return check_file_type_and_end(chars,"_EX")

#姜玉璐20211221
def check_is_prop_h(func=None):
    """检查道具EX档
    """    
    #props=u"props"

    refs = cmds.ls(type="reference")
    error_list = []
    for ref in refs:
        try:
            unresolved_name = cmds.referenceQuery(ref, filename=True, wcn=True)
            name_space = cmds.referenceQuery(ref, namespace=True).replace(":", "")
            temp_filename = os.path.splitext(os.path.split(unresolved_name)[1])[0]
            if 'props' in temp_filename and not temp_filename.endswith('_EX'):
                root_node = cmds.referenceQuery(ref, n=True, dp=True)[0]
                error_list.append(root_node)
        except:
            continue
    return error_list
    #return check_file_type_and_end(props,"_EX")

# def check_namespace_equel_ref_file_name_old(fun=None):
#     """检查名称空间不等于文件名
#     """ 
#     error_list = []

#     refList = cmds.ls(references = True)
#     allReferenceNodeList = list()
#     objList = list()
#     for ref in refList:
#         try:
#             if cmds.referenceQuery(ref,isLoaded = True) or not cmds.referenceQuery(ref,isLoaded = True):
#                 if cmds.referenceQuery( ref, filename=True, parent=True ):
#                     allReferenceNodeList.append(ref)
#         except:
#             pass
#     for rfnode in allReferenceNodeList:
#         file_path=cmds.referenceQuery(rfnode,f=1)
#         file_name=''
#         file_num=''
#         ns_str=cmds.referenceQuery(rfnode,ns=1).rsplit(':',1)[1]
#         if '{' in file_path:
#             file_name=file_path.rsplit('/',1)[1][:-3].rsplit('.',1)[0]
#             file_num=file_path.rsplit('{',1)[1][:-1]
#         else:
#             file_name=file_path.rsplit('/',1)[1].rsplit('.',1)[0]
#         if ns_str!=file_name+file_num:
#             error_list.append(rfnode)

#     return error_list


def check_namespace_equel_ref_file_name(fun=None):
    """检查名称空间不等于文件名
    """ 
    error_list = []

    refList = cmds.ls(references = True)
    allReferenceNodeList = list()
    objList = list()
    for ref in refList:
        try:
            if cmds.referenceQuery(ref,isLoaded = True) or not cmds.referenceQuery(ref,isLoaded = True):
                if cmds.referenceQuery( ref, filename=True, parent=True ):
                    allReferenceNodeList.append(ref)
        except:
            pass
    for rfnode in allReferenceNodeList:
        file_path=cmds.referenceQuery(rfnode,f=1)
        file_name=''
        file_num=''
        ns_str=cmds.referenceQuery(rfnode,ns=1).rsplit(':',1)[1]
        if '{' in file_path:
            file_name=file_path.rsplit('/',1)[1][:-3].rsplit('.',1)[0]
            file_num=file_path.rsplit('{',1)[1][:-1]
        else:
            file_name=file_path.rsplit('/',1)[1].rsplit('.',1)[0]
        
        if file_name.startswith('chars_') or file_name.startswith('props_'):
            file_name = file_name.split('_RIG_EX')[0] + '_RIG_EX'    
            if not ns_str.startswith(file_name):
                error_list.append(rfnode)
        else:
            if ns_str!=file_name+file_num:
                error_list.append(rfnode)
                
    return error_list


def check_file_type_and_end(type_str,endswith):
    """检查引用文件的开始结束
    """
    value=list()
    ref_paths=get_ref_ma_file_paths()
    for ref in ref_paths.keys():
        file_name=util_helper.UtilFileHelper.get_file_name_without_ext(ref)
        #如果是chars就必须是Ex结束,以prop开头必须以H结束
        if type_str not in file_name:
            continue
        if endswith in file_name:
            continue
        node=cmds.referenceQuery(ref,referenceNode=True)
        value.append(node)
    return value

def get_ref_ma_file_paths():
    """取引用文件名以及名称空间
    """    
    result={}
    refs=cmds.ls(type="reference")
    for i in refs:
        try:
            ref=cmds.referenceQuery(i,filename=True)
        except:
            continue
        if ref.endswith(".ma"):
            name=cmds.referenceQuery(ref,namespace=True).replace(":","")  #去掉名称空间中的冒号
            result[ref]=name
    return result


def check_mesh_arnold_subdivision_none(self):
    """模型没设置arnorld细分类型
    """    
    result=list()
    shapes=cmds.ls(type="mesh")
    if not shapes:
        return result
    for i in shapes:
        if cmds.objExists("{}.{}".format(i,"aiSubdivType")):
            value=cmds.getAttr("{}.{}".format(i,"aiSubdivType"))
            if value==0:
                trans = cmds.listRelatives(i ,p = 1)[0]
                if trans not in result:
                    if "NoR" not in trans and "Grow" not in trans:
                        result.append(trans)
    return result


def check_mesh_arnold_subdivision_over3(self):
    """模型的arnorld细分迭代大于3或等于1
    """    
    result=list()
    shapes=cmds.ls(type="mesh")
    if not shapes:
        return result
    for i in shapes:
        if cmds.objExists("{}.{}".format(i,"aiSubdivIterations")):
            value=cmds.getAttr("{}.{}".format(i,"aiSubdivIterations"))
            if value>3:
                result.append(i)
    return result
# 杨晓坤 20211116
def check_filenode_colorspace(self):
    '''
    检查file节点和aiImage节点的色彩空间
    '''
    
    file_node_dic = {"file":"colorSpace",
                    "aiImage":"colorSpace"}
    result = list()
    for node_type,node_attr in file_node_dic.items():
        all_node = cmds.ls(type=node_type, l=1)
        for file_node in all_node:
            arg = cmds.getAttr("{}.{}".format(file_node,node_attr))
            if not arg.startswith("ACES") and not arg.startswith("Utility") and not arg.startswith("Output"):
                result.append(file_node)
    return result


def check_ass_texpath(self):
    result = []
    getAllAss = []
    getAllNodes = cmds.ls(type='aiStandIn')
    if getAllNodes:
        # 分析ass代理文件贴图路径
        getAllAss = []
        for node in getAllNodes:
            getPath = cmds.getAttr(node + ".dso")
            if getPath and getPath not in getAllAss:
                getAllAss.append(getPath)
    
              
    # 如果有ass路径
    if getAllAss:
        for path in getAllAss:

            getAllPath = []
            ar.AiBegin()
            ar.AiMsgSetConsoleFlags(ar.AI_LOG_ALL)
            ar.AiASSLoad(path, ar.AI_NODE_ALL)
            iterator = ar.AiUniverseGetNodeIterator(ar.AI_NODE_ALL)

            while not ar.AiNodeIteratorFinished(iterator):
                node = ar.AiNodeIteratorGetNext(iterator)
                if ar.AiNodeIs(node, "MayaFile") or ar.AiNodeIs(node, "procedural") or ar.AiNodeIs(node, "image"):
                    getPath = ar.AiNodeGetStr(node, "filename")
                    if getPath and getPath not in getAllPath:
                        getAllPath.append(getPath)
            ar.AiNodeIteratorDestroy(iterator)
            ar.AiEnd()

            for filefullpath in getAllPath:
                if filefullpath.endswith(".ass"):
                    continue
                if filefullpath.endswith(".tx"):
                    continue
                if os.path.exists("{}.tx".format(filefullpath.rsplit(".",1)[0])):
                    continue
                    
                if not path in result:
                    result.append(path)
            
            
    return result


# 姜玉璐 20211215
def checkHairAttr(fun=None):
    '''
    检查毛发属性
    :return:

    '''
    values = []
    hair_list = cmds.ls(type='hairSystem')
    for hair_node in hair_list:
        attr_num = cmds.getAttr(hair_node + ".simulationMethod")
        attr_num_active = cmds.getAttr(hair_node + ".active")
        if attr_num != 1 or attr_num_active != 0:
            values.append(hair_node)
    return values
# 姜玉璐 20211222
# def check_shad_sg(fun=None):
#     '''
#     检查sg节点命名一致性
#     '''
#     values = []
#     default = [u'initialParticleSE', u'initialShadingGroup', u'surfaceShader1SG']
#     shading_sgs = cmds.ls(type='shadingEngine')
#     for sg in shading_sgs:
#         shading = cmds.connectionInfo(sg + '.aiSurfaceShader', sfd=True).split('.')[0]
#         if shading:
#             spec_sg = shading + '_SG'
#             if sg != spec_sg:
#                 if sg != unname_sg:
#                     if sg not in default:
#                         values.append(sg)
#         else:
#             shading = cmds.connectionInfo(sg + '.surfaceShader', sfd=True).split('.')[0]
#             if cmds.nodeType(shading) != 'lambert':
#                 spec_sg = shading + '_SG'
#                 if sg != spec_sg:
#                     if sg != unname_sg:
#                         if sg not in default:
#                             values.append(sg)
#    return values
#姜玉璐 20211223
def check_shad_sg(fun=None):

    return check_sg_node(2)
def check_unname_node(fun=None):
    return check_sg_node(1)
def check_sg_node(flag):
    '''
    检查未命名节点
    '''
    values = []
    default = [u'initialParticleSE', u'initialShadingGroup', u'surfaceShader1SG']
    shading_sgs = cmds.ls(type='shadingEngine')
    for sg in shading_sgs:
        shading_plug = cmds.connectionInfo(sg + '.aiSurfaceShader', sfd=True)
        if shading_plug:
            shading = shading_plug.split('.')[0]
            if shading:
                spec_sg = shading + '_SG'
                unname_sg = shading + 'SG'
                if sg != spec_sg:
                    if flag == 1:
                        if sg == unname_sg:
                            if sg not in default:
                                values.append(sg)
                    else:
                        if sg != unname_sg:
                            if sg not in default:
                                values.append(sg)
        else:
            try:
                shading = cmds.connectionInfo(sg + '.surfaceShader', sfd=True).split('.')[0]
                if shading != 'lambert1':

                    spec_sg = shading + '_SG'
                    unname_sg = shading + 'SG'
                    if sg != spec_sg:
                        if flag == 1:
                            if sg == unname_sg:
                                if sg not in default:
                                    values.append(sg)
                        else:

                            if sg != unname_sg:
                                if sg not in default:
                                    values.append(sg)

            except Exception as e:
                pass
    return values
#姜玉璐20211228
def check_mod_key(fun=None):
    values = []
    objs = []
    meshs = cmds.ls(type='mesh')
    attrs = ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz', '.visibility']
    for mesh in meshs:
        trans = cmds.listRelatives(mesh, p=True)[0]
        if trans not in objs:
            objs.append(trans)
    num = len(objs)
    for obj in objs:
        if fun:
            state = fun(obj, num)
            if not state:
                return
        for attr in attrs:
            if cmds.keyframe(obj + attr, q=True):
                values.append(obj)
                break
    return values
# 姜玉璐20220113
def check_mod_attr(fun = None):
    values = []
    shapesobjects = cmds.ls(type="mesh")
    transobjects = cmds.listRelatives(shapesobjects, p=1,f=1)
    if transobjects:
        transobjects = list(set(transobjects))
        num = len(transobjects)
        for obj in transobjects:
            if fun:
                state = fun(obj, num)
                if not state:
                    return
            try:
                objects_difft_Attr = []
                objects_list_Attr = cmds.listAttr(obj, k=True)
                for attr in objects_list_Attr:
                    if 'FBX' in attr:
                        objects_difft_Attr.append(attr)
                if objects_difft_Attr:
                    if obj not in values:
                        values.append(obj)
            except:
                pass
    return values
# 姜玉璐20220114
def check_mat_file(fun = None):
    values = []
    obj_list = cmds.ls(type=["animCurveUU", "animCurveUA", "cameraView", "condition", "plusMinusAverage","polyDelEdge","polyBridgeEdge","polyUnite","multiplyDivide","polyPlanarProj"])
    for obj in obj_list:
        if not cmds.listConnections(obj):
            values.append(obj)
    return values
# 姜玉璐20220121
def check_mesh_opaque(fun = None):
    values = []
    shapes = cmds.ls(type="mesh", l=True)
    for shape in shapes:
        if not '|Eyes_Grp|' in shape and cmds.objExists(shape + ".aiOpaque"):
            if cmds.getAttr(shape + ".aiOpaque") == 0:
                values.append(shape.split('|')[-1])            
    return values

def check_multishape(fun = None):
    values = []
    shapes = cmds.ls(type="mesh")
    polytrans = []
    for shape in shapes:
        trans = cmds.listRelatives(shape, p=1,f=1)
        if trans not in polytrans:
            polytrans.append(trans)
    for i in polytrans:
        shape_num = len(cmds.ls(i, dag=1, l=1, type=['mesh']))
        if shape_num>1:
            values.append(i)
    return values


# 杨晓坤20220208
def check_vertex_number(fun = None):
    import maya.api.OpenMaya as om_new

    error_list = []
    for shape_node in cmds.ls(type="mesh",l=1):
        meshName = cmds.listRelatives(shape_node, p=1, pa=1)[0]
        meshDag = om_new.MGlobal.getSelectionListByName(meshName).getDagPath(0)
        try:
            itVerts = om_new.MItMeshVertex(meshDag)
            mesh = om_new.MFnMesh(meshDag)
            vertex_num = mesh.numVertices
            weird_vertex_num = 0
            while not itVerts.isDone():
                if not itVerts.numConnectedEdges():
                    if not shape_node in error_list:
                        error_list.append(shape_node)
                    break
                itVerts.next()
        except:
            pass
        
    return error_list


def check_overlap_face(fun = None):
    shapes = cmds.ls(g=1, type="mesh")
    values = []
    for shape in shapes:
        mode_lst = []
        face_list = []
        # mobj = pm.PyNode(shape).__apiobject__()
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(shape)
        dag_path = OpenMaya.MDagPath()
        selectionList.getDagPath(0, dag_path)
        
        mitface = OpenMaya.MItMeshPolygon(dag_path)
        while not mitface.isDone():
            mpoint = mitface.center(OpenMaya.MSpace.kWorld)
            mode = struct.pack('dddd', round(mpoint.x, 4), round(mpoint.y, 4), round(mpoint.z, 4),
                               round(mpoint.w, 4)).encode('hex')
            if mode in mode_lst:
                face = shape + ".f[{}]".format(mitface.index())
                face_list.append(face)
            mode_lst.append(mode)
            mitface.next()
        if face_list:
            values.append([shape, face_list])
    cmds.select(shapes)
    other_list = mel.eval('polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","0","1e-05","0","1e-05","1","1e-05","0","-1","0","0" };')
    if other_list:
        for other in other_list:
            obj = other.split(".")[0]
            face_list = cmds.ls(other, fl=1)
            values.append([obj, face_list])
    return values

# 杨晓坤20220314
def check_uvshell(fun = None):
    error_list = []
    body_obj = u'Body_001_mo'
    obj_list = [u'|NoRender_Grp|body_001_NoRd', u'|NoRender_Grp|GrowMesh_Grp|GrowMesh_001_mo']
    
    for obj in obj_list:
        if cmds.objExists(obj):
            shapes = cmds.listRelatives(obj, c=1, pa=1, f=1, type="mesh")
            for shape in shapes:
                all_uv = cmds.polyEditUVShell((shape + ".map[*]"), q=1, u=1, v=1 )
                all_u = []
                all_v = []
                if all_uv:
                    for index,v in enumerate(all_uv):
                        if index%2==0:
                            all_u.append(v)
                        else:
                            all_v.append(v)
                    if sorted(all_u)[-1] > 1 or sorted(all_v)[-1] > 1:
                        error_list.append("{}--uv错误".format(shape))
                else:
                    error_list.append(u"{}--不存在uv".format(shape))
        else:
            error_list.append(u"{}--不存在".format(obj))
    if cmds.objExists(body_obj):
        shapes = cmds.listRelatives(body_obj, c=1, pa=1, f=1, type="mesh")
        for shape in shapes:
            all_uv = cmds.polyEditUVShell((shape + ".map[*]"), q=1, u=1, v=1 )
            all_u = []
            all_v = []
            if all_uv:
                for index,v in enumerate(all_uv):
                    if index%2==0:
                        all_u.append(v)
                    else:
                        all_v.append(v)
                if sorted(all_u)[-1] > 4 or sorted(all_v)[-1] > 1:
                    error_list.append("{}--uv错误".format(shape))
            else:
                error_list.append(u"{}--不存在uv".format(shape))
    else:
        error_list.append(u"{}--不存在".format(body_obj))

    return error_list

# 杨晓坤20220510
def check_facial_mesh(fun=None):
    obj_list = cmds.ls("Body_001_mo_facial")

    # 如果是模型阶段，没有链接aiSurfaceShader，跳过检查
    mod_pipeline = True
    if cmds.ls("Body_001_mo"):
        shape_nodes = cmds.listRelatives("Body_001_mo", c=1, pa=1)
        for shapenode in shape_nodes:
            sg_nodes = cmds.listConnections(shapenode, type="shadingEngine", s=0, d=1)
            if sg_nodes:
                for sgnode in sg_nodes:
                    aishader = cmds.listConnections((sgnode+".aiSurfaceShader"), s=1, d=0)
                    if aishader:
                        mod_pipeline = False

    if mod_pipeline:
        return []
    else:
        if len(obj_list) > 1:
            return [u"有多个模型   Body_001_mo_facial"]
        elif len(obj_list) < 1:
            return [u"未发现模型   Body_001_mo_facial"]
        else:
            return []

# 杨晓坤20220513
def get_shapenode_attr(shape_node,check_type):
    render_dic = {
        ".castsShadows": 1,
        ".receiveShadows": 1,
        ".holdOut": 0,
        ".motionBlur": 1,
        ".primaryVisibility": 1,
        ".smoothShading": 1,
        ".visibleInReflections": 1,
        ".visibleInRefractions": 1,
        ".doubleSided": 1,
        ".aiVisibleInDiffuseReflection": 1,
        ".aiVisibleInSpecularReflection": 1,
        ".aiVisibleInDiffuseTransmission": 1,
        ".aiVisibleInSpecularTransmission": 1,
        ".aiVisibleInVolume": 1,
        ".aiSelfShadows": 1
        }
    disrender_dic = {
        ".castsShadows": 0,
        ".receiveShadows": 0,
        ".holdOut": 0,
        ".motionBlur": 0,
        ".primaryVisibility": 0,
        ".smoothShading": 0,
        ".visibleInReflections": 0,
        ".visibleInRefractions": 0,
        ".doubleSided": 0,
        ".aiVisibleInDiffuseReflection": 0,
        ".aiVisibleInSpecularReflection": 0,
        ".aiVisibleInDiffuseTransmission": 0,
        ".aiVisibleInSpecularTransmission": 0,
        ".aiVisibleInVolume": 0,
        ".aiSelfShadows": 0
        }
    eyeshadow_dic = {
        ".castsShadows": 1,
        ".receiveShadows": 1,
        ".holdOut": 0,
        ".motionBlur": 1,
        ".primaryVisibility": 0,
        ".smoothShading": 0,
        ".visibleInReflections": 0,
        ".visibleInRefractions": 0,
        ".doubleSided": 1,
        ".aiTranslator": "polymesh",
        ".aiVisibleInDiffuseReflection": 0,
        ".aiVisibleInSpecularReflection": 0,
        ".aiVisibleInDiffuseTransmission": 0,
        ".aiVisibleInSpecularTransmission": 0,
        ".aiVisibleInVolume": 0,
        ".aiSelfShadows": 1,
        ".aiOpaque": 0
        }    
    if check_type == "render":
        for key,val in render_dic.items():
            if cmds.getAttr(shape_node + key) != val:
                return False
    elif check_type == "disrender":
        for key,val in disrender_dic.items():
            if cmds.getAttr(shape_node + key) != val:
                return False
    elif check_type == "eyeshadow":
        for key,val in eyeshadow_dic.items():
            if cmds.getAttr(shape_node + key) != val:
                return False            
    return True
# 获取某个组下的某个类型的所有节点
def get_child_mod(obj,objtype):
    ret_list = []
    if cmds.listRelatives(obj, c=1, pa=1):
        for child in cmds.listRelatives(obj, c=1, pa=1):
            if cmds.objectType(child) == objtype:
                ret_list += [child]
        if cmds.listRelatives(obj, c=1, pa=1):
            for child in cmds.listRelatives(obj, c=1, pa=1):
                ret_list += get_child_mod(child,objtype)
        
    return list(set(ret_list))
# 检查渲染模型属性
def check_render_stats(fun=None):
    error_list = []
    for obj in cmds.ls("Geometry", r=1):
        for shape_node in get_child_mod(obj,"mesh"):
            if "Eyes_Grp" in shape_node or "_facial" in shape_node:
                continue
            # 检查 or "EyeShadow" in shape_node
            if "EyeShadow" in shape_node:
                if not get_shapenode_attr(shape_node,"eyeshadow"):
                    error_list.append(shape_node)
            else:
                if not get_shapenode_attr(shape_node,"render"):
                    error_list.append(shape_node)
    return error_list

# 杨晓坤20220517
# 检查不渲染模型属性
def check_norender_stats(fun=None):
    error_list = []
    for obj in cmds.ls("NoRender_Grp", r=1):
        for shape_node in get_child_mod(obj,"mesh"):
            if not get_shapenode_attr(shape_node,"disrender"):
                error_list.append(shape_node)
    return error_list
    
# 罗庸 20230209    
def getCheckShapeName(fun=None):
    '''
    检查Shape命名
    Shape名字按照Transform名字+Shape+数字ID的形式
    :return: bool
    '''
    value = []
    mesh_list = cmds.ls(['Geometry', 'NoRender_Grp'], type='mesh', dag=True, l=True)
    for mesh in mesh_list:
        mesh_name = mesh.split('|')[-1]
        
        tran = cmds.listRelatives(mesh, p=True, pa=True, type='transform')[0]
        tran_name = tran.split('|')[-1]
        
        if not mesh_name.startswith('{}Shape'.format(tran_name)):
            if not tran in value:
                value.append(tran)

    return value       


# 罗庸 20230512 
def getCheckHasWeaponGrp(fun=None):
    value = []
    trans_list = cmds.ls('Geometry', type='transform', dag=True, l=True)
    for trans in trans_list:
        if cmds.nodeType(trans) != 'transform':
            continue
            
        trans_name = trans.split('|')[-1]
        if trans_name == 'Weapon_Grp':
            value.append(trans)

    return value      

# 罗庸 20230515
def getCheckTransformLock(fun=None):
    value = []
    mesh_list = cmds.ls(['Geometry', 'NoRender_Grp'], type='mesh', dag=True, l=True, ni=True)
    for mesh in mesh_list:
        is_lock = False
        trans = cmds.listRelatives(mesh, p=True, type='transform')[0]
        for attr in 'trs':
            for axis in 'xyz':
                if cmds.getAttr('{}.{}{}'.format(trans, attr, axis), l=True):
                    is_lock = True
                
        if is_lock and not trans in value:
            value.append(trans)    
            
    return value

# 罗庸 20230807
def getCheckTransformUnfreeze(fun=None):
    value = []
    mesh_list = cmds.ls(['Geometry', 'NoRender_Grp'], type='mesh', dag=True, l=True, ni=True)
    if cmds.objExists('Geometry') and not 'Geometry' in mesh_list:
        mesh_list.append('Geometry')
    if cmds.objExists('NoRender_Grp') and not 'NoRender_Grp' in mesh_list:
        mesh_list.append('NoRender_Grp')    
    for mesh in mesh_list:
        is_unfreeze = False
        trans = cmds.listRelatives(mesh, p=True, type='transform')[0] if cmds.nodeType(mesh) == 'mesh' else mesh
        for attr in 'trs':
            for axis in 'xyz':
                val = cmds.getAttr('{}.{}{}'.format(trans, attr, axis))
                if attr != 's':
                    if abs(val - 0.0) > 0.000001:
                        is_unfreeze = True
                else:
                    if abs(val - 1.0) > 0.000001:
                        is_unfreeze = True
                
        if is_unfreeze and not trans in value:
            value.append(trans)    
            
    return value 
    

# 罗庸 20230620
def getCheckMeshLaminaFace(fun=None):
    value = []
    # mesh_list = cmds.ls(['Geometry', 'NoRender_Grp'], type='mesh', dag=True, l=True, ni=True)
    mesh_list = cmds.ls(type='mesh', dag=True, l=True, ni=True)

    for mesh in mesh_list:
        components = cmds.polyInfo(mesh, nmv=True, nme=True, lf=True)
        if components:
            for component in components:
                value.append(component)   
                
    return value     

  