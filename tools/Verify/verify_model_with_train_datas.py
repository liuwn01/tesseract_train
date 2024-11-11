import json
from PIL import Image, ImageDraw, ImageFont
#from IPython.display import display
import uuid
import shutil
import subprocess
import os
import random
import pytesseract
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import argparse

def check_string_in_text(file_path, target_string):
    with open(file_path, 'r', encoding='utf-8') as file:
        return any(target_string in line for line in file)

def read_gt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().replace('\n', '').replace('\r', '')

def save_result(file_path, lines):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def image_to_string(filepath, lang):
    return pytesseract.image_to_string(Image.open(filepath), lang=lang).replace(" ","").replace('\n', '').replace('\r', '')

def get_result_file(file_path):
    global REBUILDCSV
    if os.path.exists(file_path) and not REBUILDCSV:
        return open(file_path, 'a', encoding='utf-8')
    else:
        return open(file_path, 'w', encoding='utf-8')

def handle_tasks(task):
    global TXT_TRAIN,TEMP_FOLDER
    file_prefix = task["file_prefix"]
    gt_index_prefix = task["gt_index_prefix"]
    filepath = task["filepath"]

    try:
        print(f"processing: {file_prefix}")
        tesseract_parsed_string = image_to_string(filepath, TESSERACT_LANG)
        gt_string = read_gt_file(f"{file_prefix}.gt.txt")
        isInTrain = check_string_in_text(TXT_TRAIN, f"{gt_index_prefix}.lstmf")
        isInEval = check_string_in_text(TXT_EVAL, f"{gt_index_prefix}.lstmf")
        # print(gt_index_prefix,isInTrain,isInEval)
        # print(gt_string, "|||", tesseract_parsed_string, SequenceMatcher(None, gt_string, tesseract_parsed_string).ratio())
        isMatched = False

        ratio = SequenceMatcher(None, gt_string, tesseract_parsed_string).ratio()
        dest_folder = None
        if ratio > 0.9999 or gt_string == tesseract_parsed_string:
            isMatched = True
            dest_folder = f"{TEMP_FOLDER}/matched"
        else:
            dest_folder = f"{TEMP_FOLDER}/unmatched"

        try:
            move_file(f"{file_prefix}.tif", dest_folder)
            move_file(f"{file_prefix}.box", dest_folder)
            move_file(f"{file_prefix}.gt.txt", dest_folder)
            move_file(f"{file_prefix}.lstmf", dest_folder)
        except Exception as e:
            print(f"Move file error: {file_prefix}")


        with lock:
            global result_file
            result_file.write(f"{gt_index_prefix},{int(isMatched)},{ratio},{int(isInTrain)},{int(isInEval)},'{gt_string}','{tesseract_parsed_string}'\n")
            result_file.flush()
    except Exception as e:
        print(f"Failed to process '{file_prefix}': {e}")
        raise e

def move_file(src, dest):
    if os.path.exists(src):
        shutil.move(src, dest)
        #print(f"File '{src}' moved to '{dest}' successfully.")
    #else:
        #print(f"Source file '{src}' does not exist.")

def copy_file(src, dest):
    if os.path.exists(src):
        shutil.copy2(src, dest)
        print(f"File '{src}' copied to '{dest}' successfully.")
    else:
        print(f"Source file '{src}' does not exist.")

def copy_directory(src_dir, dest_dir):
    if os.path.exists(src_dir):
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)

        shutil.copytree(src_dir, dest_dir)
        print(f"Directory '{src_dir}' copied to '{dest_dir}' successfully.")
    else:
        print(f"Source directory '{src_dir}' does not exist.")

TXT_TRAIN = "list.train"
TXT_EVAL = "list.eval"
TXT_GT = "all-gt"
TEMP_FOLDER = "./temp"
TESSERACT_LANG = "gb2"
lock = Lock()
max_concurrent_tasks = os.cpu_count()
tasks=[]
result_file = None
REBUILDCSV = False

def main(args):
    global TXT_TRAIN,TXT_EVAL,TXT_GT,TEMP_FOLDER,GROUPD_TRUTH_FOLDER,TESSERACT_LANG,result_file, REBUILDCSV

    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    os.makedirs(f"{TEMP_FOLDER}/matched", exist_ok=True)
    os.makedirs(f"{TEMP_FOLDER}/unmatched", exist_ok=True)

    #copy file
    tesstrain_data_root = args.dataroot
    TESSERACT_LANG = args.model
    GROUPD_TRUTH_FOLDER = f"{TESSERACT_LANG}-ground-truth"
    REBUILDCSV = bool(args.rebuildcsv)

    copy_file(os.path.join(tesstrain_data_root, f"{TESSERACT_LANG}/{TXT_TRAIN}"), "./")
    copy_file(os.path.join(tesstrain_data_root, f"{TESSERACT_LANG}/{TXT_EVAL}"), "./")
    copy_file(os.path.join(tesstrain_data_root, f"{TESSERACT_LANG}/{TXT_GT}"), "./")

    if not os.path.exists(f"./{GROUPD_TRUTH_FOLDER}") or bool(REBUILDCSV):
        copy_directory(os.path.join(tesstrain_data_root, f"{GROUPD_TRUTH_FOLDER}"), f"./{GROUPD_TRUTH_FOLDER}")

    try:
        result_file = get_result_file("./result.csv")

        for fpathe, dirs, fs in os.walk(GROUPD_TRUTH_FOLDER):
            for f_name in fs:
                filepath = os.path.join(fpathe, f_name)
                # print(f"{fpathe} ==> {f_name}")
                if filepath.endswith('.tif'):
                    file_prefix = filepath.replace(".tif", "")
                    gt_index_prefix = f_name.replace(".tif", "")
                    tasks.append(
                        {
                            "filepath": filepath,
                            "file_prefix": file_prefix,
                            "gt_index_prefix": gt_index_prefix
                        }
                    )
                    # handle_tasks(tasks[len(tasks)-1]) #for debugging

        with ThreadPoolExecutor(max_workers=max_concurrent_tasks) as executor:
            futures = [executor.submit(handle_tasks, item) for item in tasks]
            for future in as_completed(futures):
                pass

        # print(f"Total: {total_items}; Error_Items: {error_items}")
        print("Done.")
    except Exception as e:
        print(f"Failed to verify! {e}")
    finally:
        result_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="verify traineddata with train datas")

    parser.add_argument("--model", type=str, required=True, help="model name", default="gb2")
    parser.add_argument("--dataroot", type=str, default="../../tesstrain/data", help="where is tesstrain/data folder")
    parser.add_argument("--rebuildcsv", type=int, default=0, help="Whether to regenerate Result.csv")

    args = parser.parse_args()
    main(args)





