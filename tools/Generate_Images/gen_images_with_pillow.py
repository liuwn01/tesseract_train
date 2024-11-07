import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont
import uuid
import shutil
import subprocess
import os
import random
import time

FONT_MAPPINT = {
    "simsunb.ttf": "SimSun-ExtB",
    "simsun.ttc": "SimSun",
    "arial.ttf": "Arial",
    "msyh.ttc": "Microsoft YaHei",
    "monbaiti.ttf": "Mongolian Baiti",
    "himalaya.ttf": "Microsoft Himalaya",
    "msyi.ttf": "Microsoft Yi Baiti",
    "taile.ttf": "Microsoft Tai Le",
    "ntailu.ttf": "Microsoft New Tai Lue",
    "seguisym.ttf": "Segoe UI Symbol",
    "micross.ttf": "Microsoft Sans Serif",
}

json_data = [
    "arial.ttf",
    "himalaya.ttf",
    "micross.ttf",
    "monbaiti.ttf",
    "msyh.ttc",
    "msyi.ttf",
    "ntailu.ttf",
    "seguisym.ttf",
    "simsun.ttc",
    "simsunb.ttf",
    "taile.ttf"
]

number_of_generated = 1
min_len_of_generated_str = 10
max_len_of_generated_str = 30
outputFolder = f"./output"
errorFolder = f"{outputFolder}_E"
font_size = 32
# current_dir = os.path.dirname(os.path.abspath(__file__))
# fonts_folder = os.path.abspath(os.path.join(current_dir, '..', '..', 'fonts'))
# unicharset_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'langdata','eng.unicharset'))
max_concurrent_tasks = os.cpu_count()

def calculate_image_size(generated_str, font, start_x, start_y, spacing):
    global font_size
    image_width = 0
    image_height = 0

    for char in generated_str:
        image = Image.new("RGB", (100 * font_size, 100 * font_size), "white")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(target_font, font_size)
        # 计算字符的边界框
        testbox_x, testbox_y = 1, 1
        bbox = draw.textbbox((testbox_x, testbox_y), char, font=font)
        top_left = (bbox[0], bbox[1])
        top_right = (bbox[2], bbox[1])
        bottom_left = (bbox[0], bbox[3])
        bottom_right = (bbox[2], bbox[3])

        image_width = image_width + top_right[0] - top_left[0] + spacing
        image_height = max(image_height, bottom_left[1]-testbox_y)

        #print(f"{image_width}, {image_height}: {image_width} + {top_right[0]} - {top_left[0]} + {spacing}")
    return image_width+font_size+start_x, image_height+start_y+10

def gen_images_by_pillow(task):
    global font_size
    file_prefix = task["file_prefix"]
    outputFolder = task["outputFolder"]
    generated_str = task["generated_str"]
    target_font = task["target_font"]

    start_x, start_y = 1, 10
    spacing = 1
    #image_width = font_size * len(generated_str)
    #image_height = 480
    image_width, image_height = calculate_image_size(generated_str, target_font, start_x, start_y, spacing)

    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)
    box_positions = []

    for char in generated_str:
        font = ImageFont.truetype(target_font, font_size)

        # 计算字符的边界框
        bbox = draw.textbbox((start_x, start_y), char, font=font)
        top_left = (bbox[0], bbox[1])
        top_right = (bbox[2], bbox[1])
        bottom_left = (bbox[0], bbox[3])
        bottom_right = (bbox[2], bbox[3])

        # draw.rectangle([(bbox[0]-1, bbox[1]), (bbox[2]+1, bbox[3])], outline="blue", width=1)

        x0 = bottom_left[0]
        y0 = image_height - bottom_left[1]
        x1 = top_right[0]
        y1 = image_height - top_right[1]
        box_positions.append(f"{char} {x0} {y0} {x1} {y1} 0\n")

        # 在图片上绘制字符
        draw.text((start_x, start_y), char, font=font, fill="black")

        # 更新下一个字符的x位置
        start_x += bbox[2] - bbox[0] + spacing

    try:
        box_path = f'{outputFolder}/{file_prefix}.box'
        with open(box_path, 'w', newline='\n', encoding='utf-8') as f:
            f.writelines(box_positions)

        gt_file = f'{outputFolder}/{file_prefix}.gt.txt'
        with open(gt_file, 'w', newline='\n', encoding='utf-8') as f:
            f.write(generated_str)

        image.save(f"{outputFolder}/{file_prefix}.tif", format='TIFF')
    except Exception as e:
        print(f"Failed to generate image '{outputFolder}/{file_prefix}.tif'")

if os.path.exists(outputFolder):
    shutil.rmtree(outputFolder)
os.makedirs(outputFolder, exist_ok=True)

if os.path.exists(errorFolder):
    shutil.rmtree(errorFolder)
os.makedirs(errorFolder, exist_ok=True)


for fpathe,dirs,fs in os.walk('./ComplianceChars'):
    for f_name in fs:
        filepath=os.path.join(fpathe,f_name)
        print(f"{fpathe} ==> {f_name}")
        if filepath.endswith('.txt'):
            with open(filepath, 'r', encoding="utf-8") as inf:
                txt_chars = inf.read().replace(" ","").replace('\n', '').replace('\r', '')
                print(f_name,txt_chars)

                target_font = f_name.replace('.txt', '')
                index=0

                tasks = []

                for iterable_index, _ in enumerate(range(number_of_generated*len(txt_chars))):
                    length = random.randint(min_len_of_generated_str, max_len_of_generated_str)
                    generated_str = txt_chars[iterable_index % len(txt_chars)] + ''.join(random.choice(txt_chars) for _ in range(length))

                    file_prefix = f"{f_name.replace('.ttf', '').replace('.ttc', '').replace('.txt', '')}_{index}"
                    tasks.append(
                        {
                            "target_font": target_font,
                            "generated_str": generated_str,
                            "file_prefix": file_prefix,
                            "outputFolder": outputFolder,
                            # "unicharset_path": unicharset_path,
                            # "fonts_folder": fonts_folder,
                            "errorFolder": errorFolder
                        }
                    )
                    index += 1

                with ThreadPoolExecutor(max_workers=max_concurrent_tasks) as executor:
                    futures = [executor.submit(gen_images_by_pillow, item) for item in tasks]

                    for future in as_completed(futures):
                        pass
                        #result = future.result()
                        #print(result)
