# -*- coding: utf-8 -*-
# 作者：cling
# 微信：clingkaka
# 个人主页：www.cg6i.com
# 模型下载：www.cgfml.com
# AI聊天绘画：ai.cgfml.com
# 敲码不易修改搬运请保留以上信息，感谢！！！！！


from PySide2 import QtWidgets, QtGui, QtCore
import maya.cmds as cmds
#import pymel.core as pm


class MyLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(MyLineEdit, self).__init__(parent)
        self.setAcceptDrops(True)  # 允许接收拖放事件

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():  # 如果拖入的是文件或者URL
            event.accept()  # 接受事件
        else:
            event.ignore()  # 忽略事件

    def dropEvent(self, event):
        urls = event.mimeData().urls()  # 获取拖入的文件或者URL列表
        if urls:  # 如果列表不为空
            path = urls[0].toLocalFile()  # 获取第一个文件或者URL的本地路径
            self.setText(path)  # 设置文本框的内容为路径


class CreateMaterialWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(CreateMaterialWindow, self).__init__(parent)
        self.setWindowTitle("Arnold_PBR")
        self.resize(400, 300)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 设置窗口始终在顶部
        self.createUI()

    def createUI(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Name row
        nameRow = QtWidgets.QHBoxLayout()  # 创建一个水平布局
        nameLabel = QtWidgets.QLabel("材质球名称:")  # 创建一个标签
        self.nameText = QtWidgets.QLineEdit()  # 创建一个文本框
        self.nameText.setPlaceholderText("请输入自定义材质球名字，默认为：Material")  # 设置示意文字
        nameRow.addWidget(nameLabel)  # 把标签添加到水平布局里
        nameRow.addWidget(self.nameText)  # 把文本框也添加到水平布局里
        layout.addLayout(nameRow)  # 把水平布局添加到垂直布局里

        # Top row
        topRow = QtWidgets.QHBoxLayout()  # 创建一个水平布局
        topLabel = QtWidgets.QLabel("选择色彩空间:")
        self.sRGBCheck = QtWidgets.QCheckBox("sRGB")  # 创建一个复选框
        self.ACESCheck = QtWidgets.QCheckBox("ACES")  # 创建另一个复选框
        self.ACESCheck.setChecked(True)
        self.colorSpaceGroup = QtWidgets.QButtonGroup()  # 创建一个按钮组
        self.colorSpaceGroup.addButton(self.sRGBCheck)  # 把复选框添加到按钮组里
        self.colorSpaceGroup.addButton(self.ACESCheck)  # 把另一个复选框也添加到按钮组里
        self.colorSpaceGroup.setExclusive(True)  # 设置按钮组的模式为互斥的
        topRow.addWidget(topLabel)
        topRow.addWidget(self.sRGBCheck)  # 把复选框添加到水平布局里
        topRow.addWidget(self.ACESCheck)  # 把另一个复选框也添加到水平布局里
        layout.addLayout(topRow)  # 把水平布局添加到垂直布局里

        shezhiRow = QtWidgets.QHBoxLayout()  # 创建一个水平布局
        # 勾选复选框则开启UDIM
        self.udim = QtWidgets.QCheckBox("是否使用udim")
        self.udim.setChecked(False)  # 默认不勾选
        layout.addWidget(self.udim)

        self.Triplanar = QtWidgets.QCheckBox("是否使用映射节点")
        self.Triplanar.setChecked(False)  # 默认不勾选
        layout.addWidget(self.Triplanar)
        shezhiRow.addWidget(self.udim)  # 把复选框添加到水平布局里
        shezhiRow.addWidget(self.Triplanar)  # 把另一个复选框也添加到水平布局里
        layout.addLayout(shezhiRow)  # 把水平布局添加到垂直布局里

        # Base Color row
        baseColorRow = QtWidgets.QHBoxLayout()
        baseColorLabel = QtWidgets.QLabel("Base Color:")
        self.baseColorText = MyLineEdit()  # 使用自定义的类
        self.baseColorText.setPlaceholderText("请输入或拖入Base Color文件")  # 设置示意文字
        baseColorBtn = QtWidgets.QPushButton("选择贴图")
        baseColorBtn.clicked.connect(self.getBaseColorFile)  # 用单独的方法来处理点击事件
        baseColorRow.addWidget(baseColorLabel)
        baseColorRow.addWidget(self.baseColorText)
        baseColorRow.addWidget(baseColorBtn)
        layout.addLayout(baseColorRow)

        # 勾选复选框则先把baseColorTexture连接到aiColorCorrect节点再连接到.baseColor，不勾选则
        self.colorCorrectCheck = QtWidgets.QCheckBox("是否添加调色节点")
        self.colorCorrectCheck.setChecked(False)  # 默认不勾选
        layout.addWidget(self.colorCorrectCheck)

        # Normal row
        normalRow = QtWidgets.QHBoxLayout()
        normalLabel = QtWidgets.QLabel("Normal:")
        self.normalText = MyLineEdit()  # 使用自定义的类
        self.normalText.setPlaceholderText("请输入或拖入Normal文件")
        normalBtn = QtWidgets.QPushButton("选择贴图")
        normalBtn.clicked.connect(self.getNormalFile)
        normalRow.addWidget(normalLabel)
        normalRow.addWidget(self.normalText)
        normalRow.addWidget(normalBtn)
        layout.addLayout(normalRow)

        # 法线和凹凸节点切换勾选则表示使用aiBump2d，取消勾选则用normalMap
        self.aiBump2dCheck = QtWidgets.QCheckBox("是否切换为aiBump2d节点")
        self.aiBump2dCheck.setChecked(False)  # 默认不勾选
        layout.addWidget(self.aiBump2dCheck)

        # Roughness row
        roughnessRow = QtWidgets.QHBoxLayout()
        roughnessLabel = QtWidgets.QLabel("Roughness:")
        self.roughnessText = MyLineEdit()  # 使用自定义的类
        self.roughnessText.setPlaceholderText("请输入或拖入Roughness文件")
        roughnessBtn = QtWidgets.QPushButton("选择贴图")
        roughnessBtn.clicked.connect(self.getRoughnessFile)
        roughnessRow.addWidget(roughnessLabel)
        roughnessRow.addWidget(self.roughnessText)
        roughnessRow.addWidget(roughnessBtn)
        layout.addLayout(roughnessRow)

        # Metalness row
        metalnessRow = QtWidgets.QHBoxLayout()
        metalnessLabel = QtWidgets.QLabel("Metalness:")
        self.metalnessText = MyLineEdit()  # 使用自定义的类
        self.metalnessText.setPlaceholderText("请输入或拖入Metalness文件")
        metalnessBtn = QtWidgets.QPushButton("选择贴图")
        metalnessBtn.clicked.connect(self.getMetalnessFile)
        metalnessRow.addWidget(metalnessLabel)
        metalnessRow.addWidget(self.metalnessText)
        metalnessRow.addWidget(metalnessBtn)
        layout.addLayout(metalnessRow)

        # Opacity row
        opacityRow = QtWidgets.QHBoxLayout()
        opacityLabel = QtWidgets.QLabel("Opacity:")
        self.opacityText = MyLineEdit()  # 使用自定义的类
        self.opacityText.setPlaceholderText("请输入或拖入Opacity文件")
        opacityBtn = QtWidgets.QPushButton("选择贴图")
        opacityBtn.clicked.connect(self.getOpacityFile)
        opacityRow.addWidget(opacityLabel)
        opacityRow.addWidget(self.opacityText)
        opacityRow.addWidget(opacityBtn)
        layout.addLayout(opacityRow)

        # emission row
        emissionRow = QtWidgets.QHBoxLayout()
        emissionLabel = QtWidgets.QLabel("Emission:")
        self.emissionText = MyLineEdit()  # 使用自定义的类
        self.emissionText.setPlaceholderText("请输入或拖入Emission文件")
        emissionBtn = QtWidgets.QPushButton("选择贴图")
        emissionBtn.clicked.connect(self.getEmissionFile)
        emissionRow.addWidget(emissionLabel)
        emissionRow.addWidget(self.emissionText)
        emissionRow.addWidget(emissionBtn)
        layout.addLayout(emissionRow)

        # OK button
        okBtn = QtWidgets.QPushButton("生成材质球")
        okBtn.clicked.connect(self.createMaterial)
        layout.addWidget(okBtn)

    def getFile(self, textEdit):
        """获取文件路径并显示在文本框中"""
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select file")
        textEdit.setText(fileName)

    def getBaseColorFile(self):
        """获取 Base Color 文件"""
        self.getFile(self.baseColorText)

    def getNormalFile(self):
        """获取 Normal 文件"""
        self.getFile(self.normalText)

    def getRoughnessFile(self):
        """获取 Roughness 文件"""
        self.getFile(self.roughnessText)

    def getMetalnessFile(self):
        """获取 Metalness 文件"""
        self.getFile(self.metalnessText)

    def getOpacityFile(self):
        """获取 opacity 文件"""
        self.getFile(self.opacityText)

    def getEmissionFile(self):
        """获取 emission 文件"""
        self.getFile(self.emissionText)

    def createMaterial(self):


        """创建材质并连接纹理"""
        global metalnessNode
        baseColorFile = self.baseColorText.text()
        normalFile = self.normalText.text()
        roughnessFile = self.roughnessText.text()
        metalnessFile = self.metalnessText.text()
        opacityFile = self.opacityText.text()
        emissionFile = self.emissionText.text()

        missingFiles = []

        name = self.nameText.text()  # 获取文本框的内容
        if not name:  # 如果内容为空
            name = "Material"  # 使用默认的名字
        # 获取当前场景选择的物体
        selection = cmds.ls(selection=True)
        if not selection:
            # 如果未选择任何物体，则创建新的材质球
            aiSurfaceShader = cmds.shadingNode('aiStandardSurface', asShader=True, name=name)
        else:
            # 如果有选择物体，则将新建的材质球指定给该物体
            cmds.select(selection)
            aiSurfaceShader = cmds.shadingNode('aiStandardSurface', asShader=True, name=name)
            cmds.hyperShade(assign=aiSurfaceShader)
        cmds.setAttr(aiSurfaceShader + '.base', 1)
        myPlace2dTexture = cmds.shadingNode('place2dTexture', asUtility=True, name=name + "_UVTile")

        if baseColorFile:
            baseColorNode = cmds.shadingNode('file', isColorManaged=True, name=name + "_baseColor")
            cmds.setAttr(baseColorNode + '.fileTextureName', baseColorFile, type='string')
            cmds.connectAttr(myPlace2dTexture + '.outUV', baseColorNode + '.uvCoord')
            cmds.connectAttr(myPlace2dTexture + '.outUvFilterSize', baseColorNode + '.uvFilterSize')
            cmds.connectAttr(myPlace2dTexture + '.coverage', baseColorNode + '.coverage')
            cmds.connectAttr(myPlace2dTexture + '.translateFrame', baseColorNode + '.translateFrame')
            cmds.connectAttr(myPlace2dTexture + '.rotateFrame', baseColorNode + '.rotateFrame')
            cmds.connectAttr(myPlace2dTexture + '.mirrorU', baseColorNode + '.mirrorU')
            cmds.connectAttr(myPlace2dTexture + '.mirrorV', baseColorNode + '.mirrorV')
            cmds.connectAttr(myPlace2dTexture + '.stagger', baseColorNode + '.stagger')
            cmds.connectAttr(myPlace2dTexture + '.wrapU', baseColorNode + '.wrapU')
            cmds.connectAttr(myPlace2dTexture + '.wrapV', baseColorNode + '.wrapV')
            cmds.connectAttr(myPlace2dTexture + '.repeatUV', baseColorNode + '.repeatUV')
            cmds.connectAttr(myPlace2dTexture + '.vertexUvOne', baseColorNode + '.vertexUvOne')
            cmds.connectAttr(myPlace2dTexture + '.vertexUvTwo', baseColorNode + '.vertexUvTwo')
            cmds.connectAttr(myPlace2dTexture + '.vertexUvThree', baseColorNode + '.vertexUvThree')
            cmds.connectAttr(myPlace2dTexture + '.vertexCameraOne', baseColorNode + '.vertexCameraOne')
            cmds.connectAttr(myPlace2dTexture + '.noiseUV', baseColorNode + '.noiseUV')
            cmds.connectAttr(myPlace2dTexture + '.offset', baseColorNode + '.offset')
            cmds.connectAttr(myPlace2dTexture + '.rotateUV', baseColorNode + '.rotateUV')
            cmds.setAttr(baseColorNode + '.ignoreColorSpaceFileRules', 1)
            if self.udim.isChecked():  # 如果勾选了 udin 复选框则开启多象限
                cmds.setAttr(baseColorNode + '.uvTilingMode', 3)
            else:  # 如果没有勾选 udim 复选框则关闭
                cmds.setAttr(baseColorNode + '.uvTilingMode', 0)

            if self.sRGBCheck.isChecked():  # 如果勾选了sRGB
                cmds.setAttr(baseColorNode + '.colorSpace', 'sRGB', type='string')  # 设置 color space 为 sRGB
            elif self.ACESCheck.isChecked():  # 如果勾选了ACES
                cmds.setAttr(baseColorNode + '.colorSpace', 'Utility - sRGB - Texture',
                             type='string')  # 设置 color space 为 Utility - sRGB - Texturess

            if self.colorCorrectCheck.isChecked() and self.Triplanar.isChecked():
                # 创建 aiColorCorrect 节点
                colorCorrectNode = cmds.shadingNode('aiColorCorrect', asUtility=True, name=name + '_base_ColorCorrect')
                # 创建 aiTriplanar 节点
                bstriplanarNode = cmds.shadingNode('aiTriplanar', asUtility=True, name=name + '_base_Triplanar')

                # 连接节点
                cmds.connectAttr(baseColorNode + '.outColor', colorCorrectNode + '.input')
                cmds.connectAttr(colorCorrectNode + '.outColor', bstriplanarNode + '.input')
                cmds.connectAttr(bstriplanarNode + '.outColor', aiSurfaceShader + '.baseColor')

            elif self.colorCorrectCheck.isChecked():
                # 创建 aiColorCorrect 节点
                colorCorrectNode = cmds.shadingNode('aiColorCorrect', asUtility=True, name=name + '_base_ColorCorrect')

                # 连接节点
                cmds.connectAttr(baseColorNode + '.outColor', colorCorrectNode + '.input')
                cmds.connectAttr(colorCorrectNode + '.outColor', aiSurfaceShader + '.baseColor')

            elif self.Triplanar.isChecked():
                # 创建 aiTriplanar 节点
                bstriplanarNode = cmds.shadingNode('aiTriplanar', asUtility=True, name=name + '_base_Triplanar')

                # 连接节点
                cmds.connectAttr(baseColorNode + '.outColor', bstriplanarNode + '.input')
                cmds.connectAttr(bstriplanarNode + '.outColor', aiSurfaceShader + '.baseColor')

            else:
                # 没有勾选复选框时，直接连接 outColor 到材质的基色
                cmds.connectAttr(baseColorNode + '.outColor', aiSurfaceShader + '.baseColor')


        else:
            missingFiles.append('Base Color')

        if normalFile:
            normalNode = cmds.shadingNode('file', isColorManaged=True, name=name + "_normal")
            cmds.setAttr(normalNode + '.fileTextureName', normalFile, type='string')
            cmds.defaultNavigation(connectToExisting=True, source=myPlace2dTexture, destination=normalNode)
            cmds.setAttr(normalNode + '.ignoreColorSpaceFileRules', 1)
            cmds.setAttr(normalNode + '.alphaIsLuminance', 1)
            if self.udim.isChecked():  # 如果勾选了 udin 复选框则开启多象限
                cmds.setAttr(normalNode + '.uvTilingMode', 3)
            else:  # 如果没有勾选 udim 复选框则关闭
                cmds.setAttr(normalNode + '.uvTilingMode', 0)
            if self.sRGBCheck.isChecked():  # 如果勾选了sRGB
                cmds.setAttr(normalNode + '.colorSpace', 'Raw', type='string')  # 设置 color space 为 Raw
            elif self.ACESCheck.isChecked():  # 如果勾选了ACES
                cmds.setAttr(normalNode + '.colorSpace', 'Utility - Linear - sRGB',
                             type='string')  # 设置 color space 为 Utility - Linear - sRGB

            if self.aiBump2dCheck.isChecked() and self.Triplanar.isChecked():
                bump2dNode = cmds.shadingNode('aiBump2d', asUtility=True, name=name + '_Bump')  # 创建一个 aiBump2d 节点
                notriplanarNode = cmds.shadingNode('aiTriplanar', asUtility=True,
                                                   name=name + '_BumpTrip')  # 创建一个 aiTriplanar 节点
                cmds.connectAttr(bstriplanarNode + '.scale', notriplanarNode + '.scale', force=True)
                cmds.connectAttr(bstriplanarNode + '.rotate', notriplanarNode + '.rotate', force=True)
                cmds.connectAttr(bstriplanarNode + '.offset', notriplanarNode + '.offset', force=True)

                cmds.connectAttr(normalNode + '.outAlpha', bump2dNode + '.bumpMap')  # 连接 outAlpha 到 bumpMap
                cmds.connectAttr(bump2dNode + '.outValue',
                                 notriplanarNode + '.input')  # 连接 aiBump2d 的 outValue 到 aiTriplanar 的 input
                cmds.connectAttr(notriplanarNode + '.outColor',
                                 aiSurfaceShader + '.normalCamera')  # 连接 aiTriplanar 的 outColor 到材质的法线相机

            elif self.aiBump2dCheck.isChecked():
                bump2dNode = cmds.shadingNode('aiBump2d', asUtility=True, name=name + '_Bump')  # 创建一个 aiBump2d 节点

                cmds.connectAttr(normalNode + '.outAlpha', bump2dNode + '.bumpMap')  # 连接 outAlpha 到 bumpMap
                cmds.connectAttr(bump2dNode + '.outValue',
                                 aiSurfaceShader + '.normalCamera')  # 连接 aiBump2d 的 outValue 到材质的法线相机

            elif self.Triplanar.isChecked():
                normalMap = cmds.shadingNode('aiNormalMap', asUtility=True, name=name + '_NormalMap')  # 创建一个 aiNormalMap 节点
                notriplanarNode = cmds.shadingNode('aiTriplanar', asUtility=True, name=name + '_NormalTrip')  # 创建一个 aiTriplanar 节点
                cmds.connectAttr(bstriplanarNode + '.scale', notriplanarNode + '.scale', force=True)
                cmds.connectAttr(bstriplanarNode + '.rotate', notriplanarNode + '.rotate', force=True)
                cmds.connectAttr(bstriplanarNode + '.offset', notriplanarNode + '.offset', force=True)

                cmds.connectAttr(normalNode + '.outColor', normalMap + '.input')  # 连接 outValue 到 aiTriplanar 的 input
                cmds.connectAttr(normalMap + '.outValue', notriplanarNode + '.input')  # 连接 aiTriplanar 的 outColor 到材质的法线相机
                cmds.connectAttr(notriplanarNode + '.outColor',
                                 aiSurfaceShader + '.normalCamera')  # 连接 outValue 到材质的法线相机


            else:
                normalMap = cmds.shadingNode('aiNormalMap', asUtility=True,
                                             name=name + '_NormalMap')  # 创建一个 aiNormalMap 节点
                cmds.connectAttr(normalNode + '.outColor', normalMap + '.input')  # 连接 outColor 到 input
                cmds.connectAttr(normalMap + '.outValue', aiSurfaceShader + '.normalCamera')  # 连接 outValue 到材质的法线相机



        else:
            missingFiles.append('Normal')

        if roughnessFile:
            roughnessNode = cmds.shadingNode('file', isColorManaged=True, name=name + "_roughness")
            cmds.setAttr(roughnessNode + '.fileTextureName', roughnessFile, type='string')
            cmds.defaultNavigation(connectToExisting=True, source=myPlace2dTexture, destination=roughnessNode)

            cmds.setAttr(roughnessNode + '.ignoreColorSpaceFileRules', 1)
            cmds.setAttr(roughnessNode + '.alphaIsLuminance', 1)
            if self.udim.isChecked():  # 如果勾选了 udin 复选框则开启多象限
                cmds.setAttr(roughnessNode + '.uvTilingMode', 3)
            else:  # 如果没有勾选 udim 复选框则关闭
                cmds.setAttr(roughnessNode + '.uvTilingMode', 0)
            if self.sRGBCheck.isChecked():  # 如果勾选了sRGB
                cmds.setAttr(roughnessNode + '.colorSpace', 'Raw', type='string')  # 设置 color space 为 Raw
            elif self.ACESCheck.isChecked():  # 如果勾选了ACES
                cmds.setAttr(roughnessNode + '.colorSpace', 'Utility - Raw',
                             type='string')  # 设置 color space 为 Utility - Raw
            if self.Triplanar.isChecked():
                routriplanarNode = cmds.shadingNode('aiTriplanar', asUtility=True, name=name + '_rouTrip')  # 创建一个 aiTriplanar 节点
                cmds.connectAttr(bstriplanarNode + '.scale', routriplanarNode + '.scale', force=True)
                cmds.connectAttr(bstriplanarNode + '.rotate', routriplanarNode + '.rotate', force=True)
                cmds.connectAttr(bstriplanarNode + '.offset', routriplanarNode + '.offset', force=True)

                cmds.connectAttr(roughnessNode + '.outColor', routriplanarNode + '.input', force=True)
                cmds.connectAttr(routriplanarNode + '.outColorR', aiSurfaceShader + '.specularRoughness', force=True)
            else:
                cmds.connectAttr(roughnessNode + '.outAlpha', aiSurfaceShader + '.specularRoughness', force=True)

        else:
            missingFiles.append('Roughness')

        if metalnessFile:
            metalnessNode = cmds.shadingNode('file', isColorManaged=True, name=name + "_metalness")
            cmds.setAttr(metalnessNode + '.fileTextureName', metalnessFile, type='string')
            # 连接 place2dTexture 节点到文件节点
            cmds.defaultNavigation(connectToExisting=True, source=myPlace2dTexture, destination=metalnessNode)

            cmds.setAttr(metalnessNode + '.ignoreColorSpaceFileRules', 1)
            cmds.setAttr(metalnessNode + '.alphaIsLuminance', 1)
            if self.udim.isChecked():  # 如果勾选了 udin 复选框则开启多象限
                cmds.setAttr(metalnessNode + '.uvTilingMode', 3)
            else:  # 如果没有勾选 udim 复选框则关闭
                cmds.setAttr(metalnessNode + '.uvTilingMode', 0)
            if self.sRGBCheck.isChecked():  # 如果勾选了sRGB
                cmds.setAttr(metalnessNode + '.colorSpace', 'Raw', type='string')  # 设置 color space 为 Raw
            elif self.ACESCheck.isChecked():  # 如果勾选了ACES
                cmds.setAttr(metalnessNode + '.colorSpace', 'Utility - Raw',
                             type='string')  # 设置 color space 为 Utility - Raw
            if self.Triplanar.isChecked():
                mettriplanarNode = cmds.shadingNode('aiTriplanar', asUtility=True, name=name + '_metTrip')  # 创建一个 aiTriplanar 节点
                cmds.connectAttr(bstriplanarNode + '.scale', mettriplanarNode + '.scale', force=True)
                cmds.connectAttr(bstriplanarNode + '.rotate', mettriplanarNode + '.rotate', force=True)
                cmds.connectAttr(bstriplanarNode + '.offset', mettriplanarNode + '.offset', force=True)

                cmds.connectAttr(metalnessNode + '.outColor', mettriplanarNode + '.input', force=True)
                cmds.connectAttr(mettriplanarNode + '.outColorR', aiSurfaceShader + '.metalness', force=True)
            else:
                cmds.connectAttr(metalnessNode + '.outAlpha', aiSurfaceShader + '.metalness', force=True)
        else:
            missingFiles.append('Metalness')

        if opacityFile:
            opacityNode = cmds.shadingNode('file', isColorManaged=True, name=name + "_opacity")
            cmds.setAttr(opacityNode + '.fileTextureName', opacityFile, type='string')
            # 连接 place2dTexture 节点到文件节点
            cmds.defaultNavigation(connectToExisting=True, source=myPlace2dTexture, destination=opacityNode)

            cmds.setAttr(opacityNode + '.ignoreColorSpaceFileRules', 1)
            cmds.setAttr(opacityNode + '.alphaIsLuminance', 1)
            if self.udim.isChecked():  # 如果勾选了 udin 复选框则开启多象限
                cmds.setAttr(opacityNode + '.uvTilingMode', 3)
            else:  # 如果没有勾选 udim 复选框则关闭
                cmds.setAttr(opacityNode + '.uvTilingMode', 0)
            if self.sRGBCheck.isChecked():  # 如果勾选了sRGB
                cmds.setAttr(opacityNode + '.colorSpace', 'Raw', type='string')  # 设置 color space 为 Raw
            elif self.ACESCheck.isChecked():  # 如果勾选了ACES
                cmds.setAttr(opacityNode + '.colorSpace', 'Utility - Raw',
                             type='string')  # 设置 color space 为 Utility - Raw
            if self.Triplanar.isChecked():
                OtriplanarNode = cmds.shadingNode('aiTriplanar', asUtility=True, name=name + '_optTrip')  # 创建一个 aiTriplanar 节点
                cmds.connectAttr(bstriplanarNode + '.scale', OtriplanarNode + '.scale', force=True)
                cmds.connectAttr(bstriplanarNode + '.rotate', OtriplanarNode + '.rotate', force=True)
                cmds.connectAttr(bstriplanarNode + '.offset', OtriplanarNode + '.offset', force=True)

                cmds.connectAttr(opacityNode + '.outColor', OtriplanarNode + '.input', force=True)
                cmds.connectAttr(OtriplanarNode + '.outColor', aiSurfaceShader + '.opacity', force=True)
            else:
                cmds.connectAttr(opacityNode + '.outColor', aiSurfaceShader + '.opacity', force=True)

        else:
            missingFiles.append('Opacity')


        if emissionFile:
            emissionNode = cmds.shadingNode('file', isColorManaged=True, name=name + "_emission")
            cmds.setAttr(emissionNode + '.fileTextureName', emissionFile, type='string')
            # 连接 place2dTexture 节点到文件节点
            cmds.defaultNavigation(connectToExisting=True, source=myPlace2dTexture, destination=emissionNode)

            cmds.setAttr(emissionNode + '.ignoreColorSpaceFileRules', 1)
            if self.udim.isChecked():  # 如果勾选了 udin 复选框则开启多象限
                cmds.setAttr(emissionNode + '.uvTilingMode', 3)
            else:  # 如果没有勾选 udim 复选框则关闭
                cmds.setAttr(emissionNode + '.uvTilingMode', 0)
            if self.sRGBCheck.isChecked():  # 如果勾选了sRGB
                cmds.setAttr(emissionNode + '.colorSpace', 'sRGB', type='string')  # 设置 color space 为 Raw
            elif self.ACESCheck.isChecked():  # 如果勾选了ACES
                cmds.setAttr(emissionNode + '.colorSpace', 'Utility - sRGB - Texture',
                             type='string')  # 设置 color space 为 Utility - Raw
            if self.Triplanar.isChecked():
                EtriplanarNode = cmds.shadingNode('aiTriplanar', asUtility=True, name=name + '_EtTrip')  # 创建一个 aiTriplanar 节点
                cmds.connectAttr(bstriplanarNode + '.scale', EtriplanarNode + '.scale', force=True)
                cmds.connectAttr(bstriplanarNode + '.rotate', EtriplanarNode + '.rotate', force=True)
                cmds.connectAttr(bstriplanarNode + '.offset', EtriplanarNode + '.offset', force=True)

                cmds.connectAttr(emissionNode + '.outColor', EtriplanarNode + '.input', force=True)
                cmds.connectAttr(EtriplanarNode + '.outColor', aiSurfaceShader + '.emissionColor', force=True)
            else:
                cmds.connectAttr(emissionNode + '.outColor', aiSurfaceShader + '.emissionColor', force=True)

        else:
            missingFiles.append('Emission')



        # 如果有选择物体则将新建的材质球指定该物体
        cmds.select(selection)
        cmds.hyperShade(assign=aiSurfaceShader)

        if missingFiles:
            message = '缺少以下贴图文件请检查是否正常:\n'
            for f in missingFiles:
                message += f + '\n'
            QtWidgets.QMessageBox.critical(self, "Error", message)
        else:
            QtWidgets.QMessageBox.information(self, "Success", "材质球创建成功")



        self.close()  # 关闭对话框


def showWindow():
    window = CreateMaterialWindow()
    window.show()

    # 保持对话框或窗口对象的引用
    return window


# 在全局范围内保持对话框或窗口对象的引用
dialog = showWindow()

