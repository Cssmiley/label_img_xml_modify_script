#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 上面兩行是for python2(一定要原封不動放最上面) ,否則遇到中文會跳錯 SyntaxError: Non-ASCII character '\xe4' in file xml_parse_count.py on line 6, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details
"""
計算劣化數量
    - 選取資料夾路徑(GUI或手動填)-手動填
    - 遍歷選取資料夾讀取 .xml 檔
    - 列出該張圖片的所有劣化分類
    - 計算各項劣化圖片總數量
    

    ## 使用
    - 安裝套件 : 不需安裝,使用內建lib
    - 執行 python檔: 
    `> python3 xml_parse_count_csv.py -p "要處理的資料夾路徑"`
    `> python3 xml_parse_count_csv.py -p D:\labelImg提交檔案\測試
    `> python3 xml_parse_count_csv.py -r "要處理的遞迴資料夾路徑"`
    `> python3 xml_parse_count_csv.py -r D:\labelImg提交檔案\`
    - 印出總數及各劣化數量如下範例:
    `Total xml : 6, defaultdict(<class 'int'>, {'crack_00': 3, 'rusty_water': 1, 'spalling': 4, 'crack_AC': 1, 'crack': 1, 'corrosion': 1})`

"""
import csv
import os
import platform
import subprocess
import xml.etree.ElementTree as ET
import collections
import sys
import re
import argparse
from pathlib import Path

count_xml = 0 # 用於計算總xml數(若每張都有輸出xml即是總張數)
count_det = collections.defaultdict(int) # 用於計算圖片個劣化類別總數
#deprecated
#count_2000 = 0 # 用於計算2000張內不包含裂縫和無劣化的張數

recursive_count={}
# 計算 xml 數,劣化數
count_results = {}

def count_file_deteriorate(_file_path):
    # 用於計算總xml數(若每張都有輸出xml即是總張數)
    global count_xml
    
    _file_name = os.path.basename(_file_path)

    if _file_name.endswith(".xml"): # 跳過 .xml 以外的檔
        count_xml += 1 # 計算 xml 數
        # 從檔案載入並解析 XML 資料
        tree = ET.parse(_file_path)
        root = tree.getroot()
        """尋找 XML 節點"""
        # 搜尋所有子節點
        # 用 Pythoninc 的 collections.defaultdict取代,計算單張圖片劣化類別
        deteriorate = root.findall("./object/name")
        det = collections.defaultdict(int)
        for name in deteriorate:
            det[name.text] += 1
        # 無劣化以 "other" 代表
        if not det:
            print(f"not det: {_file_name }") 
            det["other"] += 1 
        print(det) # 單張的所有劣化及數量
        print(f"det.keys: {det.keys()}, file_path : {_file_path }")
        # 計算各圖片劣化類別總數
        for k in det.keys():
            count_det[k] += 1
     
    count_xml_det = {"count_det":count_det,
                     "count_xml":count_xml }
    
    return count_xml_det


# 一般資料夾計算
def count_folder(_folder):
    
    for _file in os.listdir(_folder):
        _file_path = os.path.join(_folder, _file) 
        folder_count = count_file_deteriorate(_file_path)
    print(f"folder_count : {folder_count}")
    return folder_count

# 遞迴資料夾計算
def count_recursive_folder(_folder): # 遞迴處理使用Pathlib,而路徑會是 Pathlib.PosixPath 物件 和一般使用str物件表示路徑的處理不同
    global recursive_count
    for _subitem in sorted(Path(_folder).iterdir()):
        
        if _subitem.is_dir():
            print(f"dir: {_subitem}")
            count_recursive_folder(_subitem)
        
        if _subitem.is_file():
            print(f"file: {_subitem}")
        
            _file = _subitem 
            root = _file.parent 

            print(f"root: {root}")
            _file_name = str(_file).lower() # 副檔名統一小寫
            print(f"file_name : {_file_name }")
            _file_path = Path(_file_name )
            recursive_count = count_file_deteriorate(_file_path)
    
        print(f"_subitem: {_subitem}")
    return recursive_count

def main():
   # 劣化標註列表
    """
    # deprecated
    det_list = ["crack", 
                "spalling",
                "efflorescence",
                "corrosion",
                "water_gain",
                "rusty_water"]
    """
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

    # 用在 python xml_parse_count.py "指定資料夾"
    # 若存在 sys.argv[1] 就用來當路徑,否則就用.py 檔所在資料夾當路徑
    """
    # deprecated 不要和Argparse混用
    try :
        fn = sys.argv[1]
    except:
        fn = os.path.abspath('.')
        
    print(fn)
    print(os.path.isdir(fn))
    if os.path.exists(fn):
        print(os.path.basename(fn))
    folder_path = fn
    """

    """讀取 XML 檔案"""

    # 一般資料夾計算數量
    if (not (args.recursive)) and(args.path): # 因為args.path 有設定default值,只有指定-r時args.path會有預設值"."產生,條件需加上 not(args.recursive)
        count_results = count_folder(folder_path)
        
    #遞迴計算
    if (args.recursive):
        count_results = count_recursive_folder(recursive_folder_path)
        
    print(count_results)
    print(f"Total xml : { count_results['count_xml'] }, { count_results['count_det'] }")

if __name__=="__main__":
    main()
"""
# 一般資料夾計算數量
for file_name in os.listdir(folder_path):
# 讀取檔案,只讀取 xml 檔
    if not file_name.endswith('.xml'): 
        continue # 跳過 .xml 以外的檔
    file_path = os.path.join(folder_path, file_name )
    print(file_path)

    # 用於計算總xml數(若每張都有輸出xml即是總張數)
    count_xml += 1

    # 從檔案載入並解析 XML 資料
    tree = ET.parse(file_path)
    root = tree.getroot()
    #尋找 XML 節點
    # 搜尋所有子節點
    # 用 Pythoninc 的 collections.defaultdict取代,計算單張圖片劣化類別
    deteriorate = root.findall("./object/name")
    det = collections.defaultdict(int)
    for name in deteriorate:
        det[name.text] += 1
    # 無劣化以 "other" 代表
    if not det:
        print(f"not det: {file_name }")
        det["other"] += 1 
    print(det)
    print(f"det.keys: {det.keys()}, file_name : {file_name }")
    
    # 計算各圖片劣化類別總數
    for k in det.keys():
        count_det[k] += 1
"""
"""
# deprecated
# 計算2000張內不包含裂縫和無劣化的張數
    flag = 0
    for i in det_list:
        if  re.match("crack",i):
            continue
        flag |= det.get(i,0) 
    if flag > 0:
        count_2000 += 1
"""
"""
print(f"Total xml : {count_xml }, {count_det}")
# print(f"count_2000: {count_2000}")
"""