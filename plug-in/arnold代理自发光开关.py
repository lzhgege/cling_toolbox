# -*- coding: utf-8 -*-
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore

class SetProxyEmissionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SetProxyEmissionDialog, self).__init__(parent)
        
        # Create UI elements
        self.emission_label = QtWidgets.QLabel("Emission Intensity:")
        self.emission_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.emission_slider.setRange(0, 100)
        self.emission_slider.setValue(50)
        self.emission_textbox = QtWidgets.QLineEdit(str(self.emission_slider.value() / 100.0))
        self.ok_button = QtWidgets.QPushButton("OK")
        
        # Connect signals and slots
        self.emission_slider.valueChanged.connect(self.update_emission_textbox)
        self.emission_textbox.editingFinished.connect(self.update_emission_slider)
        self.ok_button.clicked.connect(self.accept)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.emission_label)
        layout.addWidget(self.emission_slider)
        layout.addWidget(self.emission_textbox)
        layout.addWidget(self.ok_button)
        
        # Set dialog properties
        self.setLayout(layout)
        self.setWindowTitle("Set Proxy Emission")
    
    def update_emission_textbox(self, value):
        self.emission_textbox.setText(str(value / 100.0))
    
    def update_emission_slider(self):
        value = float(self.emission_textbox.text())
        self.emission_slider.setValue(int(value * 100))

# Create dialog instance and show it
dialog = SetProxyEmissionDialog()
result = dialog.exec_()

if result == QtWidgets.QDialog.Accepted:
    # Get selected Arnold proxies
    proxies = cmds.ls(sl=True, type="aiStandIn")
    
    # Loop through proxies and set emission intensity
    for proxy in proxies:
        # Check if proxy has an emissive material connected
        materials = cmds.listConnections(proxy, type="aiStandard")
        if materials:
            # Set emission intensity of the connected material
            cmds.setAttr(materials[0] + ".emission", dialog.emission_slider.value() / 100.0)
        else:
            # Set emission intensity of the proxy directly
            cmds.setAttr(proxy + ".overrideShaders", 1)
            cmds.setAttr(proxy + ".overrideShaderEmission", dialog.emission_slider.value() / 100.0)