import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont
#from IPython.display import display
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
current_dir = os.path.dirname(os.path.abspath(__file__))
fonts_folder = os.path.abspath(os.path.join(current_dir, '..', '..', 'fonts'))
unicharset_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'langdata','eng.unicharset'))
max_concurrent_tasks = 1 #os.cpu_count(), Concurrent requests will result in files not being generated, waiting to be fixed


def gen_images_by_tesstrainocr(task):
    file_prefix = task["file_prefix"]
    outputFolder = task["outputFolder"]
    unicharset_path = task["unicharset_path"]
    fonts_folder = task["fonts_folder"]
    errorFolder = task["errorFolder"]
    generated_str = task["generated_str"]
    target_font = task["target_font"]

    gt_file = f'{outputFolder}/{file_prefix}.gt.txt'
    with open(gt_file, 'w', newline='\n', encoding='utf-8') as f:
        f.write(generated_str)

    outputbase = gt_file.replace('.gt.txt', '')
    command = f'text2image --font="{FONT_MAPPINT[target_font]}" --text={gt_file} --outputbase={outputbase} --max_pages=1 --strip_unrenderable_words --leading=32 --xsize=3600 --ysize=480 --char_spacing=1.0 --exposure=0 --unicharset_file={unicharset_path} --fonts_dir={fonts_folder} --fontconfig_tmpdir={fonts_folder}'
    print(command)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout, result.stderr)
    except Exception as e:
        print(f"Command {command} generated an exception: {e}")

    try:
        box_path = f'{outputFolder}/{file_prefix}.box'
        size = os.path.getsize(box_path)  # 文件路径及文件名
        if size < 1:
            shutil.move(box_path, errorFolder)
            shutil.move(gt_file, errorFolder)
            shutil.move(box_path.replace('.box', '.tif'), errorFolder)
    except Exception as e:
        print(f"Move file error: {box_path}")

def check_fonts_folder(fonts_folder):
    command = f'text2image --fonts_dir {fonts_folder} --list_available_fonts --fontconfig_tmpdir {fonts_folder}'
    print(command)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout, result.stderr)
        time.sleep(2)
    except Exception as e:
        print(f"Command {command} generated an exception: {e}")

#recommended to manually run cmd before running this py
#'text2image --fonts_dir <path_to_fonts_folder> --list_available_fonts --fontconfig_tmpdir <path_to_fonts_folder>'
check_fonts_folder(fonts_folder) # If the <uuid>.cache-7 file does not exist in the fonts folder, image generation will fail.

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
                            "unicharset_path": unicharset_path,
                            "fonts_folder": fonts_folder,
                            "errorFolder": errorFolder
                        }
                    )
                    index += 1

                with ThreadPoolExecutor(max_workers=max_concurrent_tasks) as executor:
                    futures = [executor.submit(gen_images_by_tesstrainocr, item) for item in tasks]

                    for future in as_completed(futures):
                        pass
                        #result = future.result()
                        #print(result)
