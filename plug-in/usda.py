import re
import mayaUsd
import maya.internal.ufeSupport.utils as ufeUtils
from pxr import Usd, Vt,Sdf,UsdGeom


# 设置帧率
fps = 25

# 获取非Maya的选择项
sl = ufeUtils.getNonMayaSelectedItems()
root_shape_name = sl[0].split(",")[0]
root_shape = mayaUsd.lib.GetPrim(root_shape_name)

# 获取USD阶段和根层
stage = root_shape.GetStage()
root_layer = stage.GetRootLayer()
root_prims = root_layer.rootPrims
root_prim_spec = root_prims[0]

print(root_prim_spec)

# 设置帧率
stage.SetFramesPerSecond(fps)
stage.SetTimeCodesPerSecond(fps)

# 获取根原语并设置为默认原语
root_prim = stage.GetPrimAtPath(root_prim_spec.path)
Usd.Stage.SetDefaultPrim(stage, root_prim)

# 导出层内容为字符串
exported_string = stage.GetRootLayer().ExportToString()

# 替换文件头并删除重排序行
first_line = "#usda 1.0"
exported_string = exported_string.replace(exported_string.split("\n")[0], first_line)
reorder_line_pattern = r'reorder rootPrims .*?\n'
exported_string = re.sub(reorder_line_pattern, '', exported_string)
print(exported_string)

# 写入到.usda文件
usd_file_path = "f:/UE4_project/usd_text/testa.usda"
with open(usd_file_path, "w") as usd_file:
    usd_file.write(exported_string)
