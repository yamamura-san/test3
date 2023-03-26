import PySimpleGUI as sg
import configparser
from pypylon import pylon
import cv2
import time
import datetime
import os
import glob
import numpy as np

# 撮影設定を読み込み、撮影用のGUI表示関数
def cap_win(videotime, exposuretime, fps, gain, x_min, x_max, y_min, y_max):

    # フォルダ作成
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d-%H-%M")
    dir_output = "result_" + current_time
    os.makedirs(dir_output, exist_ok=True)
    dir_output_src = dir_output +"/source"
    os.makedirs(dir_output_src, exist_ok=True)    

    i = 1
    #　ループ
    while True:
        layout = [[sg.Text('処理を選択してください')],
                  [sg.Text("{}回目の撮影です".format(i))],
                  [sg.Button('撮影する'), sg.Button('撮影終了')]]

        window = sg.Window('動画撮影処理', layout)

        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        #　ボタン１を押したときの処理
        elif event == '撮影する':
            # 動画撮影
            dir = cap(dir_output, videotime, exposuretime, fps, gain, x_min, x_max, y_min, y_max, i)
            # tmpフォルダの画像を平均化し、sourveフォルダにave画像を保存する
            ave(dir, dir_output_src, i)

            window.close()
            i = i+1

        #　ボタン２を押したときの処理
        elif event == '撮影終了':
            break

    window.close()
    return i-1, dir_output_src # 戻り値は撮影した回数とsource画像のフォルダ

# 撮影関数
def cap(dir_output, videotime, exposuretime, fps, gain, x_min, x_max, y_min, y_max, i):

    # フォルダ作成処理
    # 実行時に生成するtmpフォルダ名の作成
    output_tmp = dir_output + "/tmp"
    os.makedirs(output_tmp, exist_ok=True)

    # conecting to the first available camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

    # Grabing Continusely (video) with minimal delay
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    # exposure time seting
    camera.ExposureTime.SetValue(exposuretime)
    # framerate
    camera.AcquisitionFrameRateEnable.SetValue(True)
    camera.AcquisitionFrameRate.SetValue(fps)
    # gain setting
    camera.Gain.SetValue(gain)

    converter = pylon.ImageFormatConverter()

    # converting to opencv bgr format
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    # カメラの設定変更のためにdelayさせる
    time.sleep(1)
    i=0
    # 100枚撮影
    while i < 100:
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            # Access the image data
            image = converter.Convert(grabResult)
            img = image.GetArray()
            img= img[y_min : y_max, x_min : x_max]
            img = tone(img, 100)
            cv2.imwrite(output_tmp+'/img_'+str(i)+'.bmp', img)
            i +=1

    # Releasing the resource
    camera.StopGrabbing()

    return output_tmp

# 画像平均関数
def ave(dir, dir_output, k):
    #指定したディレクトリの画像を抽出
    imgs = dir+"/*bmp"
    imgs_list = glob.glob(imgs)

    #平均値を計算するための空のndarrayを作成
    img = cv2.imread(imgs_list[0],cv2.IMREAD_GRAYSCALE)
    h,w=img.shape[:2]
    base=np.zeros((h,w),np.uint32)

    #平均化処理
    for i in imgs_list:
        img = cv2.imread(i,cv2.IMREAD_GRAYSCALE)
        base += img
    base = base/(len(imgs_list))
    base=base.astype(np.uint8)
    cv2.imwrite(dir_output + "/ave_{0}.bmp".format(k), base)

    print("平均化処理完了")

# トーン補正関数
def tone(image, thresh):
    x = np.arange(256)
    y = np.zeros(256)
    y[: thresh+1] = (255/thresh)*x[: thresh+1]
    dst = cv2.LUT(image, y).astype(np.uint8)

    return dst

if __name__ == "__main__":
    cv2.imshow("title", tone(cv2.imread('test.bmp', cv2.IMREAD_GRAYSCALE), 105))
    print(cap_win(2, 1000, 100, 23, 500, 900, 0, 1000))
