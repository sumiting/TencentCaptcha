
import cv2 as cv
import numpy as np
import math,random

# 寻找直线
def FindLines(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # 灰度化
    blurred = cv.GaussianBlur(image, (5, 5), 0)  # 高斯模糊
    canny = cv.Canny(blurred, 200, 400)  # canny边缘检测
    lines = cv.HoughLinesP(canny, 1, np.pi / 180, 20, minLineLength=15, maxLineGap=8)  # 霍夫变换寻找直线
    return lines[:, 0, :]  # 返回直线


# 这里对直线进行过滤
def FindResultLises(lines):
    resultLines = []
    for x1, y1, x2, y2 in lines:
        if (abs(y2 - y1) < 5 or abs(x2 - x1) < 5) and min(x1, x2) > 60:  # 只要垂直于坐标轴的直线并且起始位置在60像素以上
            resultLines.append([x1, y1, x2, y2])
    return resultLines


# 判断点是否在直线上
def distAbs(point_exm, list_exm):
    x, y = point_exm
    x1, y1, x2, y2 = list_exm
    dist_1 = math.sqrt(abs((y2 - y1) + (x2 - x1) + 1))  # 直线的长度
    dist_2 = math.sqrt(abs((y1 - y) + (x1 - x) + 1)) + math.sqrt(abs((y2 - y) + (x2 - x) + 1))  # 点到两直线两端点距离和
    return abs(dist_2 - dist_1)


# 交点函数 y = kx + b 求交点位置
def findPoint(line1, line2):
    poit_status = False
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    x = y = 0

    if (x2 - x1) == 0: # 垂直x轴
        k1 = None
        b1 = 0
    else:
        k1 = 1.0 * (y2 - y1) / (x2 - x1)
        b1 = y1 * 1.0 - k1 * x1 * 1.0

    if (x4 - x3) == 0:
        k2 = None
        b2 = 0
    else:
        k2 = 1.0 * (y4 - y3) / (x4 - x3)
        b2 = y3 * 1.0 - k2 * x3 * 1.0

    if k1 is None:
        if not k2 is None:
            x = x1
            y = k2 * x1 + b2
            poit_status = True
    elif k2 is None:
        x = x3
        y = k1 * x3 + b1
        poit_status = True
    elif k1 != k2:
        x = (b2 - b1) * 1.0 / (k1 - k2)
        y = k1 * x * 1.0 + b1 * 1.0
        poit_status = True

    return poit_status, [x, y]


# 求交点
def linePoint(resultLines):
    for x1, y1, x2, y2 in resultLines:
        for x3, y3, x4, y4 in resultLines:
            point_is_exist, [x, y] = findPoint([x1, y1, x2, y2], [x3, y3, x4, y4])   # 两线是否有交点
            if point_is_exist:
                dist_len1 = distAbs([x, y], [x1, y1, x2, y2])
                dist_len2 = distAbs([x, y], [x3, y3, x4, y4])
                if dist_len1 < 5 and dist_len2 < 5:  # 如果误差在5内我们认为点在直线上
                    # 判断交点在行直线中是左端点还是右端点
                    if abs(y2 - y1) < 5:
                        # x1是行直线
                        if abs(x1 - x) + abs(y1 - y) < 5:  # 左端点
                            return -1, [x, y]
                        else:
                            return 1, [x, y]
                    else:
                        # x2是行直线
                        if abs(x3 - x) + abs(y3 - y) < 5:
                            return -1, [x, y]
                        else:
                            return 1, [x, y]
    return 0, [0, 0]


# 通过加速减速模拟滑动轨迹
def moveTrack(xoffset):
    updistance = xoffset*4/5
    t = 0.2
    v = 0
    steps_list = []
    current_offset = 0
    while current_offset<xoffset:
        if current_offset<updistance:
            a = 2 + random.random() * 2
        else:
            a = -random.uniform(12,13)
        vo = v
        v = vo + a * t
        x = vo * t + 1 / 2 * a * (t * t)
        x = round(x, 2)
        current_offset += abs(x)
        steps_list.append(abs(x))
    # 上面的 sum(steps_list) 会比实际的大一点，所以再模拟一个往回拉的动作，补平多出来的距离
    disparty = sum(steps_list)-xoffset
    last1 = round(-random.random() - disparty, 2)
    last2 = round(-disparty-last1, 2)
    steps_list.append(last1)
    steps_list.append(last2)

    return steps_list

def run(path):
    img = cv.imread(path)
    lines = FindLines(img)
    lines = FindResultLises(lines)
    L_or_R, point_x = linePoint(lines)   # L_or_R 用于判断交点在行直线左边还是右边  后面拖动要用到
    print(L_or_R,point_x)
    xoffset = point_x[0]
    yoffset = point_x[1]
    if L_or_R == 1:
        x_offset = xoffset - 20  # 20是阴影快一半的长度  可根据实际情况调整
    else:
        x_offset = xoffset + 20
    moveList=moveTrack(x_offset)
    return moveList
if __name__ == '__main__':
    img = cv.imread('bg.jpg')
    lines = FindLines(img)
    lines = FindResultLises(lines)
    L_or_R, point_x = linePoint(lines)   # L_or_R 用于判断交点在行直线左边还是右边  后面拖动要用到
    print(L_or_R,point_x)
    xoffset = point_x[0]
    yoffset = point_x[1]
    if L_or_R == 1:
        x_offset = xoffset - 20  # 20是阴影快一半的长度  可根据实际情况调整
    else:
        x_offset = xoffset + 20

    cv.circle(img, (int(xoffset), int(yoffset)), 5, (0, 0, 255), 3)
    cv.imshow('circle', img)
    cv.waitKey(0)
    cv.destroyAllWindows()
