# -*- coding: utf-8 -*-
import json
import os
from maya import cmds

def open_folder_dialog():
    dialog = cmds.fileDialog2(fileMode=3)
    if dialog:
        return dialog[0]
    else:
        return None

def create_or_get_json(folder_path):
    json_path = os.path.join(folder_path, 'GPU_project.json')
    if not os.path.exists(json_path):
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)
    return json_path

def modify_json_file(original_file_path, new_json_path):
    with open(original_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['new_json_path'] = new_json_path
    with open(original_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def main():
    original_file_path = "D:\\Cling_toolbox\\json\\gpu_route.json"
    folder_path = open_folder_dialog()
    if folder_path:
        new_json_path = create_or_get_json(folder_path)
        modify_json_file(original_file_path, new_json_path)
        cmds.confirmDialog(title=u"成功", message=u"公共资产路径已设置成功请重启工具架。", button=[u"确定"])
    else:
        cmds.warning("No folder selected.")

main()
