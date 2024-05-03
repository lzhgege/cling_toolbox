# -*- coding: utf-8 -*-
import modelAssetInspectUI.model.checkBase as checkBase
import modelAssetInspectUI.model.handleBase as handleBase
import sys
if sys.version_info[0] == 2:
    reload(checkBase)
    reload(handleBase)
elif sys.version_info[0] > 2:
    import importlib
    importlib.reload(checkBase) 
    importlib.reload(handleBase) 
# reload(checkBase)
# reload(handleBase)

NOT_DATA_WIDGET = [u"检查重名"]

CHECK_FUN_DICT = {u"未知节点": [u"删除未知节点", checkBase.getCheckUnknownNode, handleBase.handleUnknownNode, 'list'],
                  u"检查空组":[u"检查空组", checkBase.getCheckEmptyGrp, None, 'list'],
                  u"检查重名":[u"检查重名", checkBase.getCheckRename, handleBase.handleRename, 'list'],
                  u"NameSpace名称空间":[u"一键删除", checkBase.getCheckSpaceName, handleBase.handleSpaceName, 'list'],
                  u"动画层":[u'删除动画层', checkBase.getCheckAnimationLayer, handleBase.handleAnimationLayer, 'list'],
                  u"显示层":[u'删除显示层', checkBase.getCheckDisplayLayer, handleBase.handleDisplayLayer, 'list'],
                  u'表达式':[u'删除表达式', checkBase.getCheckExpression, handleBase.handleExpression, 'list'],
                  # u"Geometry组": checkBase.getCheckFileRoot,
                  u"以下模型有变换数据":
                      [u"以下模型有变换数据", checkBase.getCheckFreezeTransformation, handleBase.handleFreezeTransformation, 'list'],
                  u"轴心点没有在世界坐标中心的物体":
                      [u'设置到世界中心', checkBase.getCheckReseTransformation, handleBase.handleReseTransformation, 'list'],
                  u"是否有曲线有k帧": [u'删除k帧', checkBase.getCheckKFramTransforms, handleBase.handleKFramTransforms, 'list'],
                  u"检查transform下面是否有多个shape":
                      [u'intermediate切换', checkBase.getCheckTransformShapes, handleBase.handleTransformShapes, 'tree'],
                  u"是否有隐藏的transform": [u'改为显示', checkBase.getCheckHideTransforms, handleBase.handleHideTransforms, 'list'],
                  u"是否有渲染层": [u'删除渲染层', checkBase.getCheckRenderLayer, handleBase.handleRenderLayer, 'list'],
                  u"是否渲染设置回调函数": [u'删除函数', checkBase.getCheckRenderCallbacks, handleBase.handleRenderCallbacks, 'list'],
                  u"没有设置arnorld细分的模型":[None, checkBase.check_mesh_arnold_subdivision_none, None, 'list'],
                  u"模型的arnorld细分迭代大于3":[None, checkBase.check_mesh_arnold_subdivision_over3, None, 'list'],
                  u"是否有多余的材质": [u"材质编辑", checkBase.getCheckUnusedML, handleBase.handleUnusedML, 'list'],
                  u"是否有灯光": [u"删除灯光", checkBase.getCheckLights, handleBase.handleLights, 'list'],
                  u'LightEditor是否有错误的显示项':
                      [u"修复错误的显示项", checkBase.getCheckLightEditor, handleBase.handleLightEditor, 'list'],
                  u"是否有无效aov": [u'删除AOV', checkBase.getCheckAovs, handleBase.handleAovs, 'list'],
                  u"是否有多余的相机": [u"删除or参数正常化", checkBase.getCheckCameras, handleBase.handleCameras, 'list'],
                  u"是否含有renderSetup信息": 
                      [u'删除renderSetup信息', checkBase.getCheckRenderSetup, handleBase.handleRenderSetup, 'list'],
                  u"是否有按面给材质": [None, checkBase.getCheckAssignFaceShader, None, 'list'],
                  u"是否顶点颜色显示": [u'取消顶点颜色显示', checkBase.getCheckShowColorMesh, handleBase.handleShowColorMesh, 'list'],
                  u"是否有历史记录": [u"删除历史", checkBase.getCheckHistoryMesh, handleBase.handleHistoryMesh, 'list'],
                  u"是否有按3显示的情况":
                      [u'按0显示', checkBase.getCheckDisplaySmoothMesh, handleBase.handleDisplaySmoothMesh, 'list'],
                  u"是否有隐藏的shape(shape.v)": [u'显示shape节点', checkBase.getCheckHeidMesh, handleBase.handleHeidMesh, 'list'],
                  u"以下模型设置不影响渲染":
                      [u"恢复默认状态", checkBase.getCheckRenderStatsMesh, handleBase.handleRenderStatsMesh, 'list'],
                  u"是否有锁定法线的模型":[u"修复", checkBase.check_mesh_has_locked_normals, handleBase.handle_check_mesh_has_locked_normals, 'list'],
                  u"是否存在关联复制": [u"修复", checkBase.getCheckInstanceCopyMesh, handleBase.convertInstanceMeshToNormalObject, 'list'],
                  u"是否有五边面": [None, checkBase.getCheckMeshFiveSides,None, 'tree'],
                  u"是否0点0线0面": [None, checkBase.getCheckZeroVEF, None, 'list'],
                  u"检查是否有物体重名": [None, checkBase.getCheckMeshWithSameName, None, 'list'],
                  u"检查polygon重命名": [None, checkBase.checkAllPolygonSameName, None, 'list'],
                  u"检查所有DAG_Object重命名": [None, checkBase.checkAllSameName, None, 'list'],
                  u"两个及以上uvSet": [None, checkBase.checkMoreThanOneUvSet, None, 'list'],
                  u"以下模型设置有细分并会影响渲染": [u"设置", checkBase.getNoRenderGrpSettting, handleBase.handleNoRenderGrpSetting, 'list'],
                  u"模型点是否有位移数据": [u'数据清零', checkBase.getCheckMeshObjectPnts, handleBase.handleMeshObjectPnts, 'list'],
                  u"shape信息": [u"大表显示", checkBase.getCheckMeshInfo, handleBase.handleMeshInfo, 'table'],
                  u"Body拓扑检查": [u"解决方案视频", checkBase.getCheckBodyTopo, handleBase.handle_check_body_topo, 'list'],
                  u"文件名不包含shot":[None, checkBase.check_file_name_is_shot, None, 'list'],
                  u"是否包含CAM组":[u"改组名(先选组)", checkBase.check_contains_group_cam, handleBase.handle_check_contains_group_cam, 'list'],
                  u"镜头名规范检查":[u"改镜头名", checkBase.check_shot_satandard, handleBase.handleCheckShotStandard, 'list'],
                  u"chars文件检查EX档":[None, checkBase.check_is_chars_ex, None, 'list'],
                  u"props文件检查EX档":[None, checkBase.check_is_prop_h, None, 'list'],
                  u"空间命名是否跟引用文件一致":[u"修复", checkBase.check_namespace_equel_ref_file_name, handleBase.handle_update_ref_namespace, 'list'],
                  u"贴图色彩空间":[None, checkBase.check_filenode_colorspace, None, 'list'],
                  u"Ass代理贴图路径":[u"详细检查", checkBase.check_ass_texpath, handleBase.read_pic_in_aistandin, 'list'],
                  u"nhairSystem设置检查":[u'错误修复', checkBase.checkHairAttr, handleBase.set_hairshape_attr, 'list'],
                  u"检查SG节点命名是否一致":[u'修复', checkBase.check_shad_sg, handleBase.set_shad_sg , 'list'],
                  u"存在未命名SG节点":[None, checkBase.check_unname_node,None , 'list'],
                  u"是否有模型有k帧":[None, checkBase.check_mod_key,None , 'list'],
                  u"变态属性":[u"修复",checkBase.check_mod_attr,handleBase.delete_redundant_attr,'list'],
                  u"检查材质文件多余绑定节点":[None,checkBase.check_mat_file, None,'list'],
                  u"Opaque 没有开启":[None,checkBase.check_mesh_opaque, None,'list'],
                  u"多shape结构":[u"修复",checkBase.check_multishape, handleBase.repair_multishape,'list'],
                  u"多余废点":[u"修复", checkBase.check_vertex_number, handleBase.rep_vertex_number, 'list'],
                  u"重合面":[None, checkBase.check_overlap_face,None, 'tree'],
                  u"权重模型":[None, checkBase.check_uvshell,None, 'list'],
                  # u"是否有facial模型":[u"创建facial模型", checkBase.check_facial_mesh, handleBase.repair_facial_mesh, 'list'],
                  u"渲染模型参数异常":[u"修复", checkBase.check_render_stats, handleBase.repair_render_stats, 'list'],
                  u"非渲染模型参数异常":[u"修复", checkBase.check_norender_stats, handleBase.repair_disrender_stats, 'list'],
                  u"是否存在shape命名错误":[u"修复",checkBase.getCheckShapeName, handleBase.repair_shapeNameError,'list'],
                  u"武器组":[None,checkBase.getCheckHasWeaponGrp, None,'list'],
                  u"位移锁定":[u"修复",checkBase.getCheckTransformLock, handleBase.repair_TransformLock,'list'],
                  u"位移未冻结":[None,checkBase.getCheckTransformUnfreeze, None,'list'],
                  u"检查重面":[None,checkBase.getCheckMeshLaminaFace, None,'list']
                  }
