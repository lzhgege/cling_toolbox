# -*- coding: utf-8 -*-
# cling 2023/12/11改
import maya.cmds as mc
import maya.mel as mel


def CreateDynamicRope():
    global InitialCurv, NewCurvesDynamicNode, DynamicNucleusNode, DynamicCurv, DynamicCurvPivotN, DynamicCurvControl_N, DynamicCurvPivotV, DynamicCurvControl_V, the_cir, the_nub, the_poly, the_nurbsTesse, HairSystemNode, NewCurvesDynamicNode, nRigidNode, NewCurvesDynamicNode, Dynamic_Group
    CurveRadius = mc.floatSliderGrp('New_CurveRadius_Valu', q=True, v=True)
    CurveUnumber = mc.intSliderGrp('New_CurveUnumber_Value', q=True, v=True)
    CurveVnumber = mc.intSliderGrp('New_CurveVnumber_Value', q=True, v=True)
    SolverDisplay = 0
    InitialOutliner = mc.ls(dagObjects=1)
    ModCurv = mc.ls(sl=True)
    InitialCurv = ModCurv[-1]
    mc.select(InitialCurv, r=True)
    NewCurv = mc.duplicate(rr=True)[0]
    mc.setAttr(InitialCurv + '.visibility', 0)
    LowOutliner = mc.ls(dagObjects=1)
    if mc.nodeType(mc.listRelatives(NewCurv, s=True)) == 'bezierCurve':
        mc.bezierCurveToNurbs()
    mc.rebuildCurve(NewCurv, ch=True, rpo=True, rt=False, end=True, kr=False, kcp=False, kep=True, kt=False, s=200, d=3,
                    tol=0.01)
    mc.select(NewCurv, r=True)
    mel.eval('makeCurvesDynamic  2 { "1", "1", "0", "1", "0"};')
    NewOutliner = mc.ls(dagObjects=1)
    CurvesDynamicNode = set(NewOutliner).difference(set(LowOutliner))
    NewCurvesDynamicNode = list(CurvesDynamicNode)
    DynamicNucleusNode = mc.ls(NewCurvesDynamicNode, type='nucleus')[0]
    NewDynamicNucleusSubsteps = mc.intSliderGrp('New_DynamicNucleusSubsteps_Value', q=True, v=True)
    mc.setAttr(DynamicNucleusNode + '.subSteps', NewDynamicNucleusSubsteps)
    NewDynamicNucleusMaxCollision = mc.intSliderGrp('New_DynamicNucleusMaxCollision_Value', q=True, v=True)
    mc.setAttr(DynamicNucleusNode + '.maxCollisionIterations', NewDynamicNucleusMaxCollision)
    DynamicCurv = mc.ls(NewCurvesDynamicNode, type='nurbsCurve')[0]
    DynamicCurvPivotN = mc.xform(DynamicCurv + '.cv[0]', q=True, t=True, ws=True)
    DynamicCurvControl_N = mc.polySphere(r=CurveRadius * 1.5, sx=20, sy=20, ax=(0, 1, 0), cuv=2, ch=1)[0]
    mc.move(DynamicCurvPivotN[0], DynamicCurvPivotN[1], DynamicCurvPivotN[2], rpr=True)
    mc.select(DynamicCurv + '.cv[0]', r=True)
    mc.select(DynamicCurvControl_N, add=True)
    mel.eval('createNConstraint transform 0;')
    mc.setAttr(DynamicCurvControl_N + '.rx', lock=True)
    mc.setAttr(DynamicCurvControl_N + '.ry', lock=True)
    mc.setAttr(DynamicCurvControl_N + '.rz', lock=True)
    DynamicCurvPivotV = mc.xform(DynamicCurv + '.cv[202]', q=True, t=True, ws=True)
    DynamicCurvControl_V = mc.polySphere(r=CurveRadius * 1.5, sx=20, sy=20, ax=(0, 1, 0), cuv=2, ch=1)[0]
    mc.move(DynamicCurvPivotV[0], DynamicCurvPivotV[1], DynamicCurvPivotV[2], rpr=True)
    mc.select(DynamicCurv + '.cv[202]', r=True)
    mc.select(DynamicCurvControl_V, add=True)
    mel.eval('createNConstraint transform 0;')
    mc.setAttr(DynamicCurvControl_V + '.rx', lock=True)
    mc.setAttr(DynamicCurvControl_V + '.ry', lock=True)
    mc.setAttr(DynamicCurvControl_V + '.rz', lock=True)
    mc.select(DynamicCurv, r=True)
    the_cir = mc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=CurveRadius, d=3, ut=0, tol=0.01, s=8, ch=1,
                        n=DynamicCurv + '_circle')[0]
    mc.select(DynamicCurv, add=True)
    the_nub = \
    mc.extrude(the_cir, DynamicCurv, ch=True, rn=False, po=0, et=2, ucp=1, fpt=1, upn=1, rotation=0, scale=1, rsp=1,
               n=DynamicCurv + '_nub')[0]
    mc.setAttr(the_cir + '.visibility', 0)
    mc.setAttr(the_nub + '.visibility', 0)
    the_poly = \
    mc.nurbsToPoly(the_nub, mnd=1, n=DynamicCurv + '_poly', ch=1, f=2, pt=1, pc=200, chr=0.9, ft=0.01, mel=0.001, d=0.1,
                   ut=1, un=CurveUnumber, vt=1, vn=CurveVnumber, uch=0, ucr=0, cht=0.2, es=0, ntr=0, mrt=0, uss=1)[0]
    the_nurbsTesse = mc.listConnections(the_poly + 'Shape', t='nurbsTessellate')[0]
    HairSystemNode = mc.ls(NewCurvesDynamicNode, type='hairSystem')[0]
    mc.setAttr(HairSystemNode + '.clumpWidthScale[1].clumpWidthScale_Position', 1)
    mc.setAttr(HairSystemNode + '.clumpWidthScale[1].clumpWidthScale_FloatValue', 1)
    mc.setAttr(HairSystemNode + '.hairWidthScale[1].hairWidthScale_Position', 1)
    mc.setAttr(HairSystemNode + '.hairWidthScale[1].hairWidthScale_FloatValue', 1)
    mc.setAttr(HairSystemNode + '.selfCollide', 1)
    mc.setAttr(HairSystemNode + '.selfCollideWidthScale', CurveRadius * 200)
    mc.setAttr(HairSystemNode + '.solverDisplay', SolverDisplay)
    mc.setAttr(HairSystemNode + '.drag', 0.5)
    mc.setAttr(HairSystemNode + '.tangentialDrag', 0.5)
    FollicleNode = mc.ls(NewCurvesDynamicNode, type='follicle')[0]
    mc.setAttr(FollicleNode + '.pointLock', 0)
    mc.select(ModCurv[:-1], r=True)
    mc.nClothMakeCollide()
    NewOutliner = mc.ls(dagObjects=1)
    CurvesDynamicNode = set(NewOutliner).difference(set(LowOutliner))
    NewCurvesDynamicNode = list(CurvesDynamicNode)
    nRigidNode = mc.ls(NewCurvesDynamicNode, type='nRigid')
    for eachnRigNode in nRigidNode:
        mc.setAttr(eachnRigNode + '.thickness', CurveRadius)

    NewOutliner = mc.ls(assemblies=1)
    CurvesDynamicNode = set(NewOutliner).difference(set(InitialOutliner))
    NewCurvesDynamicNode = list(CurvesDynamicNode)
    for eachNode in NewCurvesDynamicNode:
        mc.setAttr(eachNode + '.visibility', 0)

    mc.setAttr(DynamicCurvControl_N + '.visibility', 1)
    mc.setAttr(DynamicCurvControl_V + '.visibility', 1)
    mc.setAttr(the_poly + '.visibility', 1)
    mc.select(NewCurvesDynamicNode, r=True)
    Dynamic_Group = mc.group(n=InitialCurv + 'Dynamic_G')


def RestoreInitial():
    mc.play(st=False)
    mel.eval('playButtonStart;')
    mc.select(DynamicCurvControl_N, r=True)
    mc.move(DynamicCurvPivotN[0], DynamicCurvPivotN[1], DynamicCurvPivotN[2], rpr=True)
    mc.select(DynamicCurvControl_V, r=True)
    mc.move(DynamicCurvPivotV[0], DynamicCurvPivotV[1], DynamicCurvPivotV[2], rpr=True)


def DeleteDynamic():
    mc.play(st=False)
    mel.eval('playButtonStart;')
    mc.select(Dynamic_Group, r=True)
    mc.delete()
    mc.setAttr(InitialCurv + '.visibility', 1)


def CurveRadius():
    if mc.objExists('*Dynamic_G'):
        NewCurveRadius = mc.floatSliderGrp('New_CurveRadius_Valu', q=True, v=True)
        mc.setAttr(the_cir + '.sx', NewCurveRadius)
        mc.setAttr(the_cir + '.sy', NewCurveRadius)
        mc.setAttr(the_cir + '.sz', NewCurveRadius)
        if mc.objExists(HairSystemNode):
            mc.setAttr(HairSystemNode + '.selfCollideWidthScale', NewCurveRadius * 200)
        if mc.objExists(DynamicCurvControl_N):
            mc.setAttr(DynamicCurvControl_N + '.scaleX', NewCurveRadius)
            mc.setAttr(DynamicCurvControl_N + '.scaleY', NewCurveRadius)
            mc.setAttr(DynamicCurvControl_N + '.scaleZ', NewCurveRadius)
            mc.setAttr(DynamicCurvControl_V + '.scaleX', NewCurveRadius)
            mc.setAttr(DynamicCurvControl_V + '.scaleY', NewCurveRadius)
            mc.setAttr(DynamicCurvControl_V + '.scaleZ', NewCurveRadius)
        if mc.objExists(nRigidNode[0]):
            for eachnRigNode in nRigidNode:
                mc.setAttr(eachnRigNode + '.thickness', NewCurveRadius)


def CurveUnumber():
    if mc.objExists('*Dynamic_G'):
        NewCurveUnumber = mc.intSliderGrp('New_CurveUnumber_Value', q=True, v=True)
        mc.setAttr(the_nurbsTesse + '.uNumber', NewCurveUnumber)


def CurveVnumber():
    if mc.objExists('*Dynamic_G'):
        NewCurveVnumber = mc.intSliderGrp('New_CurveVnumber_Value', q=True, v=True)
        mc.setAttr(the_nurbsTesse + '.vNumber', NewCurveVnumber)


def DynamicNucleusSubsteps():
    if mc.objExists('*Dynamic_G') and mc.objExists(DynamicNucleusNode):
        NewDynamicNucleusSubsteps = mc.intSliderGrp('New_DynamicNucleusSubsteps_Value', q=True, v=True)
        mc.setAttr(DynamicNucleusNode + '.subSteps', NewDynamicNucleusSubsteps)


def DynamicNucleusMaxCollision():
    if mc.objExists('*Dynamic_G') and mc.objExists(DynamicNucleusNode):
        NewDynamicNucleusMaxCollision = mc.intSliderGrp('New_DynamicNucleusMaxCollision_Value', q=True, v=True)
        mc.setAttr(DynamicNucleusNode + '.subSteps', NewDynamicNucleusMaxCollision)


def HairSystemSelfFriction():
    if mc.objExists('*Dynamic_G') and mc.objExists(HairSystemNode):
        NewHairSystemSelfFriction = mc.floatSliderGrp('New_HairSystemSelfFriction_Value', q=True, v=True)
        mc.setAttr(HairSystemNode + '.friction', NewHairSystemSelfFriction)


def HairSystemStretch():
    if mc.objExists('*Dynamic_G') and mc.objExists(HairSystemNode):
        NewHairSystemStretch = mc.floatSliderGrp('New_HairSystemStretch_Value', q=True, v=True)
        mc.setAttr(HairSystemNode + '.stretchResistance', NewHairSystemStretch)


def BingoRope():
    mc.play(st=False)
    mc.select(DynamicCurv, r=True)
    mc.select(the_cir, add=True)
    mc.select(the_nub, add=True)
    mc.select(the_poly, add=True)
    DynamicRope_Group = mc.group(n=InitialCurv + '_Rope')
    mc.Ungroup()
    mc.select(NewCurvesDynamicNode, r=True)
    mc.select(DynamicCurv, d=True)
    mc.select(the_cir, d=True)
    mc.select(the_nub, d=True)
    mc.select(the_poly, d=True)
    mc.select(InitialCurv, add=True)
    mc.delete()
    mc.select(the_cir, r=True)
    mc.rename(InitialCurv + '_circle')
    mc.select(the_nub, r=True)
    mc.rename(InitialCurv + '_nub')
    mc.select(the_poly, r=True)
    mc.rename(InitialCurv + '_Poly')
    mc.select(DynamicCurv, r=True)
    mc.PickWalkUp()
    mc.rename(InitialCurv + '_Curve')
    mc.select(Dynamic_Group, r=True)
    mc.rename(InitialCurv + '_Rope')
    mel.eval('playButtonStart;')


def MayaDynamicRope_ChineseHelp():
    if mc.window('MayaDynamicRope_ChineseHelp_Tool', exists=True):
        mc.deleteUI('MayaDynamicRope_ChineseHelp_Tool')
    MayaDynamicRope_ChineseHelp_Tool_UI_Wind = mc.window('MayaDynamicRope_ChineseHelp_Tool',
                                                         title='MayaDynamicRope_ChineseHelp_Tool')
    mc.columnLayout(adjustableColumn=True, bgc=(0.13, 0.13, 0.13), w=500, h=310, cal='left', cat=('left', 10))
    HelpH = 20
    mc.text(label='', h=15)
    mc.text(label=u'Radius:     绳子的半径', h=HelpH)
    mc.text(label=u'U_Number:   绳子模型U向分段数', h=HelpH)
    mc.text(label=u'V_Number:   绳子模型V向分段数', h=HelpH)
    mc.text(label='', h=15)
    mc.text(label=u'SubSteps:   解算子步（解算精度，越大解算精度越高，但是会越卡，建议不要超过10）', h=HelpH)
    mc.text(label=u'Collision:  最大碰撞迭代次数 （解算精度，越大解算精度越高，但是会越卡，建议不要超过10）', h=HelpH)
    mc.text(label='', h=15)
    mc.text(label=u'Friction:   摩擦力', h=HelpH)
    mc.text(label=u'Stretch:    拉伸强度', h=HelpH)
    mc.text(label='', h=15)
    mc.text(label=u'Create Dynamic Rope:   创建动态绳子', h=HelpH)
    mc.text(label=u'Initial Dynamic:       恢复初始动态', h=HelpH)
    mc.text(label=u'Delete  Dynamic:       删除动态绳子', h=HelpH)
    mc.text(label=u'Finish:       效果满意，生成最终模型', h=HelpH)
    mc.text(label=u'有任何问题联系作者QQ：2384230095 谢谢！', h=HelpH)
    mc.text(label=u'cling 修改版！！', h=HelpH)
    mc.text(label='', h=15)
    mc.showWindow(MayaDynamicRope_ChineseHelp_Tool_UI_Wind)


def MayaDynamicRope_Tool():
    if mc.window('MayaDynamicRope_Tool', exists=True):
        mc.deleteUI('MayaDynamicRope_Tool')
    MayaDynamicRope_Tool_UI_Wind = mc.window('MayaDynamicRope_Tool', title='MayaDynamicRope_Tool 1.0', menuBar=True,
                                             bgc=(0.1, 0.1, 0.1))
    mc.columnLayout(adjustableColumn=True, bgc=(0.13, 0.13, 0.13), w=300, h=365)
    mc.menu(label='Help ', helpMenu=True)
    mc.menuItem(label=u'中文帮助', command='MayaDynamicRope_ChineseHelp()')
    mc.menuItem(divider=True)
    mc.menuItem(label='My Animation', command='mc.launch(web="https://www.artstation.com/artist/mlsr")')
    mc.separator(style='in', h=5, bgc=(0.17, 0.17, 0.17))
    mc.frameLayout(label='Attribute', bgc=(0.2, 0.2, 0.2))
    mc.text(label='', h=5)
    mc.setParent('..')
    mc.rowLayout(nc=3, adj=1)
    CurveRadius_Value = 1
    if mc.objExists('*Dynamic_G'):
        CurveRadius_Value = mc.getAttr(the_cir + '.sx')
    mc.floatSliderGrp('New_CurveRadius_Valu', label=u'Radius：', cw3=(70, 40, 105), field=True, min=0, max=100,
                      v=CurveRadius_Value, cc='CurveRadius()')
    mc.text(label='', h=5)
    mc.setParent('..')
    mc.rowLayout(nc=3, adj=1)
    CurveUnumber_Value = 20
    if mc.objExists('*Dynamic_G'):
        CurveUnumber_Value = mc.getAttr(the_nurbsTesse + '.uNumber')
    mc.intSliderGrp('New_CurveUnumber_Value', label=u'U_Number：', cw3=(70, 40, 105), field=True, min=0, max=100,
                    v=CurveUnumber_Value, cc='CurveUnumber()')
    mc.text(label='', h=5)
    mc.setParent('..')
    mc.rowLayout(nc=3, adj=1)
    CurveVnumber_Value = 200
    if mc.objExists('*Dynamic_G'):
        CurveVnumber_Value = mc.getAttr(the_nurbsTesse + '.vNumber')
    mc.intSliderGrp('New_CurveVnumber_Value', label=u'V_Number：', cw3=(70, 40, 105), field=True, min=0, max=1000,
                    v=CurveVnumber_Value, cc='CurveVnumber()')
    mc.text(label='', h=10)
    mc.setParent('..')
    mc.text(label='', h=10)
    mc.rowLayout(nc=3, adj=1)
    DynamicNucleusSubsteps_Value = 3
    if mc.objExists('*Dynamic_G') and mc.objExists(DynamicNucleusNode):
        DynamicNucleusSubsteps_Value = mc.getAttr(DynamicNucleusNode + '.subSteps')

    mc.intSliderGrp('New_DynamicNucleusSubsteps_Value', label=u'SubSteps：', cw3=(70, 40, 105), field=True, min=0,
                    max=20, v=DynamicNucleusSubsteps_Value, cc='DynamicNucleusSubsteps()')
    mc.text(label='', h=5)
    mc.setParent('..')
    mc.rowLayout(nc=3, adj=1)
    DynamicNucleusMaxCollision_Value = 4
    if mc.objExists('*Dynamic_G') and mc.objExists(DynamicNucleusNode):
        DynamicNucleusMaxCollision_Value = mc.getAttr(DynamicNucleusNode + '.maxCollisionIterations')

    mc.intSliderGrp('New_DynamicNucleusMaxCollision_Value', label=u'Collision：', cw3=(70, 40, 105), field=True, min=0,
                    max=20, v=DynamicNucleusMaxCollision_Value, cc='DynamicNucleusMaxCollision()')
    mc.text(label='', h=5)
    mc.setParent('..')
    mc.text(label='', h=10)
    mc.rowLayout(nc=3, adj=1)
    SelfFriction_Value = 0.5
    if mc.objExists('*Dynamic_G') and mc.objExists(HairSystemNode):
        SelfFriction_Value = mc.getAttr(HairSystemNode + '.friction')

    mc.floatSliderGrp('New_HairSystemSelfFriction_Value', label=u'Friction：', cw3=(70, 40, 105), field=True, min=0,
                      max=1, v=SelfFriction_Value, cc='HairSystemSelfFriction()')
    mc.text(label='', h=5)
    mc.setParent('..')
    mc.rowLayout(nc=3, adj=1)
    Stretch_Value = 10
    if mc.objExists('*Dynamic_G') and mc.objExists(HairSystemNode):
        Stretch_Value = mc.getAttr(HairSystemNode + '.stretchResistance')

    mc.floatSliderGrp('New_HairSystemStretch_Value', label=u'Stretch：', cw3=(70, 40, 105), field=True, min=0, max=500,
                      v=Stretch_Value, cc='HairSystemStretch()')
    mc.text(label='', h=5)
    mc.setParent('..')
    mc.text(label='', h=5)
    mc.frameLayout(label='Operation', bgc=(0.2, 0.2, 0.2))
    mc.text(label='', h=5)
    mc.setParent('..')
    mc.rowLayout(nc=1, adj=1)
    mc.button(label=u'Create Dynamic Rope', command='CreateDynamicRope()', bgc=(0, 0, 0))
    mc.setParent('..')
    mc.text(label='', h=5)
    mc.rowLayout(nc=3)
    mc.button(label=u'Initial Dynamic', w=150, command='RestoreInitial()', bgc=(0, 0, 0))
    mc.button(label=u'Delete  Dynamic', w=150, command='DeleteDynamic()', bgc=(0, 0, 0))
    mc.setParent('..')
    mc.text(label='', h=5)
    mc.separator(style='in', h=2, bgc=(0.17, 0.17, 0.17))
    mc.text(label='', h=8)
    mc.rowLayout(nc=1, adj=1)
    mc.button(label=u'Finish', command='BingoRope()', bgc=(0, 0, 0))
    mc.setParent('..')
    mc.showWindow(MayaDynamicRope_Tool_UI_Wind)


MayaDynamicRope_Tool()