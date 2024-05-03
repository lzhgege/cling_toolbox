# -*- coding: utf-8 -*-
import sys

plug_folder = r'D:/Cling_toolbox/scripts'
if plug_folder not in sys.path:
    sys.path.append(plug_folder)

from MayaDynamicRope_Tool import *

MayaDynamicRope_Tool()


