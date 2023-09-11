"""
xml_node_rename.py

需求:
1. 指定資料夾路徑,舊劣化名稱、新劣化名稱
2. 把資料夾內的 .xml 檔內的舊劣化名稱置換成新劣化名稱
3. 防呆: 
```
        若原本的劣化有 crack_01 efflorescence,更名時誤下指令 把 crack_01 更名成 efflorescence 而不是原本要換的 crack_fissures,
        會造成更名後的 efflorescence(實際上是裂縫龜裂) 和原本已經有的 efflorescence(白華) 混在一起,變成全部都必須重新人工標註修正,
        因此需要在更名時,若更改名稱和已有的劣化名稱重疊,需提示 
```
4. 注意事項!!: (!!注意!! 程式無法判斷,所以須正確下指令或是一次執行指處理一個劣化名稱比較保險)
```
        下指令時 --old_tag 和 --new_tag 項目需前後對照順序一致
        例如.
        (O)正確的例子
        ` --old_tag crack_01 water_gain --new_tag crack_fissures infiltration_crack` 
        crack_01 對到 crack_fissures, water_gain 對到 infiltration_crack
        (X) 錯誤的例子
        --old_tag crack01 water_gain --new_tag infiltration_crack crack_fissures
        crack_01 對到 infiltration_crack, water_gain 對到 crack_fissures
```
程式:
- 選取資料夾路徑(GUI或手動填)-手動填 , 指定舊劣化名稱、新劣化名稱
- 遍歷選取資料夾讀取 .xml 檔,取得劣化資訊
- 防呆: 比對劣化資訊,若更改名稱是已存在劣化標註,就詢問確認
- 更換指定的舊的劣化類別名稱,並寫入到 .xml 檔


使用:
- 安裝套件 : 不需安裝,使用內建lib
- 執行 python:
```
    下面指令會把 --path 資料夾內的 --old_tag 舊劣化名稱  置換成 --new_tag 新劣化名稱
    > python3 xml_node_rename.py --path "資料夾路徑" --old_tag "舊劣化名稱" --new_tag "新名稱"
    > python3 xml_node_rename.py --path D:\labelImg提交檔案 --old_tag crack_01 water_gain --new_tag crack_fissures infiltration_crack
    可以把上面的 --path --old_tag --new_tag 換成簡寫的 -p -o -n ,如下所示
    > python3 xml_node_rename.py -p     D:\labelImg提交檔案 -o        crack_01 water_gain -n        crack_fissures infiltration_crack
```
指令參數說明：
```
    -p, --path
        指定被置換掉的 .xml 檔案所在的資料夾路徑,例如. `D:\labelImg提交檔案`
    -o, --old_tag
        要被置換掉的劣化類別名稱,例如. crack_01
    -n, --new_tag
        用來置換的調劣化類別名稱,例如. crack_fissures
```
- 將 old 資料夾的 .xml檔內的特定劣化節點名稱(e.g. <crack_01> ) 換成新名稱(e.g. <crack_fissures>)
"""


import csv
import os
import xml.etree.ElementTree as ET
import collections
import sys
import argparse

# 創建 .csv 檔
def create_csv(file_path, header_row):
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
        
# 定義輸入參數
parser = argparse.ArgumentParser()
parser.add_argument("-p",
                    "--path",
                    nargs=1,
                    type=str,
                    help="這是路徑--path")
parser.add_argument("-o",
                    "--old_tag",
                    nargs='+',
                    help="請輸入 要被置換的劣化標註 e.g. water_gain",
                    type=str)
parser.add_argument("-n",
                    "--new_tag",
                    nargs='+',
                    help="請輸入新劣化標註 e.g. infiltration_crack",
                    type=str)
args = parser.parse_args()
folder_path =  args.path[0]
det_orig = args.old_tag
det_new = args.new_tag
print(f"第 1 個引數：{args.path},type={type(args.path)}")
print(f"第 2 個引數: {args.old_tag}, type={type(args.old_tag)}")
print(f"第 3 個引數：{args.new_tag}, type={type(args.new_tag)}")

# 若要置換的old_tag劣化類別和new_tag劣化類別數量不一致,跳出提示並終止程式
if len(det_orig) != len(det_new):
    print(f"old_tag: {args.old_tag} 和 new_tag: {args.new_tag} ,數量不一致,請重新輸入old_tag 和 new_tag 前後對照!" )
    sys.exit()

"""讀取 XML 檔案"""
# 取得劣化資訊
count_det = collections.defaultdict(int)
for filename in os.listdir(folder_path):
# 讀取檔案,只讀取 xml 檔
    if not filename.endswith('.xml'): 
        continue # 跳過 .xml 以外的檔
    file_path = os.path.join(folder_path, filename)
    #print(file_path)

    # 從檔案載入並解析 XML 資料
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    """尋找 XML 節點"""

    # 用 Pythoninc 的 collections.defaultdict取代,計算單張圖片劣化類別
    deteriorate = root.findall("./object/name")
    det = collections.defaultdict(int)
    for name in deteriorate: 
        #print(f"name.text: {name.text}")
        det[name.text] += 1 # 計算劣化數量
        #print(f"det[name.text]: {det[name.text]}")
        #print(f"enumerate(det_orig): {det_orig_dict}")
    # 無劣化以 "other" 代表
    if not det:
        print(f"not det: {filename}")
        det["other"] += 1 

    # 計算各圖片劣化類別總數
    for k in det.keys():
        count_det[k] += 1
#print(count_det)

# 防呆警告
for item in det_new: 
    print(f"item: {item}, det_new: {det_new}")
    if  item in count_det.keys():
        print(f"det.keys(): {count_det.keys()}")
        print(f"{item} 劣化已經存在,如果更名會與原有的劣化混在一起 ,可能造成全部檔案需要人工修改,是否繼續? 輸入 continue：繼續 n:取消 :")
        response = input("> ").lower().strip()
        if (response == "n") | (response == ""):
            print("已取消!!")
            sys.exit()
        elif response == "continue":
            break
        else:
            print("請輸入 continue 或 n")
            sys.exit()

""" 處理 xml檔 """
for filename in os.listdir(folder_path):
    # 跳過 .xml
    if not filename.endswith('.xml'):
        continue

    file_path = os.path.join(folder_path, filename)
    print(f"file_path:{file_path}")

    # 從檔案載入並解析 xml 資料
    tree = ET.parse(file_path)
    root = tree.getroot()

    search_tag = "./object/name"
    deteriorate = root.findall(search_tag)
    det = collections.defaultdict(int)
    for name in deteriorate: 
        for i in range(len(det_orig)):
            if name.text == det_orig[i]:
                name.text = det_new[i]
                print(f"i: {i}, det_orig[i]:{det_orig[i]}, det_new[i]: {det_new[i]}")
                file_path = os.path.join(folder_path, filename)
                tree.write(file_path,encoding="UTF-8")
        det[name.text] += 1
    print(f"det: {det}")
    print(det.keys(),filename)

    # 計算各圖片劣化類別總數
    for k in det.keys():
        count_det[k] += 1
print(count_det)