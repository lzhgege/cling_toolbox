# -*- coding: utf-8 -*-
import io
import json
import os
import sys
class JsonHelper:
    def load_json(self,path):
        """[载入json]

        Args:
            file_name ([str]): [路径文件名]

        Returns:
            [str]: [json文本]
        """        
        if not os.path.exists(path):
            return None
            
        try:    
            with io.open(path,'r',encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
            
    def write_json(self,path,json_obj):
        """[写入json]

        Args:
            json_obj ([str]): [json_str文本]
            file_name ([str]): [文件名]
        """        
        with io.open(path,'w',encoding='utf-8') as f:
            if sys.version_info[0] == 2:
                f.write(unicode(json.dumps(json_obj,ensure_ascii=False,indent=4)))
            elif sys.version_info[0] > 2:    
                f.write(str(json.dumps(json_obj,ensure_ascii=False,indent=4)))