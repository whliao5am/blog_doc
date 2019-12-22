import numpy as np
import argparse
import cv2


def order_points(pts):
    """整理点的顺序为左上-右上-右下-左下"""
    rect = np.zeros((4, 2), dtype = "float32")
    
    # 左上角点坐标和最小，右下角点坐标和最大
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # 右上角点坐标差最小，左下角点坐标差最大
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    """四点的透视变换，转为俯瞰"""
    rect = order_points(pts)
    (tl, tr, br, bl) = pts

    # 选取最大的两个边作为最后的图像边
    width1 = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width2 = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width1), int(width2))

    height1 = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height2 = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height1), int(height2))
    
    # 转化后的点坐标，还是对应顺序为左上-右上-右下-左下
    dst = np.array(
        [[0, 0],
        [max_width, 0],
        [max_width, max_height],
        [0, max_height]], dtype = "float32")

    # 调用opencv方法计算透视变换矩阵，然后应用透视变换。
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))
    return warped


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="dir path of imamges")
    args = parser.parse_args()

    image = cv2.imread(args.path)
    height, width, depth = image.shape
    ratio = image.shape[0] / 500.0
    origin = image.copy()
    image = cv2.resize(image, (int(width/height*500), 500))  # 转为图片高500，并且比例不变
    
    # 转为灰度图，高斯滤波，在进行canny边缘检测
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    _image, contours, hierarchy = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # 查找图中的轮廓
    cnts = sorted(contours, key=cv2.contourArea, reverse = True)[:5]  # 用轮廓面积排序，并取面积前五的轮廓
    
    # 循环轮廓
    for c in cnts:
        peri = cv2.arcLength(c, True)  # 轮廓周长，并且轮廓应该封闭
        approx = cv2.approxPolyDP(c, 0.02*peri, True)  # 进行多边形逼近，得到多边形的角点，并且轮廓应该封闭
        
        # 如果拟合的多边形角点为4，则可以认为是我们需要的外轮廓
        if len(approx) == 4:
            screen_cnt = approx
            break

    # 对图片进行透视变换
    warped = four_point_transform(origin, screen_cnt.reshape(4, 2) * ratio)
     
    # 对透视变换后的图片进行灰度化，然后进行取邻域值减去常数的高斯加权和的阈值二值化
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    warped = cv2.adaptiveThreshold(warped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 10)
    
    # 展示愿图片和处理后的图片，保存原图片。
    cv2.imshow("Original", cv2.resize(origin, (int(width/height*650), 650)))
    cv2.imshow("Scanned", cv2.resize(warped, (int(width/height*650), 650)))
    cv2.imwrite('Scanned.png', warped)
    cv2.waitKey(0)
