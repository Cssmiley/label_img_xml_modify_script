"""
files_dispatch.py

需求:
1. 指定 現在資料夾路徑 和 對照用的資料夾路徑 進行比對 .xml .jpg 檔案
2. 把比對符合 對照用資料夾 內的檔案存放到 matched 資料夾,不符合的放到 unmatched 資料夾,把剩下的 .xml .jpg 檔案存放到 other 資料夾
3. 產生 紀錄有比對符合 matched 和比對不存在的(對照資料夾有但現有資料夾沒有) unmatched 列表的 .csv 檔案(方便用 excel 匯入查看確認)

程式:
- 選取新、舊資料夾路徑(GUI或手動填)-手動填
- 比對 對照資料夾 和 原資料夾是否有相符的檔案,並移動 .jpg .xml 檔案到 matched 資料夾和 unmatched 資料夾
- 寫入比對符合和比對不存在的(對照資料夾有但現有資料夾沒有)檔案名稱到 .csv檔方便確認
- 將比對完移動後,剩下來的 .jpg .xml 檔案移動到 other 資料夾 

使用:
- 安裝套件 : 不需安裝,使用內建lib
- 執行 python:
```
    下面指令會把 --path 資料夾內.jpg .xml 檔, 比對 --cpath  內的檔案,符合的放到 matched 資料夾,
    不符合的放到 unmatched 資料夾,剩下的放到 other 資料夾 
    > python3 files_dispatch.py --path "現在資料夾路徑" --cpath  "對照資料夾路徑"
    例如.
    > python3 files_dispatch.py --path D:\labelImg提交檔案 --cpath  D:\labelImg提交檔案\對照資料夾

    可以把上面的 --path --cpath 換成簡寫的 -p -c ,如下所示（空格是為了和上面清楚對照可以不需要這麼多空格) 
    > python3 files_dispatch.py -p     "現在資料夾路徑" -c       "對照資料夾路徑"
    例如.
    > python3 files_dispatch.py -p D:\labelImg提交檔案 -c D:\labelImg提交檔案\對照資料夾
```
指令參數說明：
```
    -p, --path 
        現在資料夾 路徑,例如. `D:\labelImg提交檔案`
    -c, --cpath
        用來比對用的 .xml 檔所在的 對照資料夾 路徑,例如. `D:\labelImg提交檔案\對照資料夾`
```
"""
import os,sys
import shutil
import csv
import argparse

# 用在指定資料夾 對照用資料夾
"""
fn2 = sys.argv[2]
if os.path.exists(fn2):
    print(os.path.basename(fn2))
compare_folder_path = fn2 
fn1 = sys.argv[1]
if os.path.exists(fn1):
    print(os.path.basename(fn1))
present_folder_path = fn1
"""

parser = argparse.ArgumentParser()
parser.add_argument("-p",
                    "--path",
                    nargs=1,
                    type=str,
                    help="這是present資料夾路徑")
parser.add_argument("-c",
                    "--cpath",
                    nargs=1,
                    type=str,
                    help="這是compare資料夾路徑")

args = parser.parse_args()
print(f"第 1 個引數：{args.path},type={type(args.path)}")
print(f"第 2 個引數: {args.cpath}, type={type(args.cpath)}")
present_folder_path =  args.path[0]
compare_folder_path = args.cpath[0]

# 檢查使用者輸入是否是路徑
if os.path.exists(present_folder_path):
    print(present_folder_path)
else: 
    print(f"'{present_folder_path}' is not right path name, Please enter a right path name.")
    sys.exit()
if os.path.exists(compare_folder_path):
    print(compare_folder_path)
else: 
    print(f"'{compare_folder_path}' is not right path name, Please enter a right path name.") 
    sys.exit()

# 暫存分類資料夾
matched_folder = "matched"
matched_folder_path = os.path.join(present_folder_path, matched_folder)
unmatched_folder = "unmatched"
unmatched_folder_path = os.path.join(present_folder_path, unmatched_folder)
other_folder = "other"
other_folder_path = os.path.join(present_folder_path, other_folder )


# .csv 檔處理
csv_name = "_files_dispath.csv"
csv_path = os.path.join(present_folder_path, present_folder_path + csv_name) 
print(f"csv_path: {csv_path}")
# 創建 .csv 檔
def create_csv(file_path, header_row):
    path = file_path
    with open(path, 'w+') as file:
        csv_write = csv.writer(file)
        csv_write.writerow(header_row)
        file.close

# 寫入到 .csv 檔
def write_csv(file_path, data_row):
    path = file_path
    with open(path, 'a+') as file:
        csv_write = csv.writer(file)
        csv_write.writerow(data_row)
        file.close()
# 用字典的方式對照header_row,寫入到 .csv 檔
def write_dict_to_csv(csv_path,data_dict, header_row):   
    with open(csv_path,'a+',encoding='utf8',newline='') as csv_output:
        writer = csv.DictWriter(csv_output, fieldnames=header_row, extrasaction='ignore')
        print(f"data_dict{data_dict}")
        writer.writerow(data_dict)
        csv_output.close()

# 用來紀錄比對吻合與沒比對到的
matched=[]
unmatched = []

# 比對 對照資料夾 和 原資料夾是否有相符的檔案並移動到 暫存資料夾1
for _file in os.listdir(compare_folder_path):
    print(f"_file: {_file}")

    # 檢查是否存在資料夾,若不存在就建立資料夾
    if not os.path.exists(matched_folder_path):
        os.makedirs(matched_folder_path)
    # 檢查是否存在資料夾,若不存在就建立資料夾
    if not os.path.exists(unmatched_folder_path):
        os.makedirs(unmatched_folder_path)
    # 檢查是否存在資料夾,若不存在就建立資料夾
    if not os.path.exists(other_folder_path):
        os.makedirs(other_folder_path)

    # 確認 對照資料夾內的檔案是否存在 原資料夾
    full_file_path = os.path.join(present_folder_path, _file)
    compare_file_path = os.path.join(compare_folder_path, _file)
    if os.path.exists(full_file_path):
        matched.append(_file)
        shutil.move(full_file_path, matched_folder_path)
    else:
        unmatched.append(_file)
        shutil.copy(compare_file_path, unmatched_folder_path)
        print(f"不存在的檔案:{_file}")
        """
        # 記錄到 .txt檔
        txt_name = "files_dispatch.txt"
        txt_path = os.path.join(present_folder_path,txt_name )
        if not os.path.exists(txt_path):
            f= open(txt_path, 'w')
            f.close()

        with open(txt_path, 'a') as f:
            f.write(f"不存在的檔案:{_file}\n")
        """

# 寫入比對符合和不存在的檔案名稱到 .csv檔方便確認
header_row = ["matched","unmatched"]
# 檢查 .csv 檔案是否存在,若不存在就創建
if not os.path.exists(csv_path):
    create_csv(csv_path, header_row)
csv_size = os.path.getsize(csv_path)
if csv_size != 0:
    create_csv(csv_path, header_row)

# 寫入 matched, unmatched 到 .csv    
if len(matched) >= len(unmatched):
    num = len(matched) - len(matched)
    for i in num:
        unmatched.append("")
else:
    num = len(unmatched) - len(matched)
    for i in range(num):
        matched.append("")
for i in range(len(matched)):
    data_dict={"matched":matched[i], "unmatched":unmatched[i]}
    write_dict_to_csv(csv_path,data_dict,header_row)
 
# 將比對完移動後,剩下來的 .jpg .xml 檔案移動到 other 資料夾 
for _file in os.listdir(present_folder_path):
    # 跳過 .xml .jpg 以外的檔
    if not _file.endswith('.xml') | _file.endswith('.jpg') :
        continue
    current_file_path = os.path.join( present_folder_path, _file)
    shutil.move(current_file_path, other_folder_path)

