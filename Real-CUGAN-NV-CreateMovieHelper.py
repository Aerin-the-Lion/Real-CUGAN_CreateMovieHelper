'''

    @file Real-CUGAN-NV-CreateMovieHelper
    @brief Real-CUGANで楽に動画化するためのものです。
    @author Aerin the Lion(aka. Lost History)
    @date 3.12.2022

'''

# from signal import pause
from re import L
import subprocess
from subprocess import Popen, PIPE
import configparser
import os
import shutil
import sys
import ffmpy
import json

#from cv2 import cv2

#  --- 変数定義 ---
input_f = 'input_frames'
output_f = 'output_frames'
config = 'config.ini'
config_path = './' + config
model_path = './models-se/'

# モデル用クラス生成
class Models:
    def __init__(self, name, level):
        self.name = name
        self.level = level

# オブジェクト生成
no_denoise = Models('no-denoise', '-1')
denoise1x = Models('denoise level 1', '1')
denoise2x = Models('denoise level 2', '2')
denoise3x = Models('denoise level 3', '3')

'''
# OpenCVを使用したfpsの読み取り。だが、簡単な使用にするには、exeが膨大になってしまうので、断念。
# どのくらい大きくなるかというと、約300MB。ちょっと配布としては無理。体制的には、どちらもffprobeを使用しているので、これにこだわらなくてもOK
def Capture_fps(file):
    global fps
    cap = cv2.VideoCapture(file)
    fps = str(cap.get(cv2.CAP_PROP_FPS))
    # print('動画のfpsは', cap.get(cv2.CAP_PROP_FPS))
'''
# 外部のffprobeを使用したfpsの読み取り。
def Capture_fps(file):
    if not os.path.isfile('ffprobe.exe'):
        print('＋＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＋')
        print('Missing ffprobe.exe on directory under CUGAN exe file. You will probably get error if you goes on.')
        print('exeファイル直下にffprobe.exeが見当たりません。用意しないと、予期せぬアクシデントが起きます。')
        input('＋＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＋')
    global fps
    ff = ffmpy.FFprobe(
        global_options='-of json -show_streams -select_streams v',
        inputs={file: None},
    )
    res = ff.run(stdout=PIPE, stderr=PIPE)
    video_stream = res[0]
    video_detail = json.loads(video_stream).get('streams')[0]
    frame_rate = str(eval(video_detail.get('r_frame_rate')))
    fps = frame_rate
    print('動画のfpsは', fps)
    return fps

def Print_Three_Reader():
    print('.')
    print('.')
    print('.')

def DialogForModel():
    global DenoiseModel,ScaleSize
    DenoiseModel = ''
    ScaleSize =  0
    ModelNameNum =  0

    def ConvartDenoiseModel(ModelNameNum):
        if int(ModelNameNum) == 1:
            DenoiseModel = no_denoise
        elif int(ModelNameNum) == 2:
            DenoiseModel = denoise1x
        elif int(ModelNameNum) == 3:
            DenoiseModel = denoise2x
        elif int(ModelNameNum) == 4:
            DenoiseModel = denoise3x
        else:
            print('FatalError! You must select Denoise model choose between 1 and 4 with integer.')
            input('エラー！1から4の整数でデノイズレベルを指定してください！')
            sys.exit()
        return DenoiseModel

    def verifyScaleSize(ScaleSize):
        if not int(ScaleSize) <= 4:
            print("Fetal Error! You must select Denoise model choose between 2 and 4 with integer.")
            input("エラー！2から4の整数で倍率を指定してください！")
            sys.exit()
        else:
            return
                
    if DialogForUseModel == str(True):
        print('☆Starting with dialog mode...')
        print('☆対話形式による処理を開始します。')
        print('+＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝+')
        print('+// Denoise Level //+')
        print('+// Notice : Default is no-denoise. //+')
        print(' 1) ' +  no_denoise.name)
        print(' 2) ' +  denoise1x.name)
        print(' 3) ' +  denoise2x.name)
        print(' 4) ' +  denoise3x.name)
        print('+＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝+')

        print('Which are you want to use remove noise model? Select one from upper menu.')
        ModelNameNum = input('どのデノイズモデルを使用しますか？上記より選択してください。')

        Print_Three_Reader()
        print('+＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
        print('+// Scale Size //+')
        print(' 2)  x2 upscale')
        print(' 3)  x3 upscale')
        print(' 4)  x4 upscale')
        print('+＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')

        print('Select scale size what you want to from upper menu.')
        ScaleSize = input('倍率を上記から指定してください。')

        DenoiseModel = ConvartDenoiseModel(ModelNameNum)
        verifyScaleSize(ScaleSize)

        print('Selected noise model : ' + str(DenoiseModel.name) + '.')
        print('Selected scale size : ' + str(ScaleSize) + 'x .')
        print('使用するデノイズモデルは : ' + str(DenoiseModel.name) + ' です。')
        print('使用する倍率は : ' + str(ScaleSize) + 'x です。')
        return DenoiseModel, ScaleSize

    else:
        print('☆Starting with Config mode instead of Dialog one.')
        print('☆対話を省略し、configファイルから読み取ります。')
        config = configparser.ConfigParser(comment_prefixes=';', allow_no_value=True)
        config.read(config_path, encoding='UTF-8')
        ModelNameNum = config.get('DEFAULT', 'UseModel')
        ScaleSize = config.get('DEFAULT', 'ScaleSize')

        DenoiseModel = ConvartDenoiseModel(ModelNameNum)
        verifyScaleSize(ScaleSize)

        print('Selected noise model : ' + str(DenoiseModel.name) + '.')
        print('Selected scale size : ' + str(ScaleSize) + 'x です。')
        print('使用するデノイズモデルは : ' + str(DenoiseModel.name) + ' です。')
        print('使用する倍率は : ' + str(ScaleSize) + 'x です。')
        return DenoiseModel, ScaleSize

def Make_file(file):
    if not os.path.exists(file):
        print(str(file),'is created cuz it not exists on the directory.')
        print(str(file),'がないため、新規作成します。')
        os.mkdir(file)

def Import_config(file):
    global config,Bitrate,Codec,Extention,DialogForUseModel,ChromaSubsampling,SyncGapMode,TTA_Mode
    #  --- コンフィグ読み取り ---
    config = configparser.ConfigParser(comment_prefixes=';', allow_no_value=True)
    if not os.path.exists(file):
        print(str(file),'is created cuz it not exists on the directory.')
        print(str(file),'がないため、新規作成します。')
        config['DEFAULT'] = {
            'DialogForUseModel': 'True',
            '; Default = True ; if you use config setting then switch to False.':'',
            ';				  ; もしconfig.iniから読み取る場合は、Falseに切り替えてください。':'',
            'Codec': 'hevc_nvenc',
            '; Default = h264_nvenc, hevc_nvenc, libx264 ...etc':'',
            'Bitrate': '200M',
            '; Default = 200M ; if you feels huge the value, decrease it.':'',
            ';				  ; もし数字が大きいと感じた場合は、下げてください。':'',
            'Extension': 'png',
            '; Default = png ; png,jpg,webp':'',
            'ChromaSubsampling': 'yuv420p',
            '; Default = yuv420p ; yuv420p, yuv444p..(or more... plz read FFmpeg official site.)':'',
            '; --- !! These settings enables when DialogForUseModel is False !! ---':'',
            '; --- !! これらの設定はDialogForUseModelがFalseの場合に有効化されます !! ---':'',
            'UseModel': '1',
            '; Default = 1 : no-denoise':'',
            '; Models list on below for UseModel':'',
            '; 1 : no-denoise 				(default)':'',
            '; 2 : denoise1x':'',
            '; 3 : denoise2x':'',
            '; 4 : denoise3x':'',
            'ScaleSize': '2',
            '; Default = 2 ; Switch ScaleSize between 2 and 4 with integer.':'',
            '				  ; 2から4の整数で倍数を切り替えてください。':'',
            'SyncGapMode': '3',
            '; Default = 3 ; Switch ScaleSize between 0 and 3 with integer.':'',
            '				  ; 0から3の整数で倍数を切り替えてください。':'',
            'TTA-Mode': 'False',
            '; Default = False ; Switch if you want to use tta':'',
            '				  ; True or False':'',
        }
        with open(file, 'w') as file:
            config.write(file)

    # 同じファイルパス上にあることを認識させる
    # ↓exe化の場合は、こちらを使用
    #path = os.path.dirname(sys.executable)
    # ↓pyの場合は、こちらを使用
    #path = os.path.join(os.path.dirname(__file__), 'config.ini')
    #　こちらは相対パスにて設定、config.iniはexe/pyファイルの直下
    config.read(config_path, encoding='UTF-8')
    Bitrate = config.get('DEFAULT', 'Bitrate')
    Codec = config.get('DEFAULT', 'Codec')
    Extention = config.get('DEFAULT', 'Extension')
    ChromaSubsampling = config.get('DEFAULT', 'ChromaSubsampling')
    DialogForUseModel = config.get('DEFAULT', 'DialogForUseModel')
    SyncGapMode = config.get('DEFAULT', 'SyncGapMode')
    TTA_Mode = config.get('DEFAULT', 'TTA-Mode')

    def is_TTA_mode(Config_TTA_Mode):
        if Config_TTA_Mode == "True":
            TTA_Mode = "-x"
        elif Config_TTA_Mode == "False":
            TTA_Mode = ""
        else:
            print('Config.TTA_Mode : Error : please set True or False.')
            print('Config.TTA_Mode : Setted Disable TTA.')
            TTA_Mode = ""
        return TTA_Mode
    TTA_Mode = is_TTA_mode(TTA_Mode)
    

# フォルダーを作成
def Make_Files():
    Make_file(input_f)
    Make_file(output_f)

# フォルダ内が空かを確認する簡単な関数
def is_empty(dir_path: str) -> bool:
    return len(os.listdir(dir_path)) == 0
    
# 前に作成した画像がある場合は警告
def Alert_RemainingOldCreated():
    if is_empty(input_f + '/') == False:
        print('＋＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＋')
        print('・Input folder has still some files. Remove all of them otherwise you could have get some bug.')
        print('・Nevertheless if you goes on, please press any key.')
        print('・前回の連番作成した連番画像があります。バグが起きる可能性があるため、取り除いてください。')
        print('・それでも行う場合はなにかキーを押すと作業に入ります。')
        input('＋＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＋')

# exeファイルを起動したあとのcmd画面にD&Dをしたファイルを読み取り
def Filein():
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    print('・Please Drag and Drop on the screen your file.')
    print('・ファイルを画面上にドラッグアンドドロップしてください。')
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    global filename
    global basename
    global basename_without_ext
    filename = input()
    print('Debug:Full pass is:' + filename)
    basename = os.path.basename(filename)
    print('Debug:basename is:', basename)
    basename_without_ext = os.path.splitext(os.path.basename(filename))[0]
    Print_Three_Reader()
    return filename, basename, basename_without_ext

# D&Dした動画を入力、png連番を「input_frames」内に作成。
def Make_Video_to_Consecutive_Pictures():
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    print('・Creating consecutive pictures of original video…')
    print('・動画の連番を作成しています…')
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    Print_Three_Reader()
    cmd_text = 'ffmpeg -i ' + basename + ' -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 -vcodec png .\input_frames\%08d.png'
    print(cmd_text)
    subprocess.call(cmd_text, shell=True)
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    print('・Finished create consecutive pictures of original video.')
    print('・動画の連番を終了しました。')
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    Print_Three_Reader()

# うまく作れていない場合は警告文
def Check_Consecutive_Pictures():
       if not is_empty(input_f + '/') == False:
            print('＋＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＋')
            print('・It seems something wrong. If your files has 2 byte or special characters, remove it and try again.')
            print('・And you must put your file directory under the folder of CUGAN exe file.')
            print('・処理がうまくできていません。動画名にスペースや特殊文字を使用していませんか？アンダーバーなどで代用するようにしてください。')
            print('・また、使用するファイルはexe直下である必要があります。')
            input('＋＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＝＝＝＝＝!Alert!＝＝＝＝＝＝＝＋')
            sys.exit()

def SuperResolution_exe():
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    print('・Running Super-resolution process with CUGAN…')
    print('・超解像処理を実行します…')
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    Print_Three_Reader()

    cmd_text = 'realcugan-ncnn-vulkan.exe -i input_frames/ -o output_frames/ -n ' + DenoiseModel.level + ' -s ' + ScaleSize + '-f ' + Extention + ' -c' + SyncGapMode + TTA_Mode
    subprocess.call(cmd_text, shell=True)

    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    print('・Finished Super-resolution process')
    print('・超解像処理を終了しました。')
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    Print_Three_Reader()

def Combining_Picture():
    Normal = 'ffmpeg -framerate ' + fps + ' -i .\output_frames\%08d.png -i "' + basename + '" -map 0:v:0 -map 1:a:0 -strict -2 -vcodec ' + Codec + ' -acodec copy -b:v ' + Bitrate + ' -pix_fmt ' + ChromaSubsampling + ' -sws_flags spline+accurate_rnd+full_chroma_int -vf "colorspace=bt709:iall=bt601-6-625:fast=1" -color_range 1 -colorspace 1 -color_primaries 1 -color_trc 1 -r ' + fps + ' "'+ basename_without_ext +'_enhanced.mp4"'
    No_Music = 'ffmpeg -framerate ' + fps + ' -i .\output_frames\%08d.png -i "' + basename + '"-vcodec ' + Codec + ' -b:v ' + Bitrate + ' -pix_fmt ' + ChromaSubsampling + ' -sws_flags spline+accurate_rnd+full_chroma_int -vf "colorspace=bt709:iall=bt601-6-625:fast=1" -color_range 1 -colorspace 1 -color_primaries 1 -color_trc 1 -r ' + fps + ' "'+ basename_without_ext +'_enhanced_nomusic.mp4"'
    Music_MP3 = 'ffmpeg -framerate ' + fps + ' -i .\output_frames\%08d.png -i "' + basename + '"-vcodec ' + Codec + ' -ab 320k -acodec libmp3lame -b:v ' + Bitrate + ' -pix_fmt ' + ChromaSubsampling + ' -sws_flags spline+accurate_rnd+full_chroma_int -vf "colorspace=bt709:iall=bt601-6-625:fast=1" -color_range 1 -colorspace 1 -color_primaries 1 -color_trc 1 -r ' + fps + ' "'+ basename_without_ext +'_enhanced_nomusic.mp4"'
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    print('・Combining output pictures…')
    print('・連番の結合を実行します…')
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    Print_Three_Reader()

    # 最初の処理。動画の音声を連番動画に入れ込む。
    cmd_text = Normal
    subprocess.call(cmd_text, shell=True)

    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    print('・Checking the phase is finished correctly')
    print('・連番の結合が正しく終えたかチェックします…')
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    Print_Three_Reader()

    enhanced_name = basename_without_ext + '_enhanced.mp4'
    if not os.path.isfile(enhanced_name):
        # ファイルが無い場合。音声が無い場合にこの処理となり、音声オフで出力する。
        print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
        print('・Failed create movie. Retry Combining output pictures with safe mode…')
        print('・失敗を確認。再処理を実行…')
        print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
        Print_Three_Reader()

        cmd_text = No_Music
        subprocess.call(cmd_text, shell=True)

    elif os.path.getsize(enhanced_name) == 0:
            print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
            print('・Failed create movie. Retry Combining output pictures with safe mode…')
            print('・失敗を確認。再処理を実行…')
            print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
            Print_Three_Reader()

            # 再処理。音声をmp3で出力をする。
            cmd_text = Music_MP3
            subprocess.call(cmd_text, shell=True)

    else:
        print('・Checked it correctly')
        print('・正常に処理したことを確認しました。')

    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    print('・Finished combine picture to create movie.')
    print('・連番の結合を終了しました。')
    print('＋＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＋')
    Print_Three_Reader()

def Delete_Files():
    def yes_no_input():
        while True:
            print('Delete temp files?(yes/no)')
            choice = input('作成時に出たファイルを削除しますか？(yes/no)').lower()
            if choice in ['y', 'ye', 'yes']:
                return True
            elif choice in ['n','no']:
                return False

    ask_delete = yes_no_input()
    if bool(ask_delete) == True:
        shutil.rmtree(input_f)
        shutil.rmtree(output_f)
        if(os.path.isfile(basename_without_ext + '_music.wav')):
            os.remove(basename_without_ext + '_music.wav')
    elif bool(ask_delete) == False:
        print('Cancel delete files.')
        print('ファイルの削除を行いません。')
    elif ask_delete == 0:
        print('Incorrect input and cancel delete files.')
        print('不正な値です。ファイルの削除を行いません。')
    else:
        print('Incorrect input and cancel delete files.')
        print('不正な値です。ファイルの削除を行いません。')

def Main():
    Import_config(config)
    Make_Files()
    Alert_RemainingOldCreated()
    DialogForModel()
    Filein()
    Capture_fps(basename)
    Make_Video_to_Consecutive_Pictures()
    Check_Consecutive_Pictures()
    SuperResolution_exe()
    Combining_Picture()
    Delete_Files()

    print('Finished all process.')
    print('処理を終了しました。')
    input()

Main()





