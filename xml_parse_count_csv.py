#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 上面兩行是for python2(一定要原封不動放最上面) ,否則遇到中文會跳錯 SyntaxError: Non-ASCII character '\xe4' in file xml_parse_count.py on line 6, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details
import csv
import logging
import os
import platform
import subprocess
import xml.etree.ElementTree as ET
import collections
import sys
import re
# debug message in log file
logging.basicConfig(filename="log_filename.txt", 
                    level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")


# 創建 .csv 檔
def create_csv(file_path, header_row):
    logging.debug(f"create_csv({file_path}, {header_row})")
    path = file_path
    with open(path, 'w+') as file:
        csv_write = csv.writer(file)
        csv_write.writerow(header_row)
        file.close()

# 寫入到 .csv 檔
def write_csv(file_path,data_row):
    path = file_path
    with open(path, 'a+') as file:
        csv_write = csv.writer(file)
        csv_write.writerow(data_row)
        file.close()



def write_dict_to_csv(csv_path,data_dict,header_row):   
    logging.debug(f"write_dict_to_csv({csv_path},{data_dict})")
    with open(csv_path,'a+',encoding='utf8',newline='') as csv_output:
        writer = csv.DictWriter(csv_output, fieldnames=header_row, extrasaction='ignore')
        print(f"data_dict{data_dict}")
        writer.writerow(data_dict)
        csv_output.close()

# 劣化標註列表
det_list = ["crack", 
            "crack_01",
            "crack_AC",
            "crack_AC_01",
            "spalling",
            "efflorescence",
            "corrosion",
            "water_gain",
            "rusty_water"]

# folder_path,用在指定要處理的資料夾 ｀python xml_parse_count.py "指定資料夾"｀
fn = sys.argv[1]
if os.path.exists(fn):
    print(os.path.basename(fn))
folder_path = fn
print(f"folder_path: {folder_path}")

# folder_name, 用來組合檔案路徑
folder_name = os.path.basename(folder_path)
print(f"folder_name: {folder_name}")
csv_path = os.path.join(folder_path + "_xml_parse_count.csv") # 輸出的 .csv 檔路徑,用來匯入 excel 加總資料夾內單張圖片的劣化類別框選數量
# csv_path = os.path.join(".",folder_name+"_csvfile.csv") # 輸出的 csvfile.csv 檔路徑,用來匯入 excel 加總資料夾內單張圖片的劣化類別框選數量
csv_total_path = os.path.join(folder_path + "_xml_parse_count_total.csv") # 輸出的 .csv 路徑,用來匯入 excel 加總多次執行不同資料夾的 xml_parse_count_csv.py 的數量
#csv_total_path = os.path.join(".","_csvtotal.csv") # 輸出的 csvtotal.csv 路徑,用來匯入 excel 加總多次執行不同資料夾的 xml_parse_count_csv.py 的數量


count = 0 # 用於計算總xml數(若每張都有輸出xml即是總張數)
count_det = collections.defaultdict(int) # 用於計算圖片個劣化類別總數

# 遍歷 folder,讀取 xml file
for filename in os.listdir(folder_path):
# 讀取檔案,只讀取 xml 檔
    filename = filename.lower() # 副檔名統一小寫
    if not filename.endswith('.xml'): 
        continue # 跳過 .xml 以外的檔
    file_path = os.path.join(folder_path, filename)
    print(file_path)

    # 用於計算總xml數(若每張都有輸出xml即是總張數)
    count += 1

    # 從檔案載入並解析 XML 資料
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # 蒐集 <object> 底下的 <name> tag（也就是這張圖的所有劣化類別名稱),存到字典方便後續操作
    """用 collections.defaultdict 建立預設值為 0 的字典,
    將讀到的<name> 放到字典的 key,<name> 的數量放到字典的 value,
    用來計算單張圖片劣化類別的節點數(也就是一張圖有多少個特定劣化框選數量)"""
    deteriorate = root.findall("./object/name")
    det = collections.defaultdict(int)
    for name in deteriorate:
        det[name.text] += 1
    # 無劣化以 "other" 代表
    if not det:
        print(f"not det: {filename}")
        det["other"] += 1 
    print(f"det: {det}")
    print(f"det.keys: {det.keys()},set(det):{set(det)}, filename: {filename}")
    
    # 組合出標題列
    filename_list = ["filename"]
    # 把 檔名 和所有劣化類別組起來,當作csv檔匯入excel後的標題列
    for i in (det.keys()):
        filename_list.append(i)
    csv_header_list= filename_list
    print(f"csv_header_list: {csv_header_list}")

    # 組合對應標題列的字典,方便後面可以用csv.DictWriter()根據字典的 key 和標題列的相同項目寫入對應的值
    filename_dict ={"filename":filename}
    csv_header_dict= {**filename_dict,**det} # 把filename 和 劣化 組一起當作第一標題列（csv要匯入excel做處理)

    # 檢查是否已經存在 csv 檔
    if not os.path.exists(csv_path):
        create_csv(csv_path, csv_header_list)
    # 把前面xml內計算好的劣化類別字典資料寫入 csv
    write_dict_to_csv(csv_path, csv_header_dict, csv_header_list)
   
    # 計算各圖片劣化類別總數(一張圖有一種劣化算一個)
    for k in det.keys():
        count_det[k] += 1


# 組合出標題列
foldername_list = ["folder_path"]
# 把 檔名 和所有劣化類別組起來,當作csv檔匯入excel後的標題列
for i in (det.keys()):
    foldername_list.append(i)
csv_total_header_list= foldername_list
print(f"csv_total_header_list: {csv_total_header_list}")

# 組合對應標題列的字典,方便後面可以用csv.DictWriter()根據字典的 key 和標題列的相同項目寫入對應的值
foldername_dict ={"folder_path":folder_path}
count_det_data={**foldername_dict,**count_det}
print(f"count_det_data: {count_det_data}")  

# 檢查是否已經存在 csv 檔
if not os.path.exists(csv_total_path):
    create_csv(csv_total_path,csv_total_header_list)
# 把前面xml內計算好的劣化類別字典資料寫入 csv
write_dict_to_csv(csv_total_path,count_det_data,csv_total_header_list)

print(f"\nTotal xml : {count}, {count_det }, {set(count_det)}")



