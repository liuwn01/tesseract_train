import json
from PIL import Image, ImageDraw, ImageFont
#from IPython.display import display
import uuid
import shutil
import subprocess
import os


#sudo cp ./fonts/*.ttf /usr/share/fonts
#sudo cp ./fonts/*.ttc /usr/share/fonts
#sudo fc-cache -f -v

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

current_dir = os.path.dirname(os.path.abspath(__file__))
fonts_folder = os.path.abspath(os.path.join(current_dir, '..', '..', 'fonts'))
unicharset_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'langdata','eng.unicharset'))

for f in json_data:

    TARGET_FONT = f#"simsun.ttc"
    TARGET_FONT_PATH = f"{TARGET_FONT}"
    TARGET_FONT_TXT = f"./target_font_txt/{TARGET_FONT}.txt"
    outputFolder = f"./singlechar_{TARGET_FONT.replace('.ttf','').replace('.ttc','')}"
    errorFolder = f"{outputFolder}_E"

    def get_font_content():
        with open(TARGET_FONT_TXT, 'r', encoding="utf-8") as f:
            font_content = [line.strip() for line in f if line.strip()]
            return font_content[0]


    font_size = 32
    text = get_font_content()
    print(text)

    # 设置图片大小
    image_width = 360
    image_height = 480
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)

    # 设置默认字体和初始位置
    default_font = ImageFont.truetype(TARGET_FONT_PATH, font_size)  # 替换为你的默认字体
    start_x, start_y = 1, 50
    spacing = 1  # 字符间距

    # 记录字符顶点位置的列表
    char_positions = []
    gt_positions = []
    font_file = TARGET_FONT

    if os.path.exists(outputFolder):
        shutil.rmtree(outputFolder)
    os.makedirs(outputFolder, exist_ok=True)

    if os.path.exists(errorFolder):
        shutil.rmtree(errorFolder)
    os.makedirs(errorFolder, exist_ok=True)


    index = 0
    for char in text:
        # if index < 300:
        #     index += 1
        #     continue
        font = ImageFont.truetype(font_file, font_size)

        # 计算字符的边界框
        bbox = draw.textbbox((start_x, start_y), char, font=font)
        top_left = (bbox[0], bbox[1])
        top_right = (bbox[2], bbox[1])
        bottom_left = (bbox[0], bbox[3])
        bottom_right = (bbox[2], bbox[3])

        # draw.rectangle([(bbox[0]-1, bbox[1]), (bbox[2]+1, bbox[3])], outline="blue", width=1)

        char_positions.append({
            "char": char,
            "font": font_file,
            "top_left": top_left,
            "top_right": top_right,
            "bottom_left": bottom_left,
            "bottom_right": bottom_right
        })

        x0 = bottom_left[0]
        y0 = image_height - bottom_left[1]
        x1 = top_right[0]
        y1 = image_height - top_right[1]
        gt_position = f"{char} {x0} {y0} {x1} {y1} 0"

        # 在图片上绘制字符
        draw.text((start_x, start_y), char, font=font, fill="black")

        # 更新下一个字符的x位置
        start_x += bbox[2] - bbox[0] + spacing

        # 将字符顶点位置信息保存到JSON文件
        file_prefix = font_file.replace('.', '_')
        # with open(f'./{file_prefix}_char_positions.json', 'w', encoding='utf-8') as f:
        #     json.dump(char_positions, f, ensure_ascii=False, indent=4)

        box_path = f'{outputFolder}/{file_prefix}_{index}.box'
        with open(box_path, 'w', newline='\n', encoding='utf-8') as f:
            f.write(gt_position)  # 加上最后的换行符

        gt_file = f'{outputFolder}/{file_prefix}_{index}.gt.txt'
        with open(gt_file, 'w', newline='\n', encoding='utf-8') as f:
            f.write(char)  # 加上最后的换行符

        # 显示图片
        # display(image)

        # 保存图片
        # image.save(f"{outputFolder}/{file_prefix}_{index}.tif", format='TIFF')
        index += 1

        outputbase = gt_file.replace('.gt.txt', '')
        command = f'text2image --font="{FONT_MAPPINT[TARGET_FONT]}" --text={gt_file} --outputbase={outputbase} --max_pages=1 --strip_unrenderable_words --leading=32 --xsize=3600 --ysize=480 --char_spacing=1.0 --exposure=0 --unicharset_file={unicharset_path} --fonts_dir={fonts_folder} --fontconfig_tmpdir={fonts_folder}'
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout, result.stderr)
        except Exception as e:
            print(f"Command {command} generated an exception: {e}")

        try:
            size = os.path.getsize(box_path)  # 文件路径及文件名
            if size < 1:
                shutil.move(box_path,errorFolder)
                shutil.move(gt_file, errorFolder)
                shutil.move(box_path.replace('.box','.tif'), errorFolder)
        except Exception as e:
            print(f"Move file error: {box_path}")
