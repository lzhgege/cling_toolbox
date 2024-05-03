#! /usr/bin/env python 2.7 (62211)
#coding=utf-8
# Compiled at: 2021-12-15 13:24:42

import maya.cmds as cmds, maya.mel as mel, pymel.core as pm, random, sys, time, os, json
from functools import partial

icon_dir = r'Z:/Share/tcl0626/Maya_toolbox/plug-in/collect/Damage_Inc_V/Icon'
icon_ext = '.png'
icon_size = 32

lowAngle = 30
highAngle = 150
iconSize = 35
divisions = 2
itterations = 2
MAYAUSERAPPDIR = cmds.internalVar(uad=1)
PRESETJSON = os.path.join(MAYAUSERAPPDIR, 'DamagePresets.json')
WORKSPACEDMG = 'DamageInc'
if not os.path.exists(PRESETJSON):
    try:
        with open(PRESETJSON, 'w') as (f):
            data = {'Default': [
                         {'Edge': True, 'Surface': False, 
                            'Retopo': False, 
                            'Original': True, 
                            'Material': True, 
                            'Preservation': 2.0, 
                            'Depth': 0.5, 
                            'Noise Frequency': 1.0, 
                            'Noise Detail': 3.5, 
                            'Noise Scale': 1.0, 
                            'Multiplier': 5, 
                            'Axis X': False, 
                            'Axis Y': False, 
                            'Axis Z': False, 
                            'Resolution': 2, 
                            'Relax': 15, 
                            'Soften': True, 
                            'Pattern': 1}]}
            f.write(json.dumps(data, indent=2))
    except:
        pass
 
def launchDmgUI(*args):
    if cmds.workspaceControl(WORKSPACEDMG, exists=True):
        cmds.deleteUI(WORKSPACEDMG)
    if cmds.window('MayaDmg', exists=True):
        cmds.deleteUI('MayaDmg')
    MayaDamageUI()
    workspaceDmg()
 
 
def workspaceDmg(*args):
    if cmds.workspaceControl(WORKSPACEDMG, exists=True):
        cmds.deleteUI(WORKSPACEDMG)
    cmds.workspaceControl(WORKSPACEDMG, retain=False, floating=True, l='Damage Inc. V 1.2')
    cmds.control(mainWinDmg, e=1, p=WORKSPACEDMG)
 
 
def changeType(type, *args):
    if not type == 'edge':
        cmds.iconTextCheckBox('surDet', e=True, v=True)
        cmds.iconTextCheckBox('edgeDet', e=True, v=False)
    else:
        cmds.iconTextCheckBox('surDet', e=True, v=False)
        cmds.iconTextCheckBox('edgeDet', e=True, v=True)
 
 
def MayaDamageUI(*args):
    global mainWinDmg
    if cmds.window('MayaDmg', exists=1):
        cmds.deleteUI('MayaDmg')
    mainWinDmg = cmds.window('MayaDmg', t='Damage Inc v1.0', mxb=False)
    cmds.columnLayout()
    cmds.separator(h=20, style='none')
    cmds.rowColumnLayout(nr=1)
    cmds.text('            ')
    cmds.iconTextCheckBox('edgeDet', v=1, i=os.path.join(icon_dir, 'edgeDmgIcon' + icon_ext), w=icon_size, h=icon_size, ann=u'沿物体边缘损坏物体', cc=partial(changeType, 'edge'))
    cmds.text('    ')
    cmds.iconTextCheckBox('surDet', v=0, i=os.path.join(icon_dir, 'surDmgIcon' + icon_ext), w=icon_size, h=icon_size, ann=u'沿物体表面损坏物体', cc=partial(changeType, 'surface'))
    cmds.text('    ')
    cmds.iconTextCheckBox('retopo', v=0, i=os.path.join(icon_dir, 'wireFIcon' + icon_ext), w=icon_size, h=icon_size, ann=u"重新构造最终网格；如果使用，不会保留单独的材料")
    cmds.text('    ')
    cmds.iconTextCheckBox('keepOr', v=1, i=os.path.join(icon_dir, 'keepOrigIcon' + icon_ext), w=icon_size, h=icon_size, ann=u'保留原始网格并将其隐藏')
    cmds.text('    ')
    cmds.iconTextCheckBox('apllyMat', v=1, i=os.path.join(icon_dir, 'applyMatIcon' + icon_ext), w=icon_size, h=icon_size, ann=u'将单独的材料应用于受损区域')
    cmds.text('    ')
    cmds.setParent('..')
    cmds.separator(h=20)
    cmds.rowColumnLayout(nr=1)
    cmds.text('        ')
    cmds.optionMenu('presetMenu', l=u'  预设  ', w=180, cc=getPreset)
    with open(PRESETJSON) as (f):
        values = json.load(f)
    for i in values:
        cmds.menuItem(l=i)
 
    cmds.text('        ')
    cmds.button(l=u'保存', ann=u'将当前设置另存为预设', c=savePreset)
    cmds.text('    ')
    cmds.setParent('..')
    cmds.separator(h=20, style='none')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'          原始保留 :            ')
    cmds.floatSliderGrp('StrengthValField', f=1, s=0.01, v=1.5, min=0.01, max=5, w=150, ann=u'原始对象保护（反向强度）')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'            深度 :               ')
    cmds.floatSliderGrp('DepthValField', f=1, s=0.01, v=0.5, min=0.01, max=2, w=150, ann=u'深度')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'          噪声模式 :          ')
    cmds.intSliderGrp('PatternValField', f=1, v=1, min=0, max=4, w=150, ann=u'噪声模式. \n\n0 is Perlin Noise 3D \n\n1 is Billow 3D \n\n2 is Volume Wave 3D \n\n3 is Wispy 3D \n\n4 is Space Time 3D')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'         噪声频率 :          ')
    cmds.floatSliderGrp('FreqValField', f=1, s=0.001, v=1, min=0.001, max=1000.0, w=150, ann=u'噪声频率')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'      噪波细节调整 :       ')
    cmds.floatSliderGrp('DetailValField', f=1, s=0.01, v=3.5, min=1, max=100.0, w=150, ann=u'噪波细节调整')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'        噪波比例 :          ')
    cmds.floatSliderGrp('NoiseScaleValField', f=1, v=1, min=0.1, max=100.0, w=150, ann=u'噪波比例')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text('     Scale Multiplier :      ')
    cmds.intSliderGrp('NoiseMultField', f=1, v=5, min=1, max=100, w=150, ann='Scale Multiplier')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'      噪波比例轴:       ')
    cmds.checkBoxGrp('NoiseScaleX', v1=0, ann='Noise Scale X')
    cmds.text('  X        ')
    cmds.checkBoxGrp('NoiseScaleY', v1=0, ann='Noise Scale Y')
    cmds.text('  Y        ')
    cmds.checkBoxGrp('NoiseScaleZ', v1=0, ann='Noise Scale Z')
    cmds.text('  Z        ')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'  损坏解决方案 :  ')
    cmds.intSliderGrp('ResValField', f=1, v=2, min=1, max=4, w=150, ann='Damage Resolution')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'      松弛迭代次数 :        ')
    cmds.intSliderGrp('RelaxValField', f=1, v=15, min=0, max=200, w=150, ann='Damage smoothness')
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.separator(style='single', hr=1, w=300, h=30)
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text(u'      软化        ')
    cmds.checkBox('smoothCheck', l='', v=1)
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.separator(style='single', hr=1, w=300, h=30)
    cmds.setParent('..')
    cmds.rowColumnLayout(nr=1)
    cmds.text('        ')
    cmds.iconTextButton(i=os.path.join(icon_dir, 'BreakitIcon2' + icon_ext), w=250, h=30, c=damage)
    cmds.setParent('..')
    cmds.separator(h=10, style='none')
    cmds.setParent('..')
    cmds.window('MayaDmg', e=1, w=300, h=250, sizeable=1)
 
 
def damage(*args):
    start = time.time()
    selections = cmds.ls(sl=1)
    allObjList = []
    targetNum = 0
    strength = cmds.floatSliderGrp('StrengthValField', q=1, v=1)
    noiseFreq = cmds.floatSliderGrp('FreqValField', q=1, v=1) / 10
    noiseScale = cmds.floatSliderGrp('NoiseScaleValField', q=1, v=1)
    scaleMult = cmds.intSliderGrp('NoiseMultField', q=1, v=1)
    X = cmds.checkBoxGrp('NoiseScaleX', q=1, v1=1)
    Y = cmds.checkBoxGrp('NoiseScaleY', q=1, v1=1)
    Z = cmds.checkBoxGrp('NoiseScaleZ', q=1, v1=1)
    itterations = cmds.intSliderGrp('RelaxValField', q=1, v=1)
    reTopo = cmds.iconTextCheckBox('retopo', q=1, v=1)
    keepOr = cmds.iconTextCheckBox('keepOr', q=1, v=1)
    edgeDetail = cmds.iconTextCheckBox('edgeDet', q=1, v=1)
    surfaceDetail = cmds.iconTextCheckBox('surDet', q=1, v=1)
    apllyMaterial = cmds.iconTextCheckBox('apllyMat', q=1, v=1)
    smoothness = cmds.checkBox('smoothCheck', q=1, v=1)
    roughness = cmds.floatSliderGrp('DetailValField', q=1, v=1)
    resolution = cmds.intSliderGrp('ResValField', q=1, v=1)
    depthVal = cmds.floatSliderGrp('DepthValField', q=1, v=1)
    noisePattern = cmds.intSliderGrp('PatternValField', q=1, v=1)
    if not cmds.objExists('damageMat'):
        damageMat = cmds.shadingNode('lambert', asShader=1, n='damageMat')
        damageMatSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=1, name='damageMatSG')
        cmds.connectAttr(damageMat + '.outColor', damageMatSG + '.surfaceShader', f=1)
        cmds.setAttr(damageMat + '.color', 0, 1, 0, type='double3')
    for selection in selections:
        allObjList.append(selection)
 
    if len(allObjList) > 0:
        for i in allObjList:
            sourceList = []
            damageList = []
            dimensionsAll = []
            faceListA = []
            faceListB = []
            flatFaceListA = []
            geoType = cmds.objectType(i)
            timeRnd = random.uniform(0, 100)
            if geoType == 'transform':
                if edgeDetail:
                    if keepOr:
                        originalOBJ = cmds.duplicate(i)
                        cmds.hide(i)
                        for obj in originalOBJ:
                            sourceList.append(obj)
 
                    else:
                        sourceList.append(i)
                    for sourceObj in sourceList:
                        scaleXAttr = cmds.getAttr(sourceObj + '.scaleX')
                        scaleYAttr = cmds.getAttr(sourceObj + '.scaleY')
                        scaleZAttr = cmds.getAttr(sourceObj + '.scaleZ')
                        bbox = cmds.exactWorldBoundingBox(sourceObj)
                        dimentionX = bbox[3] - bbox[0]
                        dimensionsAll.append(dimentionX)
                        dimentionY = bbox[4] - bbox[1]
                        dimensionsAll.append(dimentionY)
                        dimentionZ = bbox[5] - bbox[2]
                        dimensionsAll.append(dimentionZ)
                        getDiv = max(dimensionsAll) / 40
                        getMult = 40 / max(dimensionsAll)
                        if max(dimensionsAll) >= 40:
                            cmds.scale(scaleXAttr / getDiv, scaleYAttr / getDiv, scaleZAttr / getDiv, sourceObj)
                            scaleXAttrNew = cmds.getAttr(sourceObj + '.scaleX')
                            scaleYAttrNew = cmds.getAttr(sourceObj + '.scaleY')
                            scaleZAttrNew = cmds.getAttr(sourceObj + '.scaleZ')
                        else:
                            if max(dimensionsAll) < 40:
                                cmds.scale(scaleXAttr * getMult, scaleYAttr * getMult, scaleZAttr * getMult, sourceObj)
                                scaleXAttrNew = cmds.getAttr(sourceObj + '.scaleX')
                                scaleYAttrNew = cmds.getAttr(sourceObj + '.scaleY')
                                scaleZAttrNew = cmds.getAttr(sourceObj + '.scaleZ')
                        targetObj = cmds.duplicate(sourceObj)
                        cmds.select(targetObj)
                        if apllyMaterial:
                            cmds.hyperShade(assign='damageMat')
                        targetReMesh = cmds.polyRemesh(targetObj, ipt=0)
                        for ReMesh in targetReMesh:
                            try:
                                cmds.setAttr(ReMesh + '.maxTriangleCount', 4000)
                                cmds.setAttr(ReMesh + '.refineThreshold', 2)
                            except:
                                pass
 
                        retopo = cmds.polyRetopo(targetObj)
                        for retopoeded in retopo:
                            try:
                                cmds.setAttr(retopoeded + '.targetFaceCount', 1000)
                                cmds.setAttr(retopoeded + '.curveSingularitySeparation', 1)
                                cmds.setAttr(retopoeded + '.curveInfluenceDirection', 1)
                            except:
                                pass
 
                        if reTopo:
                            retopoedMesh = cmds.duplicate(targetObj)
                            cmds.hyperShade(assign='lambert1')
                            placeholder = cmds.rename(retopoedMesh, sourceObj + '_damagePlaceholder')
                        cmds.polyMergeVertex(targetObj, d=0.3, am=1, ch=1)
                        cmds.delete(sourceObj, ch=1)
                        cmds.delete(targetObj, ch=1)
                        cmds.select(clear=1)
                        for trg in targetObj:
                            cmds.rename(trg, sourceObj + '_damage')
                            damageList.append(sourceObj + '_damage')
 
                    for target in damageList:
                        targetNum += 1
                        for r in damageList:
                            if len(allObjList) == 1:
                                import sys
                                sys.stdout.write('Computing damage for ' + str(targetNum) + ' out of ' + str(len(allObjList)) + ' object...\n')
                            else:
                                import sys
                                sys.stdout.write('Computing damage for ' + str(targetNum) + ' out of ' + str(len(allObjList)) + ' objects...\n')
 
                        cmds.select(target)
                        cmds.ConvertSelectionToFaces()
                        cmds.polyExtrudeFacet(ltz=-(depthVal - 0.05))
                        selection = cmds.ls(sl=1)
                        for face in selection:
                            faceListA.append(face)
 
                        for facea in faceListA:
                            cmds.select(facea, add=1)
 
                        cmds.select(target + '.f[*]', tgl=True)
                        cmds.polyDelFacet()
                        cmds.select(target)
                        deformerTarget = cmds.textureDeformer(n=target + '_deformer')
                        cmds.setAttr(target + '_deformer.strength', strength)
                        cmds.setAttr(target + '_deformer.offset', 0.25)
                        cmds.setAttr(target + '_deformer.pointSpace', 0)
                        cmds.setAttr(target + '_deformer.direction', 0)
                        volNoise = cmds.shadingNode('volumeNoise', asTexture=1, n=target + '_Noise')
                        cmds.setAttr(volNoise + '.threshold', 0)
                        cmds.setAttr(volNoise + '.amplitude', 0.5)
                        cmds.setAttr(volNoise + '.ratio', 1)
                        cmds.setAttr(volNoise + '.frequencyRatio', roughness)
                        cmds.setAttr(volNoise + '.noiseType', noisePattern)
                        cmds.setAttr(volNoise + '.frequency', noiseFreq)
                        cmds.setAttr(volNoise + '.time', timeRnd)
                        cmds.setAttr(volNoise + '.falloff', 2)
                        cmds.setAttr(volNoise + '.defaultColor', 0.5, 0.5, 0.5, type='double3')
                        cmds.setAttr(volNoise + '.colorGain', 0.5, 0.5, 0.5, type='double3')
                        cmds.setAttr(volNoise + '.spottyness', 1)
                        cmds.setAttr(volNoise + '.sizeRand', 0)
                        cmds.setAttr(volNoise + '.randomness', 1)
                        if X:
                            cmds.setAttr(volNoise + '.scaleX', noiseScale * scaleMult)
                        else:
                            cmds.setAttr(volNoise + '.scaleX', noiseScale)
                        if Y:
                            cmds.setAttr(volNoise + '.scaleY', noiseScale * scaleMult)
                        else:
                            cmds.setAttr(volNoise + '.scaleY', noiseScale)
                        if Z:
                            cmds.setAttr(volNoise + '.scaleZ', noiseScale * scaleMult)
                        else:
                            cmds.setAttr(volNoise + '.scaleZ', noiseScale)
                        cmds.setAttr(volNoise + '.invert', 1)
                        cmds.connectAttr(volNoise + '.outColor', target + '_deformer.texture', f=1)
                        cmds.polyAverageVertex(target, i=2 * itterations, ch=1)
                        try:
                            cmds.polyMergeVertex(target, d=0.35, am=1, ch=1)
                        except:
                            pass
 
                        if smoothness:
                            cmds.polySoftEdge(target, a=180, ch=1)
                        cmds.polySubdivideFacet(target, dv=resolution)
                        cmds.delete(target, ch=1)
                        try:
                            finalObj = cmds.polyCBoolOp(sourceObj, target, op=3, ch=1, preserveColor=0, classification=1, name=i + '_damaged')
                        except:
                            print 'Error'
 
                        if reTopo:
                            cmds.select(clear=True)
                            cmds.showHidden(placeholder)
                            for div in range(resolution):
                                cmds.polySubdivideFacet(placeholder, dv=1)
                                cmds.select(placeholder)
                                cmds.select(i + '_damaged', add=True)
                                shrinkWrapNode = cmds.deformer(placeholder, type='shrinkWrap')[0]
                                cmds.connectAttr(i + '_damaged' + '.worldMesh[0]', shrinkWrapNode + '.targetGeom')
                                cmds.setAttr(shrinkWrapNode + '.projection', 4)
                                try:
                                    cmds.delete(placeholder, ch=1)
                                    cmds.delete(finalObj, ch=1)
                                except:
                                    pass
 
                            cmds.delete(i + '_damaged')
                            cmds.rename(placeholder, i + '_damaged')
                        try:
                            cmds.delete(finalObj, ch=1)
                            cmds.delete(volNoise)
                        except:
                            pass
 
                        cmds.select(i + '_damaged')
                        if not reTopo:
                            scaleXAttrFinal = cmds.getAttr(i + '_damaged' + '.scaleX')
                            scaleYAttrFinal = cmds.getAttr(i + '_damaged' + '.scaleY')
                            scaleZAttrFinal = cmds.getAttr(i + '_damaged' + '.scaleZ')
                            bboxFinal = cmds.exactWorldBoundingBox(i + '_damaged')
                            getDivX = scaleXAttrFinal / scaleXAttrNew
                            getDivY = scaleYAttrFinal / scaleYAttrNew
                            getDivZ = scaleZAttrFinal / scaleZAttrNew
                            getMultX = scaleXAttrNew / scaleXAttrFinal
                            getMultY = scaleYAttrNew / scaleYAttrFinal
                            getMultZ = scaleZAttrNew / scaleZAttrFinal
                            if bboxFinal[3] - bboxFinal[0] >= bbox[3] - bbox[0]:
                                cmds.setAttr(i + '_damaged.scaleX', getDivX)
                                cmds.setAttr(i + '_damaged.scaleY', getDivY)
                                cmds.setAttr(i + '_damaged.scaleZ', getDivZ)
                            else:
                                if bboxFinal[3] - bboxFinal[0] < bbox[3] - bbox[0]:
                                    cmds.setAttr(i + '_damaged.scaleX', scaleXAttrFinal / getMultX)
                                    cmds.setAttr(i + '_damaged.scaleY', scaleYAttrFinal / getMultY)
                                    cmds.setAttr(i + '_damaged.scaleZ', scaleZAttrFinal / getMultZ)
                            renamed = cmds.rename(i + '_damaged', i + '_Damaged')
                            for renamedObj in renamed:
                                cmds.FreezeTransformations(renamedObj)
 
                        else:
                            cmds.setAttr(i + '_damaged' + '.scaleX', 1)
                            cmds.setAttr(i + '_damaged' + '.scaleY', 1)
                            cmds.setAttr(i + '_damaged' + '.scaleZ', 1)
                            renamed = cmds.rename(i + '_damaged', i + '_Damaged')
                            for renamedObj in renamed:
                                cmds.FreezeTransformations(renamedObj)
 
                            cmds.sets(i + '_Damaged', e=True, forceElement='initialShadingGroup')
                        cmds.refresh(cv=1)
 
                if surfaceDetail:
                    if keepOr:
                        originalOBJ = cmds.duplicate(i)
                        cmds.hide(i)
                        for obj in originalOBJ:
                            sourceList.append(obj)
 
                    else:
                        sourceList.append(i)
                    for sourceObj in sourceList:
                        scaleXAttr = cmds.getAttr(sourceObj + '.scaleX')
                        scaleYAttr = cmds.getAttr(sourceObj + '.scaleY')
                        scaleZAttr = cmds.getAttr(sourceObj + '.scaleZ')
                        bbox = cmds.exactWorldBoundingBox(sourceObj)
                        dimentionX = bbox[3] - bbox[0]
                        dimensionsAll.append(dimentionX)
                        dimentionY = bbox[4] - bbox[1]
                        dimensionsAll.append(dimentionY)
                        dimentionZ = bbox[5] - bbox[2]
                        dimensionsAll.append(dimentionZ)
                        getDiv = max(dimensionsAll) / 30
                        getMult = 30 / max(dimensionsAll)
                        if max(dimensionsAll) >= 30:
                            cmds.scale(scaleXAttr / getDiv, scaleYAttr / getDiv, scaleZAttr / getDiv, sourceObj)
                            scaleXAttrNew = cmds.getAttr(sourceObj + '.scaleX')
                            scaleYAttrNew = cmds.getAttr(sourceObj + '.scaleY')
                            scaleZAttrNew = cmds.getAttr(sourceObj + '.scaleZ')
                        else:
                            if max(dimensionsAll) < 30:
                                cmds.scale(scaleXAttr * getMult, scaleYAttr * getMult, scaleZAttr * getMult, sourceObj)
                                scaleXAttrNew = cmds.getAttr(sourceObj + '.scaleX')
                                scaleYAttrNew = cmds.getAttr(sourceObj + '.scaleY')
                                scaleZAttrNew = cmds.getAttr(sourceObj + '.scaleZ')
                        targetObj = cmds.duplicate(sourceObj)
                        cmds.select(targetObj)
                        if apllyMaterial:
                            cmds.hyperShade(assign='damageMat')
                        targetReMesh = cmds.polyRemesh(targetObj, ipt=0)
                        for ReMesh in targetReMesh:
                            try:
                                cmds.setAttr(ReMesh + '.maxTriangleCount', 4000)
                                cmds.setAttr(ReMesh + '.refineThreshold', 2)
                            except:
                                pass
 
                        retopo = cmds.polyRetopo(targetObj)
                        for retopoeded in retopo:
                            try:
                                cmds.setAttr(retopoeded + '.targetFaceCount', 1000)
                                cmds.setAttr(retopoeded + '.curveSingularitySeparation', 1)
                                cmds.setAttr(retopoeded + '.curveInfluenceDirection', 1)
                            except:
                                pass
 
                        cmds.polyMergeVertex(targetObj, d=0.3, am=1, ch=1)
                        if reTopo:
                            retopoedMesh = cmds.duplicate(targetObj)
                            cmds.hyperShade(assign='lambert1')
                            placeholder = cmds.rename(retopoedMesh, sourceObj + '_damagePlaceholder')
                        cmds.SmoothPolygon()
                        cmds.delete(sourceObj, ch=1)
                        cmds.delete(targetObj, ch=1)
                        cmds.select(clear=1)
                        for trg in targetObj:
                            cmds.rename(trg, sourceObj + '_damage')
                            damageList.append(sourceObj + '_damage')
 
                    for target in damageList:
                        targetNum += 1
                        for r in damageList:
                            if len(allObjList) == 1:
                                import sys
                                sys.stdout.write('Computing damage for ' + str(targetNum) + ' out of ' + str(len(allObjList)) + ' object...\n')
                            else:
                                import sys
                                sys.stdout.write('Computing damage for ' + str(targetNum) + ' out of ' + str(len(allObjList)) + ' objects...\n')
 
                        cmds.select(target)
                        try:
                            cmds.polyMergeVertex(target, d=0.05, am=1, ch=1)
                        except:
                            pass
 
                        cmds.ConvertSelectionToFaces()
                        cmds.polyExtrudeFacet(ltz=-depthVal / 2)
                        selection = cmds.ls(sl=1)
                        for face in selection:
                            faceListA.append(face)
 
                        for facea in faceListA:
                            cmds.select(facea, add=1)
 
                        cmds.select(target + '.f[*]', tgl=True)
                        cmds.polyDelFacet()
                        cmds.select(target)
                        cmds.delete(target, ch=1)
                        cmds.polyAverageVertex(target, i=itterations * 2, ch=1)
                        cmds.polySubdivideFacet(dv=resolution - 1)
                        cmds.delete(target, ch=1)
                        deformerTarget = cmds.textureDeformer(n=target + '_deformer')
                        cmds.setAttr(target + '_deformer.strength', strength * 2 / 3)
                        cmds.setAttr(target + '_deformer.offset', -strength * 2 * 0.1 / 3)
                        cmds.setAttr(target + '_deformer.pointSpace', 1)
                        cmds.setAttr(target + '_deformer.direction', 0)
                        volNoise = cmds.shadingNode('volumeNoise', asTexture=1, n=target + '_Noise')
                        cmds.setAttr(volNoise + '.threshold', 0.058)
                        cmds.setAttr(volNoise + '.amplitude', 0.53)
                        cmds.setAttr(volNoise + '.ratio', 0.9)
                        cmds.setAttr(volNoise + '.frequencyRatio', roughness)
                        cmds.setAttr(volNoise + '.noiseType', noisePattern)
                        cmds.setAttr(volNoise + '.frequency', noiseFreq)
                        cmds.setAttr(volNoise + '.time', timeRnd)
                        cmds.setAttr(volNoise + '.falloff', 2)
                        cmds.setAttr(volNoise + '.spottyness', 0.1)
                        cmds.setAttr(volNoise + '.sizeRand', 0)
                        cmds.setAttr(volNoise + '.randomness', 1)
                        if X:
                            cmds.setAttr(volNoise + '.scaleX', noiseScale * scaleMult)
                        else:
                            cmds.setAttr(volNoise + '.scaleX', noiseScale)
                        if Y:
                            cmds.setAttr(volNoise + '.scaleY', noiseScale * scaleMult)
                        else:
                            cmds.setAttr(volNoise + '.scaleY', noiseScale)
                        if Z:
                            cmds.setAttr(volNoise + '.scaleZ', noiseScale * scaleMult)
                        else:
                            cmds.setAttr(volNoise + '.scaleZ', noiseScale)
                        cmds.connectAttr(volNoise + '.outColor', target + '_deformer.texture', f=1)
                        cmds.delete(target, ch=1)
                        cmds.polyAverageVertex(target, i=itterations, ch=1)
                        if smoothness:
                            cmds.polySoftEdge(target, a=180, ch=1)
                        try:
                            cmds.polyMergeVertex(target, d=0.05, am=1, ch=1)
                        except:
                            pass
 
                        cmds.delete(target, ch=1)
                        try:
                            finalObj = cmds.polyCBoolOp(sourceObj, target, op=3, ch=1, preserveColor=0, classification=1, name=i + '_damaged')
                        except:
                            print 'Error'
 
                        if reTopo:
                            cmds.select(clear=True)
                            cmds.showHidden(placeholder)
                            for div in range(resolution):
                                cmds.polySubdivideFacet(placeholder, dv=1)
                                cmds.select(placeholder)
                                cmds.select(i + '_damaged', add=True)
                                shrinkWrapNode = pm.deformer(placeholder, type='shrinkWrap')[0]
                                pm.PyNode(i + '_damaged').worldMesh[0] >> shrinkWrapNode.targetGeom
                                cmds.setAttr(shrinkWrapNode + '.projection', 4)
                                try:
                                    cmds.delete(placeholder, ch=1)
                                    cmds.delete(finalObj, ch=1)
                                except:
                                    pass
 
                            cmds.delete(i + '_damaged')
                            cmds.rename(placeholder, i + '_damaged')
                        try:
                            cmds.delete(finalObj, ch=1)
                            cmds.delete(volNoise)
                        except:
                            pass
 
                        cmds.select(i + '_damaged')
                        if not reTopo:
                            scaleXAttrFinal = cmds.getAttr(i + '_damaged' + '.scaleX')
                            scaleYAttrFinal = cmds.getAttr(i + '_damaged' + '.scaleY')
                            scaleZAttrFinal = cmds.getAttr(i + '_damaged' + '.scaleZ')
                            bboxFinal = cmds.exactWorldBoundingBox(i + '_damaged')
                            getDivX = scaleXAttrFinal / scaleXAttrNew
                            getDivY = scaleYAttrFinal / scaleYAttrNew
                            getDivZ = scaleZAttrFinal / scaleZAttrNew
                            getMultX = scaleXAttrNew / scaleXAttrFinal
                            getMultY = scaleYAttrNew / scaleYAttrFinal
                            getMultZ = scaleZAttrNew / scaleZAttrFinal
                            if bboxFinal[3] - bboxFinal[0] >= bbox[3] - bbox[0]:
                                cmds.setAttr(i + '_damaged.scaleX', getDivX)
                                cmds.setAttr(i + '_damaged.scaleY', getDivY)
                                cmds.setAttr(i + '_damaged.scaleZ', getDivZ)
                            else:
                                if bboxFinal[3] - bboxFinal[0] < bbox[3] - bbox[0]:
                                    cmds.setAttr(i + '_damaged.scaleX', scaleXAttrFinal / getMultX)
                                    cmds.setAttr(i + '_damaged.scaleY', scaleYAttrFinal / getMultY)
                                    cmds.setAttr(i + '_damaged.scaleZ', scaleZAttrFinal / getMultZ)
                            renamed = cmds.rename(i + '_damaged', i + '_Damaged')
                            for renamedObj in renamed:
                                cmds.FreezeTransformations(renamedObj)
 
                        else:
                            cmds.setAttr(i + '_damaged' + '.scaleX', 1)
                            cmds.setAttr(i + '_damaged' + '.scaleY', 1)
                            cmds.setAttr(i + '_damaged' + '.scaleZ', 1)
                            renamed = cmds.rename(i + '_damaged', i + '_Damaged')
                            for renamedObj in renamed:
                                cmds.FreezeTransformations(renamedObj)
 
                            cmds.sets(i + '_Damaged', e=True, forceElement='initialShadingGroup')
                        cmds.refresh(cv=1)
 
        end = time.time()
        if len(allObjList) == 1:
            import sys
            sys.stdout.write('Damage applied to ' + str(len(allObjList)) + ' object in ' + str('%.2f' % (end - start)) + ' seconds!\n')
        else:
            import sys
            sys.stdout.write('Damage applied to ' + str(len(allObjList)) + ' objects in ' + str('%.2f' % (end - start)) + ' seconds!\n')
    else:
        import sys
        sys.stdout.write('Please select something first!')
 
 
def getCurrentAxis(*args):
    if cmds.checkBoxGrp('NoiseScaleX', q=1, v1=1) == True:
        axisX = 1
    else:
        axisX = 0
    if cmds.checkBoxGrp('NoiseScaleY', q=1, v1=1) == True:
        axisY = 1
    else:
        axisY = 0
    if cmds.checkBoxGrp('NoiseScaleZ', q=1, v1=1) == True:
        axisZ = 1
    else:
        axisZ = 0
    return (
     axisX, axisY, axisZ)
 
 
def savePreset(*args):
    strength = cmds.floatSliderGrp('StrengthValField', q=1, v=1)
    noiseFreq = cmds.floatSliderGrp('FreqValField', q=1, v=1)
    noiseScale = cmds.floatSliderGrp('NoiseScaleValField', q=1, v=1)
    scaleMult = cmds.intSliderGrp('NoiseMultField', q=1, v=1)
    X = cmds.checkBoxGrp('NoiseScaleX', q=1, v1=1)
    Y = cmds.checkBoxGrp('NoiseScaleY', q=1, v1=1)
    Z = cmds.checkBoxGrp('NoiseScaleZ', q=1, v1=1)
    itterations = cmds.intSliderGrp('RelaxValField', q=1, v=1)
    reTopo = cmds.iconTextCheckBox('retopo', q=1, v=1)
    keepOr = cmds.iconTextCheckBox('keepOr', q=1, v=1)
    edgeDetail = cmds.iconTextCheckBox('edgeDet', q=1, v=1)
    surfaceDetail = cmds.iconTextCheckBox('surDet', q=1, v=1)
    apllyMaterial = cmds.iconTextCheckBox('apllyMat', q=1, v=1)
    smoothness = cmds.checkBox('smoothCheck', q=1, v=1)
    roughness = cmds.floatSliderGrp('DetailValField', q=1, v=1)
    resolution = cmds.intSliderGrp('ResValField', q=1, v=1)
    depthVal = cmds.floatSliderGrp('DepthValField', q=1, v=1)
    getAxis = getCurrentAxis()
    noisePattern = cmds.intSliderGrp('PatternValField', q=1, v=1)
    result = cmds.promptDialog(title='Preset Name', message='Name the preset :', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
    with open(PRESETJSON) as (f):
        feeds = json.load(f)
    presetNames = feeds.keys()
    if result == 'OK':
        Name = cmds.promptDialog(query=True, text=True)
        if Name not in presetNames:
            data = {Name: [
                    {'Edge': edgeDetail, 'Surface': surfaceDetail, 
                       'Retopo': reTopo, 
                       'Original': keepOr, 
                       'Material': apllyMaterial, 
                       'Preservation': strength, 
                       'Depth': depthVal, 
                       'Noise Frequency': noiseFreq, 
                       'Noise Detail': roughness, 
                       'Noise Scale': noiseScale, 
                       'Multiplier': scaleMult, 
                       'Axis X': getAxis[0], 
                       'Axis Y': getAxis[1], 
                       'Axis Z': getAxis[2], 
                       'Resolution': resolution, 
                       'Relax': itterations, 
                       'Soften': smoothness, 
                       'Pattern': noisePattern}]}
            a = {}
            if not os.path.isfile(PRESETJSON):
                a.update(data)
                with open(PRESETJSON, mode='w') as (f):
                    f.write(json.dumps(a, indent=2))
            else:
                with open(PRESETJSON) as (f):
                    feeds = json.load(f)
                feeds.update(data)
                with open(PRESETJSON, mode='w') as (f):
                    f.write(json.dumps(feeds, indent=2))
            cmds.menuItem(l=Name, p='presetMenu')
            cmds.optionMenu('presetMenu', e=True, v=Name)
        else:
            import sys
            sys.stdout.write('Preset Already Exists')
            savePreset()
            return
    else:
        return
 
 
def getPreset(*args):
    preset = cmds.optionMenu('presetMenu', q=True, v=True)
    loadPreset(preset)
 
 
def loadPreset(Name, *args):
    attributes = [
     'Edge', 'Surface', 'Retopo', 'Original', 'Material', 'Preservation',
     'Depth', 'Noise Frequency', 'Noise Detail', 'Noise Scale', 'Multiplier',
     'Axis X', 'Axis Y', 'Axis Z', 'Resolution', 'Relax', 'Soften', 'Pattern']
    with open(PRESETJSON) as (f):
        values = json.load(f)
        preset = values[Name]
        for attr in attributes:
            getVal = values[Name][0][attr]
            if attr == 'Edge':
                cmds.iconTextCheckBox('edgeDet', e=True, v=getVal)
            if attr == 'Surface':
                cmds.iconTextCheckBox('surDet', e=True, v=getVal)
            if attr == 'Retopo':
                cmds.iconTextCheckBox('retopo', e=True, v=getVal)
            if attr == 'Original':
                cmds.iconTextCheckBox('keepOr', e=True, v=getVal)
            if attr == 'Material':
                cmds.iconTextCheckBox('apllyMat', e=True, v=getVal)
            if attr == 'Preservation':
                cmds.floatSliderGrp('StrengthValField', e=True, v=getVal)
            if attr == 'Depth':
                cmds.floatSliderGrp('DepthValField', e=True, v=getVal)
            if attr == 'Noise Frequency':
                cmds.floatSliderGrp('FreqValField', e=True, v=getVal)
            if attr == 'Noise Detail':
                cmds.floatSliderGrp('DetailValField', e=True, v=getVal)
            if attr == 'Noise Scale':
                cmds.floatSliderGrp('NoiseScaleValField', e=True, v=getVal)
            if attr == 'Multiplier':
                cmds.intSliderGrp('NoiseMultField', e=True, v=getVal)
            if attr == 'Axis X':
                cmds.checkBoxGrp('NoiseScaleX', e=True, v1=getVal)
            if attr == 'Axis Y':
                cmds.checkBoxGrp('NoiseScaleY', e=True, v1=getVal)
            if attr == 'Axis Z':
                cmds.checkBoxGrp('NoiseScaleZ', e=True, v1=getVal)
            if attr == 'Resolution':
                cmds.intSliderGrp('ResValField', e=True, v=getVal)
            if attr == 'Relax':
                cmds.intSliderGrp('RelaxValField', e=True, v=getVal)
            if attr == 'Soften':
                cmds.checkBox('smoothCheck', e=True, v=getVal)
            if attr == 'Pattern':
                cmds.intSliderGrp('PatternValField', e=True, v=getVal)
launchDmgUI()