"""
xml_node_move.py

需求:
1. 指定 old xml 和 new xml 路徑 (檔名相同) 及更動的劣化類別
2. 新建 xml,裏面包含  old xml 移除特定劣化類別節點 (ex. <crack>)後,把 new xml 特定劣化類別節點 append 到 old xml ,放到 replaced 資料夾

程式:
- 選取新、舊資料夾路徑(GUI或手動填)-手動填 , 指定劣化類別
- 遍歷選取資料夾讀取 .xml 檔
- 新建空xml,裡面包含移除舊的劣化類別節點,將更動的劣化類別節點複製,並寫入到舊的 .xml 放到 replaced 資料夾(沒有更動 old xml 和 new xml)

使用:
- 安裝套件 : 不需安裝,使用內建lib
- 執行 python:
```
    @ 置換劣化類別:
    下面指令會使用 --new_folder 資料夾內的指定劣化類別節點 --deteriorate , 替代掉 --old_folder 內的指定劣化類別節點
    > python3 xml_node_move.py --deteriorate crack efflorescence --old_folder "要被置換的舊節點資料夾路徑" --new_folder "新節點資料夾路徑"

    可以把上面的 --deteriorate --old_folder --newfolder 換成簡寫的 -d -o -n ,如下所示（空格是為了和上面清楚對照可以不需要這麼多空格) 
    > python3 xml_node_move.py -d            crack efflorescence -o           "要被置換的舊節點資料夾路徑" -n           "新節點資料夾路徑"

    @ 保留劣化類別:
    下面指令會使用 --new_folder 資料夾內的指定保留劣化類別以外的所有節點 --keep_deteriorate , 替代掉 --old_folder 內的指定劣化類別節點
    > python3 xml_node_move.py --keep_deteriorate crack efflorescence --old_folder "要被置換的舊節點資料夾路徑" --new_folder "新節點資料夾路徑"

    可以把上面的 --keep_deteriorate --old_folder --newfolder 換成簡寫的 -k -o -n ,如下所示（空格是為了和上面清楚對照可以不需要這麼多空格) 
    > python3 xml_node_move.py -k            crack efflorescence -o           "要被置換的舊節點資料夾路徑" -n           "新節點資料夾路徑"
```
指令參數說明：
```
    -d 置換劣化節點 和 -k 保留劣化節點 是互斥選項,無法同時執行
    -d, --deteriorate  
        指定要置換的劣化類別,可指定一個到多個,例如. `-d crack` 或 `-d crack efflorescence`,這些劣化類別的節點會被置換掉
    -k, --keep_deteriorate
        指定保留的劣化類別,可指定一個到多個, 例如. `-k crack` 或 `-k crack efflorescence`,除了指定的劣化類別外都會置換成新的版本
    
    -o, --old_folder
        要被置換掉的 .xml 檔案所在的資料夾路徑,例如. `D:\labelImg提交檔案`
    -n, --new_folder
        用來置換的調整過後的新劣化節點的 .xml 檔所在的資料夾路徑,例如. `D:\labelImg提交檔案\白華_efflorescence`
```
- 將 old 資料夾的 .xml檔內的特定劣化節點資訊(e.g. <crack>附帶的框選位置尺寸資訊) 換成 new 資料夾的 .xml檔的劣化節點資訊
"""
import xml.etree.ElementTree as ET
import logging
import os, sys
import shutil
import collections
import argparse
# debug message in log file
logging.basicConfig(filename="xml_node_move-log_filename.txt",
                    level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# 定義輸入參數
parser = argparse.ArgumentParser()
# 使用 argparse 的 add_mutaually_exclusive_group() 處理 置換和保留 特定劣化類別 命令不可同時進行的衝突
group = parser.add_mutually_exclusive_group()
group.add_argument("-d",
                    "--deteriorate",
                    nargs="+",
                    type=str,
                    help="這是要置換的劣化類別")
group.add_argument("-k",
                    "--keep_deteriorate",
                    nargs="+",
                    type=str,
                    help="這是要保留的劣化類別")
parser.add_argument("-o",
                    "--old_folder",
                    nargs=1,
                    help="這是第 2 個引數,請輸入路徑",
                    default=".")
parser.add_argument("-n",
                    "--new_folder",
                    nargs=1,
                    help="這是第 3 個引數, 請輸入路徑")
args = parser.parse_args()
object_tag = args.deteriorate
keep_object_tag = args.keep_deteriorate
old_folder_path = args.old_folder[0]  
new_folder_path = args.new_folder[0]
print(f"deteriorate 引數：{args.deteriorate},type={type(args.deteriorate)}")
print(f"keep_deteriorate 引數：{args.keep_deteriorate},type={type(args.keep_deteriorate)}")
print(f"old_folder 引數: {args.old_folder}, type={type(args.old_folder)}")
print(f"new_folder 引數：{args.new_folder}, type={type(args.new_folder)}")

# 顯示 置換或保留 劣化類別資訊,若未輸入相關命令則終止程式
if args.deteriorate:
    print(f"deteriorate: {object_tag},\nold_folder_path: {old_folder_path},\nnew_folder_path: {new_folder_path}")
elif args.keep_deteriorate:
    print(f"keep_deteriorate: {keep_object_tag},\nold_folder_path: {old_folder_path},\nnew_folder_path: {new_folder_path}")
else:
    print("請輸入 -d 引數 或 -k 引數")
    sys.exit()

# 建立保留劣化類別的 .xml
def keep_deteriorate_xml(out_xml_path, _keep_object_tag):
    print(f"keep_object_tag: {_keep_object_tag}, type(keep_object_tag): {type(_keep_object_tag)}\nout_xml_path: {out_xml_path}")
# 組合要寫入 xml 的節點
    # 建立 labelImg 輸出的 xml 檔的第一個節點 <annotation>
    xml_annotation = ET.Element("annotation")
    # 接著貼上上半段所有不是<object> 的節點
    for child in root:
        if child.tag == "object":
            continue # 跳過 <object> 節點
        xml_annotation.append(child)
    # 貼上指定保留劣化類別節點和新的其他劣化類別節點
    for item in _keep_object_tag:
        find_object =f"object[name='{item}']"
        print(f"find_object:{item}")
        # 從舊資料夾的xml檔,貼上指定保留劣化節點
        for xml_object in root.findall(find_object):
            xml_annotation.append(xml_object)
            print(f"append({xml_object.find('name').text})")
        # 從新資料夾的 xml 檔,貼上指定保留以外的其他劣化節點
        for xml_object in root_new.iter('object'):
            print(f"root_new.iter('object'): {xml_object}")
            print(f"xml_object.tag: {xml_object.tag}") # object
            if xml_object.find('name').text in _keep_object_tag:
                print(f"_keep_object_tag: {_keep_object_tag}")
                continue
            xml_annotation.append(xml_object)
            print(f"append({xml_object.find('name').text})")
    # 將組合好的節點寫入 .xml 檔
    tree._setroot(xml_annotation) # 將上面組合好的最上層節點 <annotation> 設成根節點
    tree.write(out_xml_path, encoding="UTF-8")
    #logging.debug(f"keep_deteriorate_xml({out_xml_path}, {_keep_object_tag})") # log down debug message for log file        

# 建立置換劣化類別的 .xml
def replace_deteriorate_xml(out_xml_path, _object_tag):
    print(f"object_tag: {_object_tag}, type(object_tag): {type(_object_tag)}\nout_xml_path: {out_xml_path}")
# 組合要寫入 xml 的節點    
    # 建立 labelImg 輸出的 xml 檔的第一個節點 <annotation>
    xml_annotation = ET.Element("annotation")
    # 接著貼上所有的節點
    for child in root:
        xml_annotation.append(child)
    # 移除指定劣化節點,並貼上更新的劣化節點
    for item in _object_tag:
        find_object = f"object[name='{item}']"
        print(f"find_object:{item}")
        # 移除 特定劣化節點
        for xml_object in root.findall(find_object):
            xml_annotation.remove(xml_object)
            print(f"remove({xml_object.find('name').text})")
        # 貼上 更改後的特定劣化節點
        for xml_object in root_new.findall(find_object):
            xml_annotation.append(xml_object)
            print(f"append({xml_object.find('name').text})")
# 將組合好的節點寫入 .xml 檔
    tree._setroot(xml_annotation) # 將上面組合好的最上層節點 <annotation>設成根節點
    tree.write(out_xml_path, encoding="UTF-8")
    #logging.debug(f"replace_deteriorate_xml({out_xml_path},{_object_tag})") # log down debug message for log file
 
"""讀取 xml 檔案"""
folder_path = old_folder_path
for filename in os.listdir(folder_path):

    # 讀取檔案, 只讀取 xml 檔
    filename = filename.lower() # 副檔名統一小寫
    if not filename.endswith('.xml'):
        continue # 跳過 .xml 以外的檔
    file_path = os.path.join(folder_path, filename)

    # read .xml file from old xml folder 
    xml_path = file_path
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # read .xml file from new xml folder
    new_xml_path = os.path.join(new_folder_path, filename)
    tree_new = ET.parse(new_xml_path)
    root_new = tree_new.getroot()

    # 蒐集 <object> 底下的 <name> tag（也就是這張圖的所有劣化類別名稱),存到字典方便後續操作
    """用 collections.defaultdict 建立預設值為 0 的字典,
    將讀到的<name> 放到字典的 key,<name> 的數量放到字典的 value,
    用來計算單張圖片劣化類別的節點數(也就是一張圖有多少個特定劣化框選數量)"""
    deteriorate = root.findall("./object/name") # 取得所有類別名稱
    det = collections.defaultdict(int) 
    for name in deteriorate:
        det[name.text] += 1
    print(f"filename: {filename} \ndet: {det}")

# 排除無劣化的 xml 檔,依據劣化輸出 xml
    if not det:
        continue # 跳過沒有框選劣化的空 xml
    # deteriorate_folder_path,用在輸出置換後的資料夾路徑
    #deteriorate_folder_path = os.path.join(".","replaced")
    deteriorate_folder_path = os.path.join(folder_path,"replaced")
    # output_xml_path,用在輸出的 .xml檔完整路徑
    output_xml_path = os.path.join(deteriorate_folder_path, filename.replace(".jpg",".xml"))

    # 檢查資料夾是否已經存在,若不存在就新增資料夾
    if not os.path.exists(deteriorate_folder_path):
        os.makedirs(deteriorate_folder_path)

    # 檢查圖片是否存在,若不存在就複製 .jpg 檔到新資料夾內
    jpg_path = os.path.join(folder_path, filename.replace(".xml",".jpg"))
    jpg_copy_path = os.path.join(deteriorate_folder_path,filename.replace(".xml",".jpg"))
    if not os.path.exists(jpg_copy_path):
        shutil.copy(jpg_path, jpg_copy_path)

    # 執行置換或保留劣化節點
    if args.deteriorate:
        # 置換劣化類別節點  
        replace_deteriorate_xml(output_xml_path, object_tag)
    elif args.keep_deteriorate:
        # 保留劣化節點
        keep_deteriorate_xml(output_xml_path, keep_object_tag)
    
