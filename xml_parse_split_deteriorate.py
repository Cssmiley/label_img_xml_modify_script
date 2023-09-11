#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 上面兩行是for python2(一定要原封不動放最上面) ,否則遇到中文會跳錯 SyntaxError: Non-ASCII character '\xe4' in file xml_parse_count.py on line 6, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details

"""
複製 .jpg圖片 和輸出 單一劣化 .xml檔 到新建的單一劣化資料夾
前置作業:
- 比對同一張圖片的多重劣化和個單一劣化的 xml 內容結構差異,確認需更改的地方
程式:
- 選取資料夾路徑(GUI或手動填)-手動填
- 遍歷選取資料夾讀取 .xml 檔
- 將劣化類別複製,並寫入到分別的劣化類別 .xml 檔
- 複製.jpg圖片到劣化類別資料夾
- 模組化

使用

安裝套件 : 不需安裝,使用內建lib
將這個 .py 檔放到想篩選圖片的資料夾內
執行 python檔:
> python3 xml_parse_split_deteriorate.py -p "要處理的資料夾路徑"
e.g.  python3 xml_parse_split_deteriorate.py -p D:\labelImg提交檔案\測試xml_parse_split_deteriorate\檔案重複bug測試
> python3 xml_parse_split_deteriorate.py -r "要遞迴處理的資料夾路徑"
e.g.  python3 xml_parse_split_deteriorate.py -r D:\labelImg提交檔案\測試xml_parse_split_deteriorate\檔案重複bug測試
輸出單一劣化資料到對應的資料夾,複製.jpg 圖片檔並抽取單一劣化 .xml 檔進資料夾

注意:
若是若是windows下,指令使用 python xml_parse_split_deteriorate.py -p "D:\labelImg提交檔案\測試\" 
最後的雙引號會被跳脫路徑名會變成多了雙引號==> D:\labelImg提交檔案\測試" 
建議後面不加"\": python xml_parse_split_deteriorate.py -p D:\labelImg提交檔案\測試 
"""
import xml.etree.ElementTree  as ET
import logging
import os, sys
import shutil
import collections
import argparse
from pathlib import Path



# 輸出單一劣化的 .xml
def write_single_deteriorate_xml(tree, root, object_tag, out_xml_path):
# 組合要寫入 xml 的節點    
    # 建立labelImg輸出的 xml 檔的第一個節點 <annotation>
    xml_annotation = ET.Element("annotation")
    _tree = tree
    _root = root
    # 接著貼上上半段所有不是 <object> 的節點
    for child in _root:
        if child.tag == "object":
            continue # 跳過 <object> 節點
        xml_annotation.append(child)
    # 最後再貼上特定的劣化節點    
    find_object = f"object[name='{object_tag}']"
    for xml_object in root.findall(find_object):
        print(f"xml_object: {xml_object}")
        xml_annotation.append(xml_object)
# 將組合好的節點寫入 .xml 檔
    _tree._setroot(xml_annotation) # 將上面組合好的最上層節點 <annotation>設成根節點
    _tree.write(out_xml_path, encoding="UTF-8")
    print(f"write_single_deteriorate_xml({object_tag})") # log down debug message for log file
 
def split_from_folder(folder_path):
    # 遍歷 folder,讀取 xml file
    _folder_path = folder_path
    for _file_name in os.listdir(_folder_path):

        # 讀取檔案,只讀取 xml 檔
        if not _file_name.lower().endswith('.xml'):# 副檔名統一小寫,判斷是不是.xml檔
            continue # 跳過 .xml 以外的檔
        file_path = os.path.join(_folder_path, _file_name)
        # read .xml file
        xml_path = file_path
        tree = ET.parse(xml_path)
        root = tree.getroot()

    # 蒐集 <object> 底下的 <name> tag（也就是這張圖的所有劣化類別名稱),存到字典方便後續操作
        """用 collections.defaultdict 建立預設值為 0 的字典,
        將讀到的<name> 放到字典的 key,<name> 的數量放到字典的 value,
        用來計算單張圖片劣化類別的節點數(也就是一張圖有多少個特定劣化框選數量)"""
        deteriorate = root.findall("./object/name") # 取得所有類別名稱
        det = collections.defaultdict(int) 
        for name in deteriorate:
            det[name.text] += 1
        print(f"_file_name: {_file_name} \ndet: {det}")

    # 無劣化的 xml 檔,增加標註"other"依據劣化輸出 xml
        if not det:
            print(f"not det: {_file_name }") 
            det["other"] += 1 
        for key in det.keys():
        # deteriorate_folder_path,用在輸出各劣化類別資料夾路徑
            # deteriorate_folder_path = os.path.join(_folder_path ,key) 
            deteriorate_folder_path = os.path.join(_folder_path,key)
            # output_xml_path,用在輸出的 .xml檔完整路徑
            output_xml_path = os.path.join(deteriorate_folder_path, _file_name)
        
    # 根據字典的keys(),建立資料夾並輸出新.xml檔
            
            # 檢查單一劣化資料夾是否已經存在,若不存在就新增資料夾
            if not os.path.exists(deteriorate_folder_path):
                os.makedirs(deteriorate_folder_path)
            # 檢查圖片是否存在,若不存在就複製 .jpg 檔到新資料夾內
            #print(f"type(_file_name): {type(_file_name)}") # 檢查這裡的str物件和 split_recursive_folder(folder_path) 使用的pathlib路徑物件的不同
            # 處理相對應的 .jpg 檔,若同檔名的.jpg檔不存在則會跳出FileNotFoundError
            jpg_path = os.path.join(_folder_path, _file_name.replace(".xml",".jpg"))
            jpg_copy_path = os.path.join(deteriorate_folder_path, _file_name.replace(".xml",".jpg"))
            try:
                if not os.path.exists(jpg_copy_path):
                    shutil.copy(jpg_path, jpg_copy_path)
            except Exception as err:
                raise Exception (str(err)) # 找不到相對應的 .jpg 檔
            # 寫入單一劣化 .xml 檔到單一劣化資料夾
            write_single_deteriorate_xml(tree, root, key, output_xml_path)
            
def split_recursive_folder(folder_path): # 遞迴處理使用Pathlib,而路徑會是 Pathlib.PosixPath 物件 和一般使用str物件表示路徑的處理不同
    _folder_path = folder_path
    for _subitem in sorted(Path(_folder_path).iterdir()): # _folder_path 不在是 str 物件
        if _subitem.is_dir():
            print(f"dir: {_subitem}")
            split_recursive_folder(_subitem)
        
        if _subitem.is_file():
            print(f"file: {_subitem}")   
            
        # 讀取檔案,只讀取 xml 檔
            _file_name = os.path.basename(_subitem) 
            #print(f"XXXXXXX_subitem: {_file_name}")
            if not _file_name.lower().endswith('.xml'): 
            #if not _file_name.name.lower().endswith('.xml'): # 副檔名統一小寫後做判斷 xxx.name.lower() 是因為Pathlib不能直接xxx.lower() 跳出AttributeError: 'PosixPath' object has no attribute 'lower'
                continue # 跳過 .xml 以外的檔
            file_path = os.path.join(_folder_path, _file_name)
            # read .xml file
            xml_path = file_path
            tree = ET.parse(xml_path)
            root = tree.getroot()

        # 蒐集 <object> 底下的 <name> tag（也就是這張圖的所有劣化類別名稱),存到字典方便後續操作
            """用 collections.defaultdict 建立預設值為 0 的字典,
            將讀到的<name> 放到字典的 key,<name> 的數量放到字典的 value,
            用來計算單張圖片劣化類別的節點數(也就是一張圖有多少個特定劣化框選數量)"""
            deteriorate = root.findall("./object/name") # 取得所有類別名稱
            det = collections.defaultdict(int) 
            for name in deteriorate:
                det[name.text] += 1
            print(f"_file_name: {_file_name} \ndet: {det}")

         # 無劣化的 xml 檔,增加標註"other"依據劣化輸出 xml
            if not det:
                print(f"not det: {_file_name }") 
                det["other"] += 1 
                
            for key in det.keys():
            # deteriorate_folder_path,用在輸出各劣化類別資料夾路徑
                # deteriorate_folder_path = os.path.join(_folder_path, key) 
                deteriorate_folder_path = os.path.join(".", key) # 遞迴處理後統一放同一個資料夾"."處裡
                # output_xml_path,用在輸出的 .xml檔完整路徑
                output_xml_path = os.path.join(deteriorate_folder_path, _file_name)
            
        # 根據字典的keys(),建立資料夾並輸出新.xml檔
                
                # 檢查單一劣化資料夾是否已經存在,若不存在就新增資料夾
                if not os.path.exists(deteriorate_folder_path):
                    os.makedirs(deteriorate_folder_path)
                # 檢查圖片是否存在,若不存在就複製 .jpg 檔到新資料夾內
                #print(f"type(_file_name): {type(_file_name)}") # 檢查這裡的pathlib 和 split_from_folder(folder_path) 使用的str物件的不同
                #print(f"str(_file_name):{str(_file_name)}, type(_file_name): {type(str(_file_name))}")
                # 處理相對應的 .jpg 檔,若同檔名的.jpg檔不存在則會跳出FileNotFoundError
                jpg_path = os.path.join(_folder_path, str(_file_name).replace(".xml", ".jpg"))
                jpg_copy_path = os.path.join(deteriorate_folder_path,  str(_file_name).replace(".xml", ".jpg"))
                
                if not os.path.exists(jpg_copy_path):
                    try:
                        shutil.copy(jpg_path, jpg_copy_path)
                    except Exception as err:
                        raise Exception(str(err))         
                else:
                # recusive 需要處理多個資料夾內的檔名可能重複的問題, 目前是加上重複檔案的資料夾名稱
                    duplicate_suffix = str(_folder_path).split(os.path.sep)[-1] #_folder_path 已被 Path()更改
                    jpg_duplicate_path = os.path.join(deteriorate_folder_path, duplicate_suffix +"_"+str(_file_name).replace(".xml", ".jpg"))
                    shutil.copy(jpg_path, jpg_duplicate_path)
                
                # 寫入單一劣化 .xml 檔到單一劣化資料夾
                if not os.path.exists(output_xml_path):
                    write_single_deteriorate_xml(tree, root, key, output_xml_path)
                else:
                # recusive 需要處理多個資料夾內的檔名可能重複的問題, 目前是加上重複檔案的資料夾名稱
                    output_xml_duplicate_path = os.path.join(deteriorate_folder_path, duplicate_suffix + "_" + str(_file_name))
                    write_single_deteriorate_xml(tree, root, key, output_xml_duplicate_path)
                
def main():
    # debug message in log file
    logging.basicConfig(filename="log__file_name.txt", 
                        level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    # 定義輸入參數
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group() # 互斥的選項
    group.add_argument("-p",
                        "--path",
                        nargs=1, 
                        type=str,
                        default=".", # 不指定 -p 參數時,預設args.path資料夾為"."
                        help="這是路徑--path,未指定則預設此 .py 檔所在資料夾")
    group.add_argument("-r",
                        "--recursive",
                        nargs = 1,
                        type = str,
                        help = "這是遞迴拋指定資料夾路徑")
    args = parser.parse_args()
    if (args.path):
        folder_path =  args.path[0]
        print(f"args.path folder_path: {folder_path}")
        
    if (args.recursive):
        recursive_folder_path = args.recursive[0]
        print(f"args.recursive folder_path: {recursive_folder_path}")
        print(f"遞迴資料夾: {args.recursive}")

    print(f"第 1 個引數：{args.path},type={type(args.path)}")
    print(f"第 2 個引數: {args.recursive}, type={type(args.recursive)}")
    
# 一般資料夾計算數量
    if (not (args.recursive)) and(args.path): # 因為args.path 有設定default值,只有指定-r時args.path會有預設值"."產生,條件需加上 not(args.recursive)
        split_from_folder(folder_path)
        
    #遞迴計算
    if (args.recursive):
        split_recursive_folder(recursive_folder_path)
    
if __name__=="__main__":
    main()
