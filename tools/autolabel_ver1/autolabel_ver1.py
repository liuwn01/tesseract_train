import json
from PIL import Image, ImageDraw, ImageFont
#from IPython.display import display
import uuid
import random
import math
import os
import shutil


def loadFontMap():
    with open('./CharFontMapping.json', 'r', encoding='utf8') as user_file:
        file_contents = user_file.read()
        # print(file_contents)
        parsed_json = json.loads(file_contents)
        return parsed_json


def loadTemplateDetails():
    with open('./TemplateDetails.json', 'r', encoding='utf8') as user_file:
        file_contents = user_file.read()
        # print(file_contents)
        parsed_json = json.loads(file_contents)
        return parsed_json


def get_gb_testdata():
    with open("./testdata-utf8.txt", 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]
        return lines


def get_random_substring(source_lines, required_length):
    try:
        # 确保有有效行
        if not source_lines:
            raise ValueError("source_lines is empty!")

        # 迭代查找符合要求的行
        for _ in range(len(source_lines)):
            selected_line = random.choice(source_lines)

            # 检查所需长度是否超出选择行的长度
            if required_length <= len(selected_line):
                # 随机选择一个起始位置
                start_position = random.randint(0, len(selected_line) - required_length)

                # 截取字符串
                substring = selected_line[start_position:start_position + required_length]
                return substring

        raise Exception(f"[get_random_substring]: unknow issue, required_length: {required_length}！")

    except Exception as e:
        return f"[get_random_substring]-Error: {e}"


def random_bool():
    return random.choice([True, False])


def loadExceptionCharList():
    with open("./exception_strs.txt", 'r', encoding='utf-8') as file:
        file_contents = file.read()
        exception_char_list = list(dict.fromkeys(file_contents.replace('\n', '').replace('\r', '')))
        return exception_char_list


def replace_all_exceptionchars(sourceStr, exceptionStr, replaceChar):
    tempStr = sourceStr
    for char in exceptionStr:
        tempStr = tempStr.replace(char, replaceChar)
    return tempStr


def cleanDataRoot(outputfolder):
    if os.path.exists(outputfolder):
        shutil.rmtree(outputfolder)
    os.makedirs(f"{outputfolder}/ch4_training_images", exist_ok=True)
    os.makedirs(f"{outputfolder}/ch4_training_localization_transcription_gt", exist_ok=True)
    os.makedirs(f"{outputfolder}/ch4_test_images", exist_ok=True)
    os.makedirs(f"{outputfolder}/ch4_test_localization_transcription_gt", exist_ok=True)


def GenerateGTFiles(sourcepath):
    json_files = [f for f in os.listdir(sourcepath) if f.endswith('.json')]
    for file_name in json_files:
        file_path = f"{sourcepath}/{file_name}"
        txt_char_positions = []
        with open(file_path, 'r', encoding='utf-8') as file:
            datas = json.load(file)
            for positions in datas:
                for point in positions['char_positions']:
                    char = point['char']
                    top_left = point['top_left']
                    top_right = point['top_right']
                    bottom_left = point['bottom_left']
                    bottom_right = point['bottom_right']
                    txt_char_positions.append(
                        f"{top_left[0]},{top_left[1]},{top_right[0]},{top_right[1]},{bottom_right[0]},{bottom_right[1]},{bottom_left[0]},{bottom_left[1]},{char}")
        fn = file_name.replace(".json", '')
        with open(f"{sourcepath}/gt_{fn}.txt", 'w', encoding='utf-8') as file:
            for record in txt_char_positions:
                file.write(record + '\n')


def GenerateAndMovefiles(sourcepath, targetjpgpath, targetgtfilepath):
    jpg_files = [f for f in os.listdir(sourcepath) if f.endswith('.jpg')]
    for jpg in jpg_files:
        shutil.copy(f"{sourcepath}/{jpg}", targetjpgpath)

    gt_files = [f for f in os.listdir(sourcepath) if f.endswith('.txt')]
    for gt in gt_files:
        shutil.copy(f"{sourcepath}/{gt}", targetgtfilepath)


def generate_images(number_of_images_to_generate, is_draw_font_boundaries):
    template_details = loadTemplateDetails()
    font_map = loadFontMap()
    gb_testdatas = get_gb_testdata()
    templatefolder = "./Templates"
    outputFolder = "./Generated"
    if os.path.exists(outputFolder):
        shutil.rmtree(outputFolder)
    os.makedirs(outputFolder, exist_ok=True)

    for t_name in template_details:
        print(f"Generate '{number_of_images_to_generate}' images from '{t_name}' ... ")

        spacing = 1  # Character Spacing
        drawing_areas = template_details[t_name]
        imagepath = f"{templatefolder}/{t_name}"
        if not os.path.exists(imagepath):
            print(f"Not exists, Skip template '{t_name}' ... ")
            break

        for image_index in range(number_of_images_to_generate):

            char_positions = []  # save all char's position

            image = Image.open(imagepath)
            draw = ImageDraw.Draw(image)

            for areainfo in drawing_areas:
                area_json = {}
                font_size = areainfo['rectangle_height']
                rectangle_tl_x0 = areainfo['top_left'][0]
                rectangle_tl_y0 = areainfo['top_left'][1]
                rectangle_width = areainfo['rectangle_width']
                row_font_color = areainfo.get("font_color", "black")
                word_count_math = math.floor(rectangle_width / (spacing + font_size))
                if random_bool():
                    word_count_math = math.floor(word_count_math * 1.4)
                # print(f"word_count_math: {word_count_math}")

                text = get_random_substring(gb_testdatas, word_count_math)
                if isReplaceExceptionChar:
                    replaced_text = replace_all_exceptionchars(text, exception_char_list, exception_char_substitute)
                else:
                    replaced_text = ""

                area_json = {
                    "areainfo": areainfo,
                    "image_text": text,
                    "json_text": replaced_text,
                    "char_positions": []
                }
                start_x, start_y = rectangle_tl_x0, rectangle_tl_y0

                real_text_len = 0
                for char in text:
                    json_char = char
                    font_file = font_map.get(char, "arial.ttf")  # 如果没有记录在A中，则使用默认字体
                    if font_file is None or font_file == "":
                        font_file = "arial.ttf"

                    if isReplaceExceptionChar and (char in exception_char_list):
                        json_char = exception_char_substitute
                        font_file = exception_strs_font

                    # print(char, font_file, type(font_file))
                    font = ImageFont.truetype(font_file, font_size)

                    # 计算字符的边界框
                    bbox = draw.textbbox((start_x, start_y), char, font=font)
                    top_left = (bbox[0], bbox[1])
                    top_right = (bbox[2], bbox[1])
                    bottom_left = (bbox[0], bbox[3])
                    bottom_right = (bbox[2], bbox[3])

                    real_text_len = real_text_len + 1

                    if is_draw_font_boundaries:
                        draw.rectangle([(bbox[0], bbox[1]), (bbox[2], bbox[3])], outline="blue",
                                       width=1)  # for test, Draw font boundaries

                    # char_positions.append({
                    #     "char": char,
                    #     "font": font_file,
                    #     "top_left": top_left,
                    #     "top_right": top_right,
                    #     "bottom_left": bottom_left,
                    #     "bottom_right": bottom_right
                    # })
                    area_json["char_positions"].append({
                        "char": json_char,
                        "font": font_file,
                        "top_left": top_left,
                        "top_right": top_right,
                        "bottom_left": bottom_left,
                        "bottom_right": bottom_right
                    })

                    # 在图片上绘制字符
                    draw.text((start_x, start_y), char, font=font, fill=row_font_color)  # "black"

                    # 更新下一个字符的x位置
                    start_x += bbox[2] - bbox[0] + spacing
                    # print(f"[Limit: {rectangle_tl_x0 + rectangle_width}], Current:'{start_x}'")
                    if start_x >= (rectangle_tl_x0 + rectangle_width - font_size / 1.3):
                        # print("break")
                        break
                area_json["image_text"] = area_json["image_text"][0:real_text_len]
                area_json["json_text"] = area_json["json_text"][0:real_text_len]
                area_json["text_len"] = real_text_len
                char_positions.append(area_json)

            # 显示图片
            # display(image)

            if image.mode == 'RGBA':
                image = image.convert('RGB')

            # 保存图片
            image.save(f"{outputFolder}/{os.path.basename(imagepath).replace('.jpg', '')}-{image_index}.jpg")

            with open(f"{outputFolder}/{os.path.basename(imagepath).replace('.jpg', '')}-{image_index}.json", 'w',
                      encoding='utf-8') as f:
                json.dump(char_positions, f, ensure_ascii=False, indent=4)


exception_strs_font = "arial.ttf"
exception_char_substitute = "®"
exception_char_list = loadExceptionCharList()
Draw_font_boundaries = False
isReplaceExceptionChar = True
number_of_images_to_generate = 10
# generate_images(number_of_images_to_generate, Draw_font_boundaries)

cleanDataRoot("./data_root_dir")

generate_images(number_of_images_to_generate, Draw_font_boundaries)
GenerateGTFiles("./Generated")
GenerateAndMovefiles("./Generated", "./data_root_dir/ch4_training_images/", "./data_root_dir/ch4_training_localization_transcription_gt/")

# generate_images(number_of_images_to_generate, Draw_font_boundaries)
# GenerateGTFiles("./Generated")
# GenerateAndMovefiles("./Generated", "./data_root_dir/ch4_test_images/", "./data_root_dir/ch4_test_localization_transcription_gt/")












