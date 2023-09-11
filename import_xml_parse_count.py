import xml_parse_count
import os,sys


folder_path = sys.argv[1]

print(xml_parse_count.count_folder(folder_path))

"""
recursive_folder_path = sys.argv[1]
results = xml_parse_count.count_recursive_folder(recursive_folder_path)
print(f"results:{results}")
"""
#results= xml_parse_count.count_file_deteriorate(sys.argv[2])
#print(results)
