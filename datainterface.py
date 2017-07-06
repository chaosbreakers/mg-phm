# _*_ coding:utf-8 _*_
"""data interface module"""
import re
import json
import cv2
from skimage import io
import matplotlib.pyplot as plt
import numpy as np


__version__ = '0.0.1'
__author__ = 'zhanglun'

def tiff_read(filename):
    """
    load image data from landsat into python workspace, data type is numpy dnarray
    """
    return io.imread(filename, as_grey=True)


def is_number(input_string):
    """
    if input_string includes number only, return corresponding number,
    otherwise return input_string
    """
    try:
        return float(input_string)
    except ValueError:
        pass

    try:
        import unicodedata
        return unicodedata.numeric(input_string)
    except (TypeError, ValueError):
        pass
    return input_string.strip('"')

def geojson_read(filename):
    """
    read landOwner.geojson and return corresponding data, data type is python dict

    """
    with open(filename) as f:
        data = json.load(f)

    return data

def get_band(imgcode, bandnumber, path=None):
    """
    imgcode:    例如LC81280332016208LGN00
                可以用文件名代替，例如LC81280332016208LGN00_B4.tif
    bandnumber: 1, 2, 3, 4...11
    """
    if bandnumber < 1 | bandnumber > 11:
        print 'ValueError: bandnumber should be 1~11'
        return 0
    if len(imgcode) < 21:
        print 'ValueError: imgcode has 21 letters'
        return 0
    imgcode = imgcode[:21]
    if imgcode[:2] != 'LC':
        print 'ValueError: imgcode begin with <LC>'
        return 0
    if imgcode[-2:] != '00':
        print 'ValueError: imgcode end with <00>'
        return 0
    filename = path + imgcode + '_B' + str(bandnumber) + '.tif'
    return tiff_read(filename)

def get_bqa(imgcode, path=None):
    """
    load BQA data
    """
    if len(imgcode) < 21:
        print 'ValueError: imgcode has 21 letters'
        return 0
    imgcode = imgcode[:21]
    if imgcode[:2] != 'LC':
        print 'ValueError: imgcode begin with <LC>'
        return 0
    if imgcode[-2:] != '00':
        print 'ValueError: imgcode end with <00>'
        return 0
    filename = path + imgcode + '_BQA' + '.tif'
    return tiff_read(filename)

def get_radiance(imgcode, bandnumber, path=None):
    """

    """
    if bandnumber in range(10, 12):
        n_str = str(bandnumber)
        s_g = 'RADIANCE_MULT_BAND_' + n_str + ' = '
        s_b = 'RADIANCE_ADD_BAND_' + n_str + ' = '
        if len(imgcode) < 21:
            print 'ValueError: imgcode has 21 letters'
            return 0
        imgcode = imgcode[:21]
        if imgcode[:2] != 'LC':
            print 'ValueError: imgcode begin with <LC>'
            return 0
        if imgcode[-2:] != '00':
            print 'ValueError: imgcode end with <00>'
            return 0
        filename = path + imgcode + '_MTL.txt'
        
        f = open(filename, 'r+')
    
        search_str_g = '(?<=' + s_g + ').*'
        search_str_b = '(?<=' + s_b + ').*'
    
        for line in f:
            s1 = re.search(search_str_g, line)
            s2 = re.search(search_str_b, line)
            if s1:
                gain = float(s1.group(0))
            elif s2:
                bias = float(s2.group(0))
    
        f.close()
    
        return gain, bias
    else:
        print('Bandnumber of get_radiance has to be in the range 10-11!')

def get_reflectance(imgcode, bandnumber, path=None):
    """

    """
    if bandnumber in range(1, 9):
        n_str = str(bandnumber)
        s_g = 'REFLECTANCE_MULT_BAND_' + n_str + ' = '
        s_b = 'REFLECTANCE_ADD_BAND_' + n_str + ' = '
        if len(imgcode) < 21:
            print 'ValueError: imgcode has 21 letters'
            return 0
        imgcode = imgcode[:21]
        if imgcode[:2] != 'LC':
            print 'ValueError: imgcode begin with <LC>'
            return 0
        if imgcode[-2:] != '00':
            print 'ValueError: imgcode end with <00>'
            return 0
        filename = path + imgcode + '_MTL.txt'
    
        f = open(filename, 'r+')
    
        search_str_g = '(?<=' + s_g + ').*'
        search_str_b = '(?<=' + s_b + ').*'
    
        for line in f:
            s1 = re.search(search_str_g, line)
            s2 = re.search(search_str_b, line)
            if s1:
                gain = float(s1.group(0))
            elif s2:
                bias = float(s2.group(0))
    
        f.close()
    
        return gain, bias
    else:
        print('Bandnumber of get_reflectance has to be in the range 1-9!')

def get_thermalconst(imgcode, bandnumber, path=None):
    """

    """
    if bandnumber in range(10, 12):
        n_str = str(bandnumber)
        s = 'K._CONSTANT_BAND_' + n_str + ' = '
        if len(imgcode) < 21:
            print 'ValueError: imgcode has 21 letters'
            return 0
        imgcode = imgcode[:21]
        if imgcode[:2] != 'LC':
            print 'ValueError: imgcode begin with <LC>'
            return 0
        if imgcode[-2:] != '00':
            print 'ValueError: imgcode end with <00>'
            return 0
        filename = path + imgcode + '_MTL.txt'
        search_str = '(?<=' + s + ').*'
    
        f = open(filename, 'r+')
        
        Ks = []
        for line in f:
            k = re.search(search_str, line)
            if k:
                Ks.append(float(k.group(0)))
    
        f.close()
    
        return Ks
    else:
        print('Band number has to be in the range 10-11!')
def get_date(imgcode, path=None):
    """
    """
    s = 'FILE_DATE ='
    if len(imgcode) < 21:
        print 'ValueError: imgcode has 21 letters'
        return 0
    imgcode = imgcode[:21]
    if imgcode[:2] != 'LC':
        print 'ValueError: imgcode begin with <LC>'
        return 0
    if imgcode[-2:] != '00':
        print 'ValueError: imgcode end with <00>'
        return 0
    filename = path + imgcode + '_MTL.txt'
    search_str = '(?<=' + s + ').*'
    
    f = open(filename, 'r+')

    for line in f:
            k = re.search(search_str, line)
            if k:
                file_date = k.group(0)
    f.close
    return file_date

def get_corner(imgcode, path=None):
    #读取坐标
    corner = np.zeros((4, 2))
    UL_LON = 'CORNER_UL_LON_PRODUCT' + ' = '
    UL_LAT = 'CORNER_UL_LAT_PRODUCT' + ' = '
    UR_LON = 'CORNER_UR_LON_PRODUCT' + ' = '
    UR_LAT = 'CORNER_UR_LAT_PRODUCT' + ' = '
    LL_LON = 'CORNER_LL_LON_PRODUCT' + ' = '
    LL_LAT = 'CORNER_LL_LAT_PRODUCT' + ' = '
    LR_LON = 'CORNER_LR_LON_PRODUCT' + ' = '
    LR_LAT = 'CORNER_LR_LAT_PRODUCT' + ' = '
    if len(imgcode) < 21:
        print 'ValueError: imgcode has 21 letters'
        return 0
    imgcode = imgcode[:21]
    if imgcode[:2] != 'LC':
        print 'ValueError: imgcode begin with <LC>'
        return 0
    if imgcode[-2:] != '00':
        print 'ValueError: imgcode end with <00>'
        return 0
    filename = path + imgcode + '_MTL.txt'

    f = open(filename, 'r+')

    search_UL_LON = '(?<=' + UL_LON + ').*'
    search_UL_LAT = '(?<=' + UL_LAT + ').*'
    search_UR_LON = '(?<=' + UR_LON + ').*'
    search_UR_LAT = '(?<=' + UR_LAT + ').*'
    search_LL_LON = '(?<=' + LL_LON + ').*'
    search_LL_LAT = '(?<=' + LL_LAT + ').*'
    search_LR_LON = '(?<=' + LR_LON + ').*'
    search_LR_LAT = '(?<=' + LR_LAT + ').*'

    for line in f:
        s1 = re.search(search_UL_LON, line)
        s2 = re.search(search_UL_LAT, line)
        s3 = re.search(search_UR_LON, line)
        s4 = re.search(search_UR_LAT, line)
        s5 = re.search(search_LL_LON, line)
        s6 = re.search(search_LL_LAT, line)
        s7 = re.search(search_LR_LON, line)
        s8 = re.search(search_LR_LAT, line)
        if s1:
            corner[0,0] = float(s1.group(0))
        elif s2:
            corner[0,1] = float(s2.group(0))
        elif s3:
            corner[1,0] = float(s3.group(0))
        elif s4:
            corner[1,1] = float(s4.group(0))
        elif s5:
            corner[2,0] = float(s5.group(0))
        elif s6:
            corner[2,1] = float(s6.group(0))
        elif s7:
            corner[3,0] = float(s7.group(0))
        elif s8:
            corner[3,1] = float(s8.group(0))

    f.close()

    return corner



    pass
    
if __name__ == '__main__':
    landOwnerdata = geojson_read('testdata/landOwners.geojson')
    s1 = geojson_read(r'testdata/1.geojson')
    s2 = geojson_read(r'testdata/2.geojson')
    s3 = geojson_read(r'testdata/3.geojson')
    s4 = geojson_read(r'testdata/4.geojson')
    s5 = geojson_read(r'testdata/5.geojson')
    s6 = geojson_read(r'testdata/6.geojson')
    s7 = geojson_read(r'testdata/7.geojson')
    s8 = geojson_read(r'testdata/8.geojson')
    s9 = geojson_read(r'testdata/9.geojson')
    s = [s1, s2, s3, s4, s5, s6, s7, s8 ,s9]
    print type(landOwnerdata)
    for index in range(len(s)):
        district = s[index]
        pointlist = []
        for item in district['features']:
            pointlist.append(item['geometry']['coordinates'][0])
        #plt.figure()
        for item in pointlist:
            xx = []
            yy = []
            for point in item:
                xx.append(point[0])
                yy.append(point[1])
            if index == 7:
                plt.plot(xx, yy,'k')
            else:
                plt.plot(xx, yy)
            plt.hold
    plt.show()