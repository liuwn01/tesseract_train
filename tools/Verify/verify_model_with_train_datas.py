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

TXT_TRAIN = "./list.train"
TXT_EVAL = "./list.eval"
TXT_GT = "./all-gt"

TEMP_FOLDER = "./temp"
GROUPD_TRUTH_FOLDER = "./Apex-ground-truth"
TESSERACT_LANG = "Apex"

def check_string_in_text(file_path, target_string):
    with open(file_path, 'r', encoding='utf-8') as file:
        return any(target_string in line for line in file)

def get_unique_characters(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().replace('\n', '').replace('\r', '')

    unique_chars = ''.join(sorted(set(content)))
    return unique_chars

def read_gt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().replace('\n', '').replace('\r', '')

def save_result(file_path, lines):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def image_to_string(filepath, lang):
    return pytesseract.image_to_string(Image.open(filepath), lang=lang).replace(" ","").replace('\n', '').replace('\r', '')

if os.path.exists(TEMP_FOLDER):
    shutil.rmtree(TEMP_FOLDER)
os.makedirs(f"{TEMP_FOLDER}/matched", exist_ok=True)
os.makedirs(f"{TEMP_FOLDER}/unmatched", exist_ok=True)

unichars = get_unique_characters(TXT_GT)

total_items = 0
error_items = 0

summarize = []
for fpathe,dirs,fs in os.walk(GROUPD_TRUTH_FOLDER):
    for f_name in fs:
        filepath=os.path.join(fpathe,f_name)
        #print(f"{fpathe} ==> {f_name}")
        if filepath.endswith('.tif'):
            file_prefix = filepath.replace(".tif","")
            gt_index_prefix = f_name.replace(".tif","")
            tesseract_parsed_string = image_to_string(filepath, TESSERACT_LANG)
            gt_string = read_gt_file(f"{file_prefix}.gt.txt")
            isInTrain = check_string_in_text(TXT_TRAIN, f"{gt_index_prefix}.lstmf")
            isInEval = check_string_in_text(TXT_EVAL, f"{gt_index_prefix}.lstmf")
            #print(gt_index_prefix,isInTrain,isInEval)
            #print(gt_string, "|||", tesseract_parsed_string, SequenceMatcher(None, gt_string, tesseract_parsed_string).ratio())
            isMatched = False
            total_items += 1
            ratio = SequenceMatcher(None, gt_string, tesseract_parsed_string).ratio()
            if ratio > 0.9999 or gt_string == tesseract_parsed_string:
                try:
                    shutil.move(f"{file_prefix}.tif", f"{TEMP_FOLDER}/matched")
                    shutil.move(f"{file_prefix}.box", f"{TEMP_FOLDER}/matched")
                    shutil.move(f"{file_prefix}.gt.txt", f"{TEMP_FOLDER}/matched")
                except Exception as e:
                    print(f"Move file error: {file_prefix}")
            else:
                try:
                    error_items += 1
                    shutil.move(f"{file_prefix}.tif", f"{TEMP_FOLDER}/unmatched")
                    shutil.move(f"{file_prefix}.box", f"{TEMP_FOLDER}/unmatched")
                    shutil.move(f"{file_prefix}.gt.txt", f"{TEMP_FOLDER}/unmatched")
                except Exception as e:
                    print(f"Move file error: {file_prefix}")

            summarize.append(f"{gt_index_prefix},{isMatched},{ratio},{int(isInTrain)},{int(isInEval)},{tesseract_parsed_string},{gt_string}\n")#{os.linesep}

print(f"Total: {total_items}; Error_Items: {error_items}; error_ratio: {error_items/total_items*100.0}%")

save_result("./result.csv", summarize)