# -*- coding: utf-8 -*-
# 作者：cling
# 微信：clingkaka
# 个人主页：www.cg6i.com
# 模型下载：www.cgfml.com
# AI聊天绘画：ai.cgfml.com
# 敲码不易修改搬运请保留以上信息，感谢！！！！！
import os
import sys

sys.path.append('D:\\cling_toolbox\\external_library')

from git import Repo
from maya import cmds


def pull_updates(repo):
    # 从远程仓库拉取更新
    origin = repo.remotes.origin
    origin.pull()
    # 更新成功后的确认对话框
    cmds.confirmDialog(title='Update Successful',
                       message=u'更新已完成，请重启工具架享用！',
                       button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK')
    # 关闭窗口
    cmds.deleteUI('UpdateWindow', window=True)


def check_for_updates(repo_path, remote_url):
    if not os.path.exists(repo_path):
        # 如果本地仓库不存在，就克隆远程仓库
        Repo.clone_from(remote_url, repo_path)

    repo = Repo(repo_path)
    origin = repo.remotes.origin

    # 获取当前的commit
    current_commit = repo.head.commit

    # 从远程仓库获取最新的信息
    origin.fetch()

    # 获取最新的commit
    latest_commit = origin.refs.master.commit

    # 获取两个commit之间的差异
    diffs = current_commit.diff(latest_commit)

    if not diffs:
        # 如果没有差异，说明已经是最新版本
        cmds.confirmDialog(title='No Updates',
                           message=u'当前已经是最新版啦！',
                           button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK')
    else:
        # 如果有差异，说明有更新
        def update_dialog():
            cmds.window('UpdateWindow', title='Update Available', widthHeight=(200, 60))
            cmds.columnLayout(adjustableColumn=True)
            cmds.text(label='Update Available', align='center')
            cmds.text(label='Latest commit message:', align='left')
            cmds.text(label=latest_commit.message, align='left')
            cmds.button(label='Update', command=lambda *args: pull_updates(repo))
            cmds.showWindow()

        update_dialog()


check_for_updates('D:\\cling_toolbox', 'https://gitee.com/one-finger-shenman_0/cling_toolbox.git')
