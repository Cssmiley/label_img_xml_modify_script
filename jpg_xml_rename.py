import shutil
import logging
import os, sys
import csv


# folder path,用在 python xml_parse_count.py "指定資料夾"
fn = sys.argv[1]
if os.path.exists(fn):
    print(os.path.basename(fn))
folder_path = fn

""".csv 檔處理"""
folder_name = os.path.basename(folder_path)
print(f"folder_name: {folder_name}")
csv_filepath = "_csvTraceRename.csv"
csv_path = os.path.join(".",folder_name+csv_filepath) 

# 創建 .csv 檔
def create_csv(file_path, header_row):
    logging.debug(f"create_csv({file_path}, {header_row})")
    path = file_path
    with open(path, 'w+') as file:
        csv_write = csv.writer(file)
        csv_write.writerow(header_row)
        file.close

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
        
# debug message in log file
logging.basicConfig(filename="log_filename.txt", 
                    level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")


# 遍歷 folder,讀取 xml file

# 取得所有檔案與子目錄名稱
#files = os.listdir(folder_path)

"""更改檔名格式"""
# 改檔名串接數字
stream_num = 4588
# 改檔名串接字串
stream_word= "_CTCI"
# 更名後新檔案存放位置
new_foldername ="多重劣化" 

"""
如果subfolder 是 dir
    遞迴呼叫
如果subitem 是 file
    重編碼
    建立檔名對照表
    更名
"""

def recursive_folder(_folder):
    global stream_num
    for _subitem in sorted(Path(_folder).iterdir()):
        if _subitem.is_dir():
            print(f"dir: {_subitem}")
            recursive_folder(_subitem)

        if _subitem.is_file():
            print(f"file: {_subitem}")
            
            _file = _subitem 
            root = _file.parent 

            print(f"root: {root}")
            filename = str(_file).lower() # 副檔名統一小寫
            print(f"filename: {filename}")
            file_path = Path(filename)
            #file_rootname = filename.split(".")[0] # 檔名
            file_rootname = file_path.stem # 檔名
            print(f"file_path.stem: {file_path.stem}")
            #file_typename = filename.split(".")[1] # 副檔名
            file_typename = file_path.suffix # 副檔名
            print(f"file_path.suffix: {file_path.suffix}")
            fullpath = os.path.join(root,_file)
            newpath = os.path.join(root, str(stream_num) + stream_word+"."+file_typename)
            # 跳過 .xml 以外的檔
            if not filename.endswith('.xml'):
                continue
            print(_file)
            
            # 更名前紀錄檔名對照表
            header_row = ["old_filepath","newpath"]
            if not os.path.exists(csv_path):
                create_csv(csv_path, header_row)
            data_dict={"old_filepath":fullpath, "newpath":newpath}
            write_dict_to_csv(csv_path,data_dict,header_row)
            data_jpg_dict={"old_filepath":fullpath.replace('.xml', '.jpg'), "newpath":newpath.replace(".xml", ".jpg")}
            write_dict_to_csv(csv_path,data_jpg_dict,header_row)                
            
            # 更名 .xml 檔
            print(f"fullpath: {fullpath}\nnewpath: {newpath}")
            os.rename(fullpath, newpath)
            # 更名 .jpg 檔
            print(f"jpg fullpath: {fullpath.replace('.xml', '.jpg')}\n jpg newpath: {newpath.replace('.xml', '.jpg')}")
            os.rename(fullpath.replace(".xml", ".jpg"), newpath.replace(".xml", ".jpg"))
            
            # 移動 .xml .jpg 檔
            
            new_folderpath = os.path.join(folder_path,new_foldername)
            if not os.path.exists(new_folderpath):
                os.makedirs(new_folderpath)
            shutil.move(newpath, new_folderpath)
            shutil.move(newpath.replace(".xml", ".jpg"), new_folderpath)
            stream_num += 1

from pathlib import Path
print(Path(folder_path).iterdir())
print(f"HIHI {Path(folder_path)}")

recursive_folder(folder_path)

"""
print(os.listdir(folder_path))
for subfolder in os.listdir(folder_path):
    for subfile in os.listdir(subfolder):
        print(subfile)
"""
"""
# 遞迴列出所有子目錄與檔案
for root, dirs, files in os.walk(folder_path):
    dirs = sorted(dirs,key=int)
    print("路徑：", root)
    print("  目錄：", dirs)
    print("  檔案：", files)
    for _file in files:
        filename = _file.lower() # 副檔名統一小寫
        file_rootname = filename.split(".")[0]
        file_typename = filename.split(".")[1]
        fullpath = os.path.join(root,_file)
        newpath = os.path.join(root, str(stream_num) + stream_word+"."+file_typename)
        # 跳過 .xml 以外的檔
        if not filename.endswith('.xml'):
            continue
        print(_file)

        # 更名前紀錄檔名對照表
        header_row = ["old_filepath","newpath"]
        if not os.path.exists(csv_path):
            create_csv(csv_path, header_row)
        data_dict={"old_filepath":fullpath, "newpath":newpath}
        write_dict_to_csv(csv_path,data_dict,header_row)
        data_jpg_dict={"old_filepath":fullpath.replace('.xml', '.jpg'), "newpath":newpath.replace(".xml", ".jpg")}
        write_dict_to_csv(csv_path,data_jpg_dict,header_row)

        # 更名 .xml 檔
        print(f"fullpath: {fullpath}\nnewpath: {newpath}")
        os.rename(fullpath, newpath)
        # 更名 .jpg 檔
        print(f"jpg fullpath: {fullpath.replace('.xml', '.jpg')}\n jpg newpath: {newpath.replace('.xml', '.jpg')}")
        os.rename(fullpath.replace(".xml", ".jpg"), newpath.replace(".xml", ".jpg"))
        # 移動 .xml .jpg 檔
        new_folderpath = os.path.join(folder_path,new_foldername)
        if not os.path.exists(new_folderpath):
            os.makedirs(new_folderpath)
        shutil.move(newpath, new_folderpath)
        shutil.move(newpath.replace(".xml", ".jpg"), new_folderpath)
        
        stream_num += 1    
        """    