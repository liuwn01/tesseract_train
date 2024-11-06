python env: 
	#conda create -n label python=3.7 -y
	#conda activate label
	jupyterlab==3.6.8
	pillow==9.5.0


autolabel_ver1.py: Main Program
	- testdata-utf8.txt: The UTF-8 version of the GB test characters. Strings of specified lengths will be randomly drawn from it for labeling.
	- CharFontMapping.json: Mapping of each character in testdata-utf8.txt to its corresponding font file.
	- exception_strs.txt: All rectangular characters in testdata-utf8.txt will be replaced with ® (® is a character in the ASCII extended table).
	- TemplateDetails.json & Templates: Records the positions in jpg images where characters can be labeled (including start points, font size, and labeling length).
	- Generated: Folder for the generated jpg and json files (intermediate results).

Others/mapping_chars.py
	- Will iterate over all font files (ttc/ttf) in the specified folder and generate a txt file for comparison.
	  Generally, you can simply copy "C:\Windows\Fonts" to "./AllFonts".
	- dict-utf8.txt: The result of de-duplicating all characters in testdata-utf8.txt.
	- ALL_output.json: Generated file that records which font files each character matches.

CharFontMapping.json
	- Based on the aforementioned ALL_output.json, it will be re-matched and CharFontMapping.json will be generated.
	
```
listb = ["simsun.ttc","SimSunExtG.ttf","simsunb.ttf","SimSunExtB.ttf","msyh.ttc","arial.ttf","taile.ttf","ntailu.ttf", "monbaiti.ttf","micross.ttf","seguisym.ttf"]#  ,"segmdl2.ttf"
exception_char_list = None
with open("./exception_strs.txt", 'r', encoding='utf-8') as file:
    file_contents = file.read()
    exception_char_list = list(dict.fromkeys(file_contents.replace('\n', '').replace('\r', '')))
    print(exception_char_list)
exception_strs_font = "arial.ttf"

def find_best_match(value_list, priority_list):
    for priority in priority_list:
        for val in value_list:
            if priority in val:
                return val.replace("./AllFonts\\Fonts\\",'').replace("./AllFonts\\Fonts_2\\",'').replace('.txt','')
    
    if len(value_list) == 1:
        return value_list[0].replace("./AllFonts\\Fonts\\",'').replace("./AllFonts\\Fonts_2\\",'').replace('.txt','')
    elif len(value_list) == 0:
        return ""
    
    return value_list

import json
with open("./ALL_output.json", 'r', encoding='utf-8') as file:
    file_contents = file.read()
    parsed_json = json.loads(file_contents)
    for key, values in parsed_json.items():
        if key in exception_char_list:
            parsed_json[key] = exception_strs_font
            continue
            
        best_match = find_best_match(values, listb)
        parsed_json[key] = best_match  
    parsed_json['⑩'] = "simsun.ttc"
    parsed_json['®'] = "arial.ttf"

    # with open('./ALL_output_updated_1.json', 'w', encoding='utf-8') as json_file:
    #     json.dump(parsed_json, json_file, ensure_ascii=False, indent=4)
        
    with open('./CharFontMapping.json', 'w', encoding='utf-8') as json_file:
        json.dump(parsed_json, json_file, ensure_ascii=False, indent=4)
```







