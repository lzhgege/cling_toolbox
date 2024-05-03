# -*- coding: utf-8 -*-
# 作者：cling
# 微信：clingkaka
# 个人主页：www.cg6i.com
# 模型下载：www.cgfml.com
# AI聊天绘画：ai.cgfml.com
# 敲码不易修改搬运请保留以上信息，感谢！！！！！
import os
import shutil
import urllib.request
import zipfile
import json
from PySide2 import QtWidgets

bbh = 3.0
destination_folder = 'D:/Cling_toolbox'
bbh_json_url = "https://tool.cgfml.com/Cling_toolbox_3.0/bbh.json"
download_url = "https://tool.cgfml.com/Cling_toolbox_3.0/Cling_toolbox.zip"
temp_zip_file = os.path.join(destination_folder, "Cling_toolbox.zip")

if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

try:
    url = urllib.request.urlopen(bbh_json_url)
    bbh_json_data = json.loads(url.read())
    if bbh != bbh_json_data["version"]:
        cmds.warning(u"当前版本（{}）最新版本（{}）".format(bbh, bbh_json_data["version"]))

        # 创建简单的对话框
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle(u"更新提示")

        description = bbh_json_data.get("description", "")
        release_date = bbh_json_data.get("release_date", "")
        formatted_description = description.replace("\\n", "\n")
        msgBox.setText(u"当前版本（{}）最新版本（{}）\n描述：{}\n发布日期：{}\n是否更新？".format(bbh, bbh_json_data["version"], formatted_description, release_date))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        choice = msgBox.exec_()

        if choice == QtWidgets.QMessageBox.Yes:
            urllib.request.urlretrieve(download_url, temp_zip_file)
            with zipfile.ZipFile(temp_zip_file, 'r') as zip_ref:
                zip_ref.extractall(destination_folder)

            cmds.confirmDialog(title=u"更新完成", message=u'成功更新，请重启maya，请勿删除 "{}"'.format(destination_folder), button=[u"确定"])
        else:
            print(u"未进行更新操作")
    else:

        cmds.confirmDialog(title=u"更新提醒", message=u"你已经是最新版无需更新。", button=[u"确定"])

except Exception as e:
    print(u'下载和解压文件时发生错误请联系cling: {}'.format(e))
finally:
    if os.path.exists(temp_zip_file):
        os.remove(temp_zip_file)
