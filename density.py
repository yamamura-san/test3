import cv2
import numpy as np
from skimage.morphology import convex_hull_image
import glob
from natsort import natsorted
import csv
import os

def dens(folder):

    # 画像ファイルの読み込み
    imgs = folder + "/*png"
    imgs_list = glob.glob(imgs)
    imgs_list = natsorted(imgs_list)

    # データを出力するcsv作成
    filename = "result.csv"
    with open(filename, "w", newline="") as f:
        header = ['img_name', 'evaluation value']
        writer = csv.writer(f)
        writer.writerow(header)    

        # 画像ごとに処理を実施
        for image in imgs_list:
            img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

            # 凸包計算
            img_hull = convex_hull_image(img)
            img_t = np.where(img_hull == False, 0, 255).astype(np.uint8)

            # 凸包の重心計算
            mu = cv2.moments(img_t, False)
            x,y= int(mu["m10"]/mu["m00"]) , int(mu["m01"]/mu["m00"])

            # 画像内での重心からのばらつき計算
            eva = 0
            h, w = img.shape[: 2]
            for i in range(h):
                for j in range(w):
                    eva =eva + (img[i][j])/255 * ((i-y)**2 + (j-x)**2)
            
            eva = int(eva)
            i = os.path.basename(image)
            writer.writerow([i, eva])

if __name__ == "__main__":
    dens("source")