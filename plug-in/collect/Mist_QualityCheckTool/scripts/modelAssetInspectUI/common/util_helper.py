# -*- coding: utf-8 -*-

import io
import os
import sys
import json
class UtilJsonHelper:
    def __init__(self,path):
        self.path=path
    def load_json(self):
        if not os.path.exists(self.path):
            return dict()
        try:
            with io.open(self.path,'r',encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
            
    def write_json(self,json_obj):
        with io.open(self.path,'w',encoding='utf-8') as f:
            # f.write(unicode(json.dumps(json_obj,ensure_ascii=False,indent=4)))
            # f.write(str(json.dumps(json_obj,ensure_ascii=False,indent=4)))
            if sys.version_info[0] == 2:
                f.write(unicode(json.dumps(json_obj,ensure_ascii=False,indent=4)))
            elif sys.version_info[0] > 2:    
                f.write(str(json.dumps(json_obj,ensure_ascii=False,indent=4)))

class UtilFileHelper:
    @staticmethod
    def get_file_name_without_ext(path):
        """取没有扩展的文件名

        Args:
            path ([type]): [description]
        """    
        file_name=os.path.basename(path)
        file_name = file_name.split('.')[0]
        return file_name
