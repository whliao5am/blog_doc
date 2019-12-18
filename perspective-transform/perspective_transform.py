import numpy as np
import cv2
import argparse


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


if __name__ == "__main__":
    image = cv2.imread('image/example.png')
    pts = np.array([(73, 239), (356, 117), (475, 265), (187, 443)], dtype = "float32")

    warped = four_point_transform(image, pts)

    cv2.imshow("original", image)
    cv2.imshow("warped", warped)
    cv2.waitKey(0)
