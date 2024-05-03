# -*- coding: utf-8 -*-
# 作者：cling
# 微信：clingkaka
# 个人主页：www.cg6i.com
# 模型下载：www.cgfml.com
# AI聊天绘画：ai.cgfml.com
# 敲码不易修改搬运请保留以上信息，感谢！！！！！

import maya.cmds as cmds
import os
import subprocess


def get_available_drives():
    """获取当前系统中已挂载的磁盘驱动器字母"""
    if os.name == 'nt':  # Windows
        return [chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":\\")]
    else:
        return []


def create_and_map_folder(selectedDrive, folderName, newDriveLetter):
    """在选定的磁盘上创建一个文件夹，并将其映射为新的磁盘驱动器"""
    folderPath = os.path.join(selectedDrive, folderName)
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
        print("Folder created successfully: {}".format(folderPath))
    else:
        print("Folder already exists: {}".format(folderPath))

    try:
        subprocess.check_call(['subst', newDriveLetter + ':', folderPath])
        print("{} has been mapped as a new drive: {}".format(folderPath, newDriveLetter))
        create_startup_script(newDriveLetter, folderPath)  # 调用创建启动脚本的函数
    except subprocess.CalledProcessError as e:
        print("Failed to map the folder as a drive: {}".format(e))


def create_startup_script(newDriveLetter, folderPath):
    """创建一个批处理脚本，并将其放在启动文件夹中，以便在每次启动时自动映射驱动器"""
    script_content = (
        "@echo off\n"
        "if not exist \"{folderPath}\\\" (\n"
        "    echo Target folder does not exist: {folderPath}\n"
        "    del \"%~f0\"\n"
        "    exit /b\n"
        ")\n"
        "subst {newDriveLetter}: \"{folderPath}\"\n".format(folderPath=folderPath, newDriveLetter=newDriveLetter)
    )
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    script_path = os.path.join(startup_folder, "map_{0}_drive.bat".format(newDriveLetter))

    with open(script_path, 'w') as script_file:
        script_file.write(script_content)
    print("Startup script created: {0}".format(script_path))


def create_map_folder_ui():
    """创建一个UI窗口，用于选择磁盘，输入文件夹名，和新的磁盘驱动器字母"""
    if cmds.window("createMapFolderUI", exists=True):
        cmds.deleteUI("createMapFolderUI", window=True)

    window = cmds.window("createMapFolderUI", title=u"映射新磁盘", widthHeight=(300, 150))
    cmds.columnLayout(adjustableColumn=True)
    available_drives = get_available_drives()
    selectedDrive = cmds.optionMenu(label=u"本地磁盘")
    for drive in available_drives:
        cmds.menuItem(label=drive)
    folderName = cmds.textFieldGrp(label=u"新建文件夹", placeholderText=u"输入名称，会在你选择得磁盘中创建")
    newDriveLetter = cmds.textFieldGrp(label=u"新的磁盘", placeholderText=u"输入磁盘号 (e.g., Z)")

    cmds.button(label=u"映射新磁盘",
                command=lambda _:
                create_and_map_folder(cmds.optionMenu(selectedDrive, query=True, value=True),
                                      cmds.textFieldGrp(folderName, query=True, text=True),
                                      cmds.textFieldGrp(newDriveLetter, query=True, text=True)))

    wenben = cmds.text(label=u"")
    wenben = cmds.text(label=u"说明：在所选择得本地磁盘中新建一个文件夹，")
    wenben = cmds.text(label=u"并将该文件夹映射为一个新得磁盘。")
    wenben = cmds.text(label=u"注意：新磁盘的磁盘容量是读取原磁盘的！！")
    wenben = cmds.text(label=u"注意：杀毒软件会误报错吴，请关闭或者允许创建bat")
    wenben = cmds.text(label=u"删除磁盘：删除新建的文件夹者删除磁盘，重启电脑生效")
    cmds.showWindow(window)


create_map_folder_ui()
