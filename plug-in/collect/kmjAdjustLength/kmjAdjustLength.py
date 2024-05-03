# -*- coding: utf-8 -*-
###################################################
"""
■概要
kmjAdjustLength
・複数のエッジを任意の長さに設定することができます
・通常はエッジの中心を基準にしますが、片側の頂点をロックすることもできます

■実行方法
kmjAdjustLength.pyファイルをスクリプトフォルダにコピーして、スクリプトエディターに下記を入力して実行します。
###ここから
import kmjAdjustLength
kmjAdjustLength.main()
###ここまで

■マニュアル
Get Length　選択したエッジから長さを取得します。複数選択した場合平均の長さが入力されます
Add Vertex　固定したい頂点をリストに追加します。無い場合はエッジの中心からスケーリングされます
Clear　リストをクリアします
Preserve UVs　スケーリングの際UVを保持します

■注意事項
・直列のエッジに対しては上手く動作しません


■更新履歴
・2020/02/17　作成

■製作者
作成者：kmj
URL：https://seesaawiki.jp/realtime3dcg/
"""
###################################################

import maya.cmds as cmds

class KMJ_AdjustLength(object):
    def __init__(self):
        self.window = 'kmjAdjustLength'
        self.title = 'kmjAdjustLength'
        self.size = (360,380)

    def create(self):
        if cmds.window('kmjAdjustLength', exists=True):
            cmds.deleteUI('kmjAdjustLength', window=True)
        self.window = cmds.window(
            self.window,
            t=self.title,
            widthHeight=self.size
        )
        self.layout()
        cmds.showWindow()

    def layout(self):
        self.formLayout01 = cmds.formLayout(nd=100)
        self.description01 = cmds.text(l='Length from an edge (multiple selection : average)', al='left')
        self.buttonGetLength = cmds.button(l='Get Length', c=self.getLengthCmd)
        self.length_val = cmds.floatField(v=1.0)
        self.separator01 = cmds.separator(st='in')
        self.description02 = cmds.text(l='Locking vertices list', al='left')
        self.buttonAddVertex = cmds.button(l='Add Vertex', c=self.addVertexCmd)
        self.buttonClearVertex = cmds.button(l='Clear', c=self.clearListCmd)
        self.lockVertexList = cmds.textScrollList(
            numberOfRows=6,
            allowMultiSelection=True
        )
        cmds.textScrollList(
            self.lockVertexList,
            edit=True,
            deleteKeyCommand=self.removeItemCmd,
            selectCommand=self.selectItem
        )
        self.checkPreserveUV = cmds.checkBox(l='Preserve UVs')
        self.buttonSet = cmds.button(l='Set Length', c=self.setLengthCmd)
        self.buttonClose = cmds.button(l='Close', c=('cmds.deleteUI("' + self.window + '")'))

        cmds.formLayout(self.formLayout01, edit=True,\
            attachPosition=(
                (self.description01, 'top', 5,0),\
                (self.description01, 'left', 5,0),\
                (self.description01, 'bottom', 0,10),\
                (self.description01, 'right', 5,100),\

                (self.buttonGetLength, 'top', 5,10),\
                (self.buttonGetLength, 'left', 5,0),\
                (self.buttonGetLength, 'bottom', 0,20),\
                (self.buttonGetLength, 'right', 5,50),\

                (self.length_val, 'top', 5,10),\
                (self.length_val, 'left', 5,50),\
                (self.length_val, 'bottom', 0,20),\
                (self.length_val, 'right', 5,100),\

                (self.separator01, 'top', 2,20),\
                (self.separator01, 'left', 5,0),\
                (self.separator01, 'bottom', 2,25),\
                (self.separator01, 'right', 5,100),\

                (self.description02, 'top', 0,22),\
                (self.description02, 'left', 5,0),\
                (self.description02, 'bottom', 0,30),\
                (self.description02, 'right', 5,100),\

                (self.buttonAddVertex, 'top', 5,30),\
                (self.buttonAddVertex, 'left', 5,0),\
                (self.buttonAddVertex, 'bottom', 5,40),\
                (self.buttonAddVertex, 'right', 5,50),\

                (self.buttonClearVertex, 'top', 5,40),\
                (self.buttonClearVertex, 'left', 5,0),\
                (self.buttonClearVertex, 'bottom', 5,50),\
                (self.buttonClearVertex, 'right', 5,50),\

                (self.lockVertexList, 'top', 5,30),\
                (self.lockVertexList, 'left', 5,50),\
                (self.lockVertexList, 'bottom', 5,60),\
                (self.lockVertexList, 'right', 5,100),\

                (self.checkPreserveUV, 'top', 5,55),\
                (self.checkPreserveUV, 'left', 5,0),\
                (self.checkPreserveUV, 'bottom', 5,65),\
                (self.checkPreserveUV, 'right', 5,100),\

                (self.buttonSet, 'top', 5,70),\
                (self.buttonSet, 'left', 20,0),\
                (self.buttonSet, 'bottom', 5,85),\
                (self.buttonSet, 'right', 20,100),\

                (self.buttonClose, 'top', 5,90),\
                (self.buttonClose, 'left', 5,0),\
                (self.buttonClose, 'bottom', 5,100),\
                (self.buttonClose, 'right', 5,100)
            )
        )

    # エッジの長さを取得
    def getLengthCmd(self, *args):
        sel_edges = cmds.filterExpand(sm=32)
        if sel_edges is not None:
            length_list = []
            for sel_edge in sel_edges:
                length_list.append(cmds.arclen(sel_edge))
            ave_length = sum(length_list) / len(length_list)    # 長さの平均値を計算
            cmds.floatField(self.length_val, v=ave_length, e=True)
            print(cmds.floatField(self.length_val, q=True, v=True)),
        else:
            cmds.error("Please select an edge.")

    # エッジの長さを適用実行部
    def setLengthCmd(self, *args):
        all_lock_vertices = self.getAllItems(self.lockVertexList)
        puv_value = cmds.checkBox(self.checkPreserveUV, q=True, v=True)
        sel_edges = cmds.filterExpand(sm=32)
        source_length = cmds.floatField(self.length_val, q=True, v=True)
        symmetry_value = cmds.symmetricModelling(q=True, s=True)    # シンメトリがONだとおかしくなるので
        error_edges = []
        for sel_edge in sel_edges:
            cmds.symmetricModelling(e=True, s=False)    # いったんシンメトリOFF
            target_length = cmds.arclen(sel_edge)
            scale_val = source_length / target_length
            cmds.select(cl=True)
            cmds.select(sel_edge)
            if all_lock_vertices is not None:    # ロックする頂点があったらピボット変更
                inc_vertices = cmds.ls(cmds.polyListComponentConversion(sel_edge, tv=True), fl=True)
                print(inc_vertices)
                locked_vertex = self.lockedVertex(inc_vertices, all_lock_vertices)
                print(locked_vertex),
                if len(locked_vertex) == 1:    # ロックする頂点の一致が一つだけならピボットに設定
                    pivot_pos = cmds.pointPosition(locked_vertex)
                    cmds.scale(1, scale_val, 1, cs=True, a=True, p=pivot_pos, puv=puv_value)
                elif len(locked_vertex) >= 2:    # 両側がロックされた頂点ならエラー
                    error_edges.append(sel_edge)
                else:
                    cmds.scale(1, scale_val, 1, cs=True, a=True, puv=puv_value)
            else:
                cmds.scale(1, scale_val, 1, cs=True, a=True, puv=puv_value)
        if len(error_edges) >= 1:    # エラーエッジがあればワーニング
            cmds.select(cl=True)
            cmds.select(error_edges)
            cmds.symmetricModelling(e=True, s=symmetry_value)    # シンメトリ戻す
            cmds.warning("Both vertices are locked.")
        else:
            cmds.select(cl=True)
            cmds.select(sel_edges)
            cmds.symmetricModelling(e=True, s=symmetry_value)    # シンメトリ戻す
            print(source_length),

    # ロックされた頂点との一致を確認
    def lockedVertex(self, inc_vertices, all_lock_vertices, *args):
        match_vertices = []
        for inc_vertex in inc_vertices:
            if inc_vertex not in all_lock_vertices:
                continue
            else:
                match_vertices.append(inc_vertex)
        return match_vertices

    # ロックする頂点の追加ボタン
    def addVertexCmd(self, *args):
        allItems = self.getAllItems(self.lockVertexList)
        sel = cmds.ls(os=True, fl=True)
        sel_vertices = cmds.ls(cmds.polyListComponentConversion(sel, tv=True), fl=True)
        cmds.select(sel_vertices)
        if sel_vertices is not None:
            if allItems is not None:
                for sel_vertex in sel_vertices:
                    if sel_vertex not in allItems:
                        cmds.textScrollList(self.lockVertexList, e=True, a=sel_vertex)
            else:
                cmds.textScrollList(self.lockVertexList, e=True, a=sel_vertices)
        else:
            cmds.error("Please select vertices.")

    # selectCommand：選択アイテムの実体を選択
    def selectItem(self, *args):
        selItem = cmds.textScrollList(self.lockVertexList, q=True, selectItem=True)
        cmds.select(cl=True)
        cmds.select(selItem)

    # Clear：リストをクリア
    def clearListCmd(self, *args):
        cmds.textScrollList(self.lockVertexList, edit=True, removeAll=True)

    # Remove from List：選択アイテムをリストから削除
    def removeItemCmd(self, *args):
        selItem = cmds.textScrollList(self.lockVertexList, q=True, selectItem=True)
        if selItem is not None:
            cmds.textScrollList(self.lockVertexList, edit=True, removeItem=selItem)

    # リスト上のアイテムを全て取得
    def getAllItems(self, *args):
        allItems = cmds.textScrollList(self.lockVertexList, q=True, allItems=True)
        return allItems

def main():
    kmjAdjustLengthWindow = KMJ_AdjustLength()
    kmjAdjustLengthWindow.create()
main()