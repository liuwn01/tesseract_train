# tesseract_train
Repository mentioned in https://youtu.be/KE4xEzFGSU8



##ubuntu 18/24 简中

[ubuntu 24.04 LTS ISO](https://mirrors.neusoft.edu.cn/ubuntu-releases/24.04.1/ubuntu-24.04.1-desktop-amd64.iso)

```
Releted Repos:
    https://github.com/tesseract-ocr/tessdata_best 
    https://github.com/tesseract-ocr/tesstrain
    https://github.com/tesseract-ocr/tessdoc
    https://github.com/tesseract-ocr/langdata_lstm
    https://github.com/tesseract-ocr/tesseract.git

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
    
2. Init dev envirement
    git clone --recursive https://github.com/liuwn01/tesseract_train.git

    or

        mkdir ~/tesseract_train
        cd ~/tesseract_train
        git clone https://github.com/tesseract-ocr/tesseract.git
        git clone https://github.com/tesseract-ocr/tesstrain

    cd ~/tesseract_train
    sudo cp ./fonts/*.ttf /usr/share/fonts
    sudo cp ./fonts/*.ttc /usr/share/fonts
    sudo fc-cache -f -v

    pip install -r ~/tesseract_train/tesstrain/requirements.txt

3. Prepare data for train

    cd ~/tesseract_train

    #download the traineddata that you want from https://github.com/tesseract-ocr/tessdata_best. (This test uses eng.traineddata), and update eng.traineddata to ~/tesseract_train/tesseract/tessdata
    #or
    cp ~/tesseract_train/langdata/eng.traineddata ~/tesseract_train/tesseract/tessdata

    #TBD, how to generate training data
    #Method 1: Using text2image cmd
        #Since abnormal characters cannot be processed, regular characters are currently used

        #Will generate fonts.config and cache file under fonts for call text2image
        text2image --fonts_dir ~/tesseract_train/fonts --list_available_fonts --fontconfig_tmpdir ~/tesseract_train/fonts 
        
        cd ~/tesseract_train/tools/Generate_Images/ComplianceChars
        #only simsun.ttc.txt use for testing
        ls | grep -v simsun.ttc.txt | xargs rm
            #rollback of rm operation: git restore .
        cd ..
        python gen_images.py #Modify 'number_of_generated' to change the number of images generated
        mkdir ~/tesseract_train/tesstrain/data
        #<model name what you want>-ground-truth, this testcase uses gb1
        mv ./output ~/tesseract_train/tesstrain/data/gb1-ground-truth
        
    #Method 2: Using Pillow
        #TBD
        cd ~/tesseract_train/tools/Generate_Images/ComplianceChars
        #only simsun.ttc.txt use for testing
        ls | grep -v simsun.ttc.txt | xargs rm
            #rollback of rm operation: git restore .
        python gen_images_with_pillow.py
        mkdir ~/tesseract_train/tesstrain/data
        #<model name what you want>-ground-truth, this testcase uses gb1
        mv ./output ~/tesseract_train/tesstrain/data/gb1-ground-truth

4. Train model
    cd ~/tesseract_train/tesstrain
    TESSDATA_PREFIX=../tesseract/tessdata make training MODEL_NAME=gb1 START_MODEL=eng TESSDATA=../tesseract/tessdata MAX_ITERATIONS=10000
        

        #make: *** 没有规则可制作目标“data/gb1-ground-truth/simsun_474.lstmf”，由“data/gb1/all-lstmf” 需求。 停止。
            please remove simsun_474.*: rm data/gb1-ground-truth/simsun_474.*

        #If you want to retrain the same model without being affected by previous data / check point
            rm data/gb1-ground-truth
            rm data/gb1

        #If you want to change the number of MAX_ITERATIONS, just run the command after changing MAX_ITERATIONS, It will continue training based on the previous check point.
        TESSDATA_PREFIX=../tesseract/tessdata make training MODEL_NAME=gb1 START_MODEL=eng TESSDATA=../tesseract/tessdata MAX_ITERATIONS=90000

        #After training is completed, gb1.traineddata will be saved in the ./data

5.Verify
    #TBD
    cd ~/tesseract_train/tesstrain
    sudo cp data/gb1.traineddata /usr/share/tesseract-ocr/5/tessdata/
    cp -r data/gb1-ground-truth ~/tesseract_train/tools/Verify/
    cp data/gb1/list.train ~/tesseract_train/tools/Verify/
    cp data/gb1/list.eval ~/tesseract_train/tools/Verify/
    cp data/gb1/all-gt ~/tesseract_train/tools/Verify/

    cd ~/tesseract_train/tools/Verify/
    #change GROUPD_TRUTH_FOLDER = 'gb1-ground-truth', TESSERACT_LANG = 'gb1'
    #pip install pytesseract
    python verify_model_with_train_datas.py
    #check result.csv #gt_file_prefix,isMatched,ratio(String Similarity),isInListTrainFile,isInListEvalFile,gt_file_string,tesseract_parsed_string

Others:
    #text2image --font=Apex Bold --text=./tesstrain/data/Apex-ground-truth\eng_97.gt.txt --outputbase=./tesstrain/data/Apex-ground-truth/eng_97 --max_pages=1 --strip_unrenderable_words --leading=32 --xsize=3600 --ysize=480 --char_spacing=1.0 --exposure=0 --unicharset_file=langdata/eng.unicharset --fonts_dir=./fonts --fontconfig_tmpdir=D:\09.Work\65.Interop\04.task\30.GBTasks\codes\tesseract_tutorial\tmp
    #text2image --fonts_dir ~/tesseract_train/fonts --list_available_fonts --fontconfig_tmpdir ~/tesseract_train/fonts
    
    cd ~/tesseract_train/tesstrain
    TESSDATA_PREFIX=../tesseract/tessdata make training MODEL_NAME=gb1 START_MODEL=eng TESSDATA=../tesseract/tessdata MAX_ITERATIONS=10000
    #Error rate reference: BCER train=61.069000%
    
    #Unpack traineddata file
    combine_tessdata -u eng.traineddata ./eng/eng
    combine_tessdata -u gb1.traineddata ./Apex/gb1
```
















