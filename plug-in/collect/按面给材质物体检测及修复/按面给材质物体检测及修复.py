# -*- coding: utf-8 -*-
import sys


plug_folder = r'D:/Cling_toolbox/plug-in/collect/按面给材质物体检测及修复/scripts'
if plug_folder not in sys.path:
    sys.path.append(plug_folder)

from checkAssignFaceShader import *
from checkAssignFaceShaderObj import *


objShaderIsBadUI()
