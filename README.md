# tesseract_train
Repository mentioned in https://youtu.be/KE4xEzFGSU8

https://github.com/tesseract-ocr/tessdata_best
https://github.com/tesseract-ocr/tesstrain
https://github.com/tesseract-ocr/tessdoc
https://github.com/tesseract-ocr/langdata_lstm
https://github.com/tesseract-ocr/tesseract.git

##ubuntu 18/24 简中
```
1. Init Ubuntu18/Ubuntu24

    sudo apt-get install libicu-dev libpango1.0-dev libcairo2-dev -y
    sudo apt-get install make git vim -y
    
    
    sudo apt update
    sudo apt install openssh-server -y
    sudo systemctl status ssh
    sudo systemctl enable ssh
    sudo ufw allow ssh
    sudo apt install git -y
    
    #sudo apt remove --autoremove tesseract-ocr tesseract-ocr-*
    sudo add-apt-repository ppa:alex-p/tesseract-ocr5
    sudo apt update
    sudo apt install tesseract-ocr -y
    tesseract --version
    
    
    mkdir -p ~/miniconda3
    cd ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    #rm ~/miniconda3/miniconda.sh
    source ~/miniconda3/bin/activate
    conda init --all
    
    conda remove -n tesstrain --all -y
    conda create -n tesstrain python=3.9 -y
    conda activate tesstrain
    pip install -r ~/tesseract_train/tesstrain/requirements.txt

2. Init dev envirement
    git clone --recursive https://github.com/liuwn01/tesseract_train.git

    or

    mkdir ~/tesseract_train
    cd ~/tesseract_train
    git clone https://github.com/tesseract-ocr/tesseract.git
    git clone https://github.com/tesseract-ocr/tesstrain


3. Prepare data for train

    cd ~/tesseract_train
    #从这个[tessdata_best](https://github.com/tesseract-ocr/tessdata_best)中下载对应语言的traineddata, 本测试使用eng.traineddata
    #把eng.traineddata文件放到~/tesseract_train/tesseract/tessdata目录下

    #TBD, how to generate training data

4. Train model
    cd ~/tesseract_train/tesstrain
    TESSDATA_PREFIX=../tesseract/tessdata make training MODEL_NAME=GB18030 START_MODEL=eng TESSDATA=../tesseract/tessdata MAX_ITERATIONS=10000



Others:
    #text2image --font=Apex Bold --text=./tesstrain/data/Apex-ground-truth\eng_97.gt.txt --outputbase=./tesstrain/data/Apex-ground-truth/eng_97 --max_pages=1 --strip_unrenderable_words --leading=32 --xsize=3600 --ysize=480 --char_spacing=1.0 --exposure=0 --unicharset_file=langdata/eng.unicharset --fonts_dir=./fonts --fontconfig_tmpdir=D:\09.Work\65.Interop\04.task\30.GBTasks\codes\tesseract_tutorial\tmp
    #text2image --fonts_dir /home/liuwn/tesseract_train/fonts --list_available_fonts --fontconfig_tmpdir /home/liuwn/tesseract_train/fonts
    
    cd ~/tesseract_train/tesstrain
    TESSDATA_PREFIX=../tesseract/tessdata make training MODEL_NAME=GB18030 START_MODEL=eng TESSDATA=../tesseract/tessdata MAX_ITERATIONS=10000
    #错误率参考: BCER train=61.069000%
    
    combine_tessdata -u eng.traineddata ./eng/eng
    combine_tessdata -u Apex.traineddata ./Apex/Apex
```
















