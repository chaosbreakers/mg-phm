# -*- coding:utf-8 -*-
"""
    image mosaicking
"""
import utm
import numpy as np
from skimage.transform import rotate
import matplotlib.pyplot as plt
import cv2
import datainterface


def gps2utm(corner):
    """
    converting from gps to mercator
    """
    utminfo = []
    for i in range(corner.shape[0]):
        coor = utm.from_latlon(corner[i, 1], corner[i, 0])
        utminfo.append(coor)  
    return utminfo

def utm2utmcorner(utminfo):
    """
    """
    utm_corner = np.zeros((4,2))
    for i in range(4):
        item = utminfo[i]
        utm_corner[i, 0], utm_corner[i, 1] = item[0], item[1]
    return utm_corner

def utm2gps(corner, utmzone):
    """
    """
    gps_corner = np.zeros((4,2))
    for i in range(4):
        point  =corner[i,:]
        utmxx = utmzone[i]
        gps_corner[i,1], gps_corner[i,0] = utm.to_latlon(point[0], point[1], utmxx[0], utmxx[1])
    return gps_corner

def cut_img_easy(img1, img2, img3, corner1, corner2, corner3):
    """
    cut remote sensing image and joint them together.
    area 1 is 129033, area 2 is 128033, area 3 is 128034.
    in corner*, the coordinate points sequence is UpperLeft UpperRight LowerLeft LowerRight
    """

    T = np.pi / 180.0
    size_1 = img1.shape[:2]
    size_2 = img2.shape[:2]
    size_3 = img3.shape[:2]

    # project GPS to map coordinates
    utm1 = gps2utm(corner1)
    utm2 = gps2utm(corner2)
    utm3 = gps2utm(corner3)
    
    #utmzone keeps utm zone number and letter for img_all
    #upper left is same as img1 upper left corner, which is utm1[0]
    #upper right is same as img2 upper right corner, which is utm2[1]
    #lower lert zone number is same as img1 upper left, while zone letter is same as img3 lower left
    #lower right is same as img3 lower right
    utmzone = ((utm1[0][2],utm1[0][3]),(utm2[1][2],utm2[1][3]),(utm1[0][2],utm3[2][3]),(utm3[3][2],utm3[3][3]))

    utm_corner1 = utm2utmcorner(utm1)
    utm_corner2 = utm2utmcorner(utm2)
    utm_corner3 = utm2utmcorner(utm3)
    # calculate roration angle
    xxx = (utm_corner1[1, 1] - utm_corner1[0, 1]) / (utm_corner1[1, 0] - utm_corner1[0, 0])
    yyy = (utm_corner1[3, 1] - utm_corner1[2, 1]) / (utm_corner1[3, 0] - utm_corner1[2, 0])
    theta_1 = (np.arctan(xxx) + np.arctan(yyy)) / 2.0 / T

    xxx = (utm_corner2[1, 1] - utm_corner2[0, 1]) / (utm_corner2[1, 0] - utm_corner2[0, 0])
    yyy = (utm_corner2[3, 1] - utm_corner2[2, 1]) / (utm_corner2[3, 0] - utm_corner2[2, 0])
    theta_2 = (np.arctan(xxx) + np.arctan(yyy)) / 2.0 / T

    xxx = (utm_corner3[1, 1] - utm_corner3[0, 1]) / (utm_corner3[1, 0] - utm_corner3[0, 0])
    yyy = (utm_corner3[3, 1] - utm_corner3[2, 1]) / (utm_corner3[3, 0] - utm_corner3[2, 0])
    theta_3 = (np.arctan(xxx) + np.arctan(yyy)) / 2.0 / T

    print '\t' + 'IN imagemosaicking.cut_img_easy: ' + 'rotating image...'
    img_1_c = rotate(img1, -theta_1)
    img_2_tmp = rotate(img2, -theta_2)
    img_3_tmp = rotate(img3, -theta_3)

    # get image shape after rotation
    size_1_c = img_1_c.shape
    size_2_tmp = img_2_tmp.shape
    size_3_tmp = img_3_tmp.shape

    # determing scale factor
    xxx = (utm_corner1[3, 0] - utm_corner1[2, 0]) / size_1[0]
    yyy = (utm_corner1[0, 1] - utm_corner1[2, 1]) / size_1[1]
    d_1 = np.array([xxx, yyy])
    d_1 = np.abs(d_1)

    xxx = (utm_corner2[3, 0] - utm_corner2[2, 0]) / size_2[0]
    yyy = (utm_corner2[0, 1] - utm_corner2[2, 1]) / size_2[1]
    d_2 = np.array([xxx, yyy])
    d_2 = np.abs(d_2)

    xxx = (utm_corner3[3, 0] - utm_corner3[2, 0]) / size_3[0]
    yyy = (utm_corner3[0, 1] - utm_corner3[2, 1]) / size_3[1]
    d_3 = np.array([xxx, yyy])
    d_3 = np.abs(d_3)

    #
    factor_1 = d_2 / d_1
    factor_2 = d_3 / d_1

    size_2_c = np.floor(size_2_tmp * factor_1).astype(np.int)
    img_2_c = cv2.resize(img_2_tmp, (size_2_c[1], size_2_c[0]))

    size_3_c = np.floor(size_3_tmp * factor_2).astype(np.int)
    img_3_c = cv2.resize(img_3_tmp, (size_3_c[1], size_3_c[0]))

    img1 = None
    img2 = None
    img3 = None
    img_2_tmp = None
    img_3_tmp = None

    # calculate origin point
    origin_1 = utm_corner1.mean(axis = 0)
    origin_2 = utm_corner2.mean(axis = 0)
    origin_3 = utm_corner3.mean(axis = 0)

    # calculate translation
    mv_1 = np.ceil((origin_2 - origin_1) / d_1)
    mv_2 = np.ceil((origin_3 - origin_1) / d_1)

    xxx = max(size_1_c[0]/2, mv_1[1] + size_2_c[0]/2)
    d_up = np.ceil(xxx).astype(np.int)

    xxx = max(size_1_c[0]/2, -mv_2[1]+size_3_c[0]/2)
    d_down = np.ceil(xxx).astype(np.int)

    d_left = np.ceil(size_1_c[1] / 2).astype(np.int)

    xxx = max(mv_1[0] + size_2_c[1]/2, mv_2[0]+size_3_c[1]/2)
    d_right = np.ceil(xxx).astype(np.int)
    
    print '\t' + 'IN imagemosaicking.cut_img_easy: ' + 'creating image_all...'
    img_all = np.zeros((d_up + d_down + 10, d_left + d_right + 10))

    # calculate new boundry
    UL = origin_1 + np.array([d_left, d_up]) * d_1
    UR = origin_1 + np.array([d_right - 2 * d_left + 10, d_up]) * d_1
    LL = origin_1 + np.array([d_left, -d_down -10]) * d_1
    LR = origin_1 + np.array([d_right - 2 * d_left + 10, -d_down - 10]) * d_1
    corner = np.concatenate((UL, UR, LL, LR)).reshape(4,2)
    
    print '\t' + 'IN imagemosaicking.cut_img_easy: ' + 'utm2gps...'
    gps_corner = utm2gps(corner, utmzone)
    
    # past img 1
    print '\t' + 'IN imagemosaicking.cut_img_easy: ' + 'pasting image 1...'
    dx_1 = d_up - np.ceil(size_1_c[0]/2) + 1
    dx_1 = dx_1.astype(np.int)
    dy_1 = int(0)
    img_all[dx_1+1:dx_1+size_1_c[0] + 1, dy_1+1:dy_1 + size_1_c[1] + 1] = img_1_c
    
    # past img 2
    print '\t' + 'IN imagemosaicking.cut_img_easy: ' + 'pasting image 2...'
    dy_2 = np.ceil(size_1_c[1]/2) + mv_1[0] - np.ceil(size_2_c[1]/2)
    dy_2 = dy_2.astype(np.int)
    dx_2 = d_up - np.ceil(size_2_c[0]/2)
    dx_2 = dx_2.astype(np.int)
    tmp_cover2 = img_all[dx_2+1:dx_2+size_2_c[0]+1, dy_2+1:dy_2+size_2_c[1]+1]
    cover_2=np.zeros_like(tmp_cover2)
    cover_2[tmp_cover2 != 0] = 1
    cover_2[img_2_c == 0] = 0
    cover_2 = 1 - cover_2 / 2
    img_all[dx_2+1:dx_2+size_2_c[0]+1, dy_2+1:dy_2+size_2_c[1]+1] = cover_2 * (tmp_cover2 + img_2_c)
    
    # past img 3
    print '\t' + 'IN imagemosaicking.cut_img_easy: ' + 'pasting image 3...'
    dy_3 = np.ceil(size_1_c[1]/2) + mv_2[0] - np.ceil(size_3_c[1]/2)
    dy_3 = dy_3.astype(np.int)
    dx_3 = np.ceil(size_1_c[0]/2) - mv_2[1] - np.ceil(size_3_c[0]/2)
    dx_3 = dx_3.astype(np.int)
    tmp_cover3 = img_all[dx_3+1:dx_3+size_3_c[0]+1, dy_3+1:dy_3+size_3_c[1]+1]
    cover_3=np.zeros_like(tmp_cover3)
    cover_3[tmp_cover3 != 0] = 1
    cover_3[img_3_c == 0] = 0
    cover_3 = 1 - cover_3 / 2
    img_all[dx_3+1:dx_3+size_3_c[0]+1, dy_3+1:dy_3+size_3_c[1]+1] = cover_3 * (tmp_cover3 + img_3_c)
    
    return img_all, gps_corner



if __name__ == '__main__':
    imgcode1 = 'LC81290332016215LGN00_MTL'
    imgcode2 = 'LC81280332016224LGN00_MTL'
    imgcode3 = 'LC81280342016224LGN00_MTL'
    path1 = 'testdata/1-12933/'
    path2 = 'testdata/2-12833/'
    path3 = 'testdata/3-12834/'
    corner1 = datainterface.get_corner(imgcode1, path1)
    corner2 = datainterface.get_corner(imgcode2, path2)
    corner3 = datainterface.get_corner(imgcode3, path3)
    img1 = datainterface.get_band(imgcode1, 3, path1)
    img2 = datainterface.get_band(imgcode2, 3, path2)
    img3 = datainterface.get_band(imgcode3, 3, path3)
    
    img, a = cut_img_easy(img1, img2, img3, corner1, corner2, corner3)
    img = cv2.resize(img, None, fx=0.1, fy=0.1)
    plt.imshow(img, 'gray')
    plt.show()