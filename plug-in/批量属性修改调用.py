#  -*- coding: utf-8 -*-
import sys
import os
import maya.cmds as cmds
import maya.utils as utils
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.mel as mel


plug = r'Z:/Share/tcl0626/Maya_toolbox/plug-in'
if plug not in sys.path:
    sys.path.append(plug)

import attribute

attribute.ParameterEditor()