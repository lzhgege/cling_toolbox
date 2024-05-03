# -*- coding: utf-8 -*-
# 作者：cling
# 微信：clingkaka
# 个人主页：www.cg6i.com
# 模型下载：www.cgfml.com
# AI聊天绘画：ai.cgfml.com
# 敲码不易修改搬运请保留以上信息，感谢！！！！！
import json
import os
import sys
from PySide2.QtWidgets import QApplication, QFileDialog
import maya.cmds as cmds

# 在Maya中指定使用UTF-8编码
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

def update_json_path(new_path):
    json_file_path = 'D:/Cling_toolbox/json/Material_library.json'  # 指定JSON文件路径
    if not os.path.exists(os.path.dirname(json_file_path)):
        os.makedirs(os.path.dirname(json_file_path))  # 确保文件夹存在，不存在则创建

    data = {}
    if os.path.isfile(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

    data['MATERIAL_LIBRARY_PATH'] = new_path

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

    cmds.warning(u'路径已更新为: ' + new_path + u'请重启工具架')

def select_folder_path():
    folder_path = QFileDialog.getExistingDirectory(None, u"选择文件夹路径")
    if folder_path:
        update_json_path(folder_path)

if __name__ == "__main__":
    select_folder_path()

