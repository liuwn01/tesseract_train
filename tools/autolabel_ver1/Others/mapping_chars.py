import os
import json
import shutil
import os
from fontTools.ttLib import TTFont

def list_characters_in_font(font_path):
    font = TTFont(font_path)
    characters = set()

    # 遍历 cmap 表中的每个条目
    for table in font['cmap'].tables:
        for codepoint in table.cmap.keys():
            characters.add(chr(codepoint))  # 将 Unicode 编码转换为字符

    return ''.join(sorted(characters))  # 返回排序后的字符


def process_fonts_in_directory(directory):
    # 递归遍历目录下的所有字体文件
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(('.ttf', '.ttc')):  # 检查文件扩展名
                font_path = os.path.join(root, filename)
                print(f"处理字体文件: {font_path}")

                try:
                    characters = list_characters_in_font(font_path)

                    # 将字符写入对应的 TXT 文件
                    txt_file_path = f'{font_path}.txt'
                    with open(txt_file_path, 'w', encoding='utf-8') as f:
                        f.write(characters)

                    print(f"已将字符写入: {txt_file_path}")
                except Exception as e:
                    print(f"处理文件时出错: {e}")

def load_dict(file_path):
    """从字典文件加载字符"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def check_character_in_file(character, file_path):
    """检查字符是否在指定的文件中"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return character in content
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return False

def process_files_in_directory(directory, char_dict):
    """递归遍历目录，检查每个字符在 TXT 文件中的存在情况"""
    results = {char: [] for char in char_dict}

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.txt'):  # 检查文件扩展名
                file_path = os.path.join(root, filename)
                print(f"处理文件: {file_path}")

                for char in char_dict:
                    if check_character_in_file(char, file_path):
                        results[char].append(file_path)

    return results


def find_minimum_files(char_file_mapping):
    """找到最小的文件集合以覆盖所有字符"""
    covered_chars = set()
    selected_files = set()

    # 将字符和其对应的文件列表转换为元组
    char_file_list = [(char, set(files)) for char, files in char_file_mapping.items()]

    while len(covered_chars) < len(char_file_mapping):
        # 选择能覆盖最多未覆盖字符的文件
        best_file = None
        best_coverage = 0
        best_file_chars = set()

        for char, files in char_file_list:
            for file in files:
                if file not in selected_files:
                    # 计算该文件能覆盖的字符
                    can_cover = {c for c in char_file_mapping if
                                 file in char_file_mapping[c] and c not in covered_chars}
                    if len(can_cover) > best_coverage:
                        best_coverage = len(can_cover)
                        best_file = file
                        best_file_chars = can_cover

        if best_file is None:  # 如果没有更多文件可选，跳出循环
            break

        # 更新已覆盖的字符和选中的文件
        covered_chars.update(best_file_chars)
        selected_files.add(best_file)

    return selected_files

def copy_files_to_directory(file, target_directory):
    """将文件复制到指定目录"""
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)  # 如果目标目录不存在，则创建

    if os.path.exists(f"{file}"):
        shutil.copy(f"{file}", target_directory)
    else:
        return
    print(f"复制文件: {file} 到 {target_directory}")

# 查找并复制文件的函数
def find_and_copy_file(font_file, source_dir, target_dir):
    for root, dirs, files in os.walk(source_dir):
        if font_file in files:
            source_path = os.path.join(root, font_file)
            shutil.copy(source_path, target_dir)
            print(f"复制成功: {font_file} -> {target_dir}")
            return True  # 找到后返回，避免重复查找
    return False  # 如果没有找到

# 解析目录下所有font文件的字典表并生成txt
directory = './AllFonts'  # 替换为你字体文件所在的文件夹路径
process_fonts_in_directory(directory)

# 示例用法
dict_file_path = 'dict-utf8.txt'#'empty_keys_1.txt' #'dict-utf8.txt'  # 替换为字典文件路径

# 加载字典 A
char_dict = load_dict(dict_file_path)

# 处理文件夹，获取字符和文件的对应关系
results = process_files_in_directory(directory, char_dict)

# 将结果保存为 JSON 文件
output_json_path = 'ALL_output.json'  # 替换为输出 JSON 文件的路径
with open(output_json_path, 'w', encoding='utf-8') as json_file:
    json.dump(results, json_file, ensure_ascii=False, indent=4)

# print(f"结果已保存到: {output_json_path}")
#
# default_fonts = ['simsunb.ttf','simhei.ttf']
#
# with open(output_json_path, 'r', encoding='utf-8') as user_file:
#     jsonresults = json.loads(user_file.read())
#     ##找到最小的文件集合以覆盖所有字符
#     minimum_files = find_minimum_files(jsonresults)
#     minimum_file_names = [ str(os.path.basename(path)).replace('.txt','') for path in minimum_files]
#
#     print(f"Minimum file set: {minimum_files}")
#
#     # 用于存储结果
#     result = {}
#
#     for char, file_list in jsonresults.items():
#         # 标志是否找到匹配
#         found = False
#         # 遍历 file_list 检查是否与 listA 匹配
#         for file_path in file_list:
#             file_name = os.path.basename(file_path)  # 只获取文件名
#             # 检查文件名是否在列表A中
#             if file_name in default_fonts:
#                 result[char] = file_name.replace('.txt','')  # 记录匹配到的文件名
#                 found = True
#                 break
#             if file_name in minimum_file_names:
#                 result[char] = file_name.replace('.txt','')  # 记录匹配到的文件名
#                 found = True
#                 break
#
#         # 如果没有找到匹配，使用 file_list 中的第一个文件
#         if not found:
#             if len(file_list) > 0:
#                 result[char] = os.path.basename(file_list[0]).replace('.txt','')
#             else:
#                 result[char] = ""
#
#     # 打印结果
#     print(json.dumps(result, ensure_ascii=False, indent=4))
#
#     # 你也可以将结果保存到一个新的 JSON 文件中
#     with open('result.json', 'w', encoding='utf-8') as f:
#         json.dump(result, f, ensure_ascii=False, indent=4)
#
#     # result = None
#     # with open('result.json', 'r', encoding='utf-8') as user_file2:
#     #     result = json.loads(user_file2.read())
#
#     # 指定的搜索目录和目标目录
#     source_dir = './AllFonts'  # 替换为你的字体文件所在目录
#     target_dir = './TargetFonts'  # 替换为你要复制到的目标目录
#
#     # 确保目标目录存在
#     os.makedirs(target_dir, exist_ok=True)
#
#     for file in list(set(filter(None, result.values()))):
#         find_and_copy_file(file,source_dir, os.path.abspath("./TargetFonts/"))


