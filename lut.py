# 原理検証用スクリプト

import cv2
import numpy as np
import matplotlib.pyplot as plt

def tone(image, thresh):
    x = np.arange(256)
    y = np.zeros(256)
    y[: thresh+1] = (255/thresh)*x[: thresh+1]

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(x,y)
    ax.set_title("LUT_{}".format(thresh))
    plt.show()

    dst = cv2.LUT(image, y).astype(np.uint8)
    print(dst.dtype)

    return dst

if __name__ == "__main__":
    cv2.imshow("title", tone(cv2.imread('test.bmp', cv2.IMREAD_GRAYSCALE), 105))
    cv2.waitKey()