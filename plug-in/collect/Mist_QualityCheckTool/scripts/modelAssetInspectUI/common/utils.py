# -*- coding: utf-8 -*-
import collections

CHECK_DICT = collections.OrderedDict()
CHECK_DICT["Scene"] = [u"未知节点", u"检查重名", u"检查空组", u"NameSpace名称空间", u"动画层", u"显示层", u'表达式', u"是否有按3显示的情况",
                       u"是否有历史记录", u"是否有按面给材质",u"检查SG节点命名是否一致",u"是否有曲线有k帧",u"是否有模型有k帧",
                       u"变态属性",u"Opaque 没有开启",u"是否有五边面",u"多余废点"]
CHECK_DICT["Transform"] = [u"以下模型有变换数据", u"轴心点没有在世界坐标中心的物体", u"是否有曲线有k帧",
                           u"检查transform下面是否有多个shape", u"是否有隐藏的transform",u"是否有模型有k帧",u"检查材质文件多余绑定节点"]

CHECK_DICT["Rendering"] = [u"是否有渲染层", u"是否有多余的材质", u"是否有灯光", u'LightEditor是否有错误的显示项',
                           u"是否有无效aov", u"是否有多余的相机", u"是否含有renderSetup信息", u"是否渲染设置回调函数",
                           u"没有设置arnorld细分的模型",u"模型的arnorld细分迭代大于3",u"贴图色彩空间",u"Ass代理贴图路径",
                           u"检查SG节点命名是否一致",u"Opaque 没有开启",u"是否有五边面"]
CHECK_DICT["Mesh"] = [u"是否顶点颜色显示", u"是否有隐藏的shape(shape.v)",u"多shape结构", u"以下模型设置有细分并会影响渲染",
                      u"是否存在关联复制", u"Body拓扑检查", u"是否0点0线0面",#u"是否有facial模型",
                      u"渲染模型参数异常",u"非渲染模型参数异常",
                      u"检查polygon重命名", u"检查所有DAG_Object重命名", u"两个及以上uvSet", 
                      u"以下模型设置有细分并会影响渲染",u"是否有锁定法线的模型",u"nhairSystem设置检查",u"检查SG节点命名是否一致",
                      u"是否有曲线有k帧",u"是否有模型有k帧",u"检查材质文件多余绑定节点",u"Opaque 没有开启",u"变态属性",u"是否有五边面",
                      u"模型点是否有位移数据", u"shape信息", u"是否存在shape命名错误", u"多余废点",u"权重模型", u"检查空组", u"位移锁定",
                      u"位移未冻结", u"检查重面"]
CHECK_DICT["Animation"] = [u"文件名不包含shot",u"是否包含CAM组", u"镜头名规范检查",u"动画层", u"显示层", u"是否有按3显示的情况",
                        u"chars文件检查EX档", u"props文件检查EX档", u"空间命名是否跟引用文件一致",u"是否有模型有k帧"]

CHECK_DICT["Rigging"] = [u"武器组"]

CHECK_DICT_ZH=collections.OrderedDict()
CHECK_DICT_ZH["Scene"]=u"场景检查"
CHECK_DICT_ZH["Transform"]=u"位移检查"
CHECK_DICT_ZH["Rendering"]=u"渲染检查"
CHECK_DICT_ZH["Mesh"]=u"模型检查"
CHECK_DICT_ZH["Animation"]=u"动画检查"
CHECK_DICT_ZH["Rigging"]=u"绑定检查"

#有数据但是显示绿色的,这个是质检的要求，有些数据没问题，要方便查看，所以不能是红色，得是绿色
CHECK_DICT_HAS_DATA_GREEN=[u"shape信息"]
CHECK_DICT_HAS_DATA_YELLOW = [u"变态属性",u"是否有隐藏的shape(shape.v)",u"多shape结构", u"是否存在shape命名错误", u"渲染模型参数异常"]
CHECK_DICT_HAS_DATA_BLUE = [u"模型的arnorld细分迭代大于3",u"检查材质文件多余绑定节点",u"Opaque 没有开启",u"以下模型设置不影响渲染",u"武器组"]

CAMERA_NAME_LIST = ['persp', 'top', 'front', 'side']
CAMERA_SHAPE_NAME_LIST = ['perspShape', 'topShape', 'frontShape', 'sideShape']
GEOMETRY = "Geometry"

TRANSFORM_ATTR_DICT = {".tx": 0, ".ty": 0, ".tz": 0,
                       ".rx": 0, ".ry": 0, ".rz": 0,
                       ".sx": 1, ".sy": 1, ".sz": 1}

DEFAULT_RENDER_LAYER = "defaultRenderLayer"
DEFAULT_LAYER = "defaultLayer"

SHAPE_DEFAULT_RENDER_STATS = {".castsShadows": True, ".receiveShadows": True, ".holdOut": False, ".motionBlur": True,
                              ".primaryVisibility": True, ".smoothShading": True, ".visibleInReflections": True,
                              ".visibleInRefractions": True, ".doubleSided": True,
                              "geometryAntialiasingOverride": False, ".shadingSamplesOverride": False,
                              ".aiVisibleInDiffuseReflection":True,".aiVisibleInSpecularReflection":True,
                              "aiVisibleInDiffuseTransmission":True,".aiVisibleInSpecularTransmission":True,
                              ".aiVisibleInVolume":True,".aiSelfShadows":True,
                              ".aiVisibleInDiffuseTransmission":True
                              }

DEFAULT_SET = ["defaultLightSet", "defaultObjectSet",
               "initialParticleSE", "initialShadingGroup"]

RENDERING_ATTR_LIST = ["preMel", "postMel", "preRenderLayerMel", "postRenderLayerMel", "preRenderMel", "postRenderMel",
                       'preFurRenderMel', 'postFurRenderMel']

NORENDER_GRP_ATTRS = ["castsShadows",
                      "receiveShadows",
                      "holdOut",
                      "motionBlur",
                      "primaryVisibility",
                      "smoothShading",
                      "geometryAntialiasingOverride",
                      "visibleInReflections",
                      "visibleInRefractions",
                      "doubleSided",
                      "aiVisibleInDiffuseReflection",
                      "aiVisibleInSpecularReflection",
                      "aiVisibleInDiffuseTransmission",
                      "aiVisibleInSpecularTransmission",
                      "aiVisibleInVolume",
                      "aiSelfShadows",
                      "aiSubdivType",
                      "aiSubdivIterations"]

#模型检查的时候，有一些组名，和包含了一些字的要跳过，记住用长名称查
CHECK_MESH_SKIP_SOME_NAME=["Main_Grp","face_ctrl_grp","bs_","_bs"]