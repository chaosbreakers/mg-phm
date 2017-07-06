# -*- coding:utf-8 -*-
"""
some useful image processing method in RemoteSensing
"""
import numpy as np
import scipy.misc
import matplotlib.pyplot as plt
#from datainterface import metadata_read
#from skimage.transform import rotate
#from skimage import io

def mean_filter(pic, filter_num=None):
    """
    mean filter
    developed by wangyuxuan in MATLAB, converted to python by zhanglun.
    """
    if filter_num is None:
        filter_num = 200

    new_pic = np.zeros_like(pic)
    for ii in range(0, pic.shape[0], filter_num):
        for jj in range(0, pic.shape[1], filter_num):
            # print 'ii: ' + str(ii)
            # print 'jj: ' + str(jj)
            area = pic[ii:ii+filter_num, jj:jj+filter_num]
            # ending slice of the pic
            if ii == pic.shape[0] - pic.shape[0] % filter_num:
                area = pic[ii:,jj:jj+filter_num]
                if jj == pic.shape[1] - pic.shape[1] % filter_num:
                    area = pic[ii:,jj:]
                    
            blank_cnt = area[area == 0].size
            if blank_cnt == area.size:
                temp = np.zeros_like(area)
                new_pic[ii:ii+filter_num, jj:jj+filter_num] = temp
            else:
                average_value = area.sum() / (area.size - blank_cnt)
                temp = average_value * np.ones_like(area)
                new_pic[ii:ii+filter_num, jj:jj+filter_num] = temp

    return new_pic


"""
def mean_filter2D(pic, filter_num=None):
    if filter_num is None:
        filter_num = min(pic.shape[0:1])/100

    return cv2.blur(pic, (filter_num, filter_num))
"""

def fill_boundry(img, imgsize):
    """
    img is a numpy array, and imgsize is a tuple or list
    where imgsize[0] is width and imgsize[1] is hight.
    """
    record = np.zeros(imgsize)
    # left side
    # count = 1
    for ii in xrange(imgsize[0]):
        tmp = img[ii, :].nonzero()
        # tmp is a array consistes indexes of non-zero elements in img.
        if len(tmp[0]) != 0:
            #there are non-zero elements in line ii
            record[ii, 0:tmp[0][0]+1] = 65535
            record[ii, tmp[0][-1]:] = 65535
        else:
            record[ii, :] = 65535
    return np.uint16(record)

def pn_coordinate(imgshape, corner, geodata):
    if type(geodata) == np.ndarray:
        points = geodata
    else:
        points = []
        for item in geodata['features']:
            points.append(item['geometry']['coordinates'][0])
        points = np.array(points[0])
    
    loc = np.zeros_like(points)
    for i in range(points.shape[0]): 
        single_point = points[i,:]
        x1 = (single_point[0] - corner[0, 0])/(corner[1, 0] - corner[0, 0]) * imgshape[0]
        y1 = 1
        x2 = (single_point[0] - corner[2, 0])/(corner[3, 0] - corner[2, 0]) * imgshape[0]
        y2 = imgshape[1]
        x3 = 1
        y3 = (single_point[1] - corner[0, 1])/(corner[2, 1] - corner[0, 1])* imgshape[1]
        x4 = imgshape[0]
        y4 = (single_point[1] - corner[1, 1])/(corner[3, 1] - corner[1, 1])* imgshape[1]

        k1 = (y2 - y1)/(x2 - x1)
        k2 = (y4 - y3)/(x4 - x3)
        b1 = y1 - k1 * x1
        b2 = y4 - k2 * x4
        x = (b2 - b1)/(k1 - k2)
        y = k1 * x + b1
        loc[i, 0] = x
        loc[i, 1] = y
    return loc.astype(np.int), points

def pn_poly(img_all, corner, geodata):
    """
    """
    
    # firstly, calculate corresponding location of geodata points and extract gps points
    locs, gpspoints = pn_coordinate(img_all.shape, corner, geodata)
    # in geodata, first point and last point is identical, which is not acceptable in pn_poly
    # this is why last point is deleted
    locs = locs[:-1, :].astype(np.float)
    
    # a single town is small in img_all, to accelerate program running, 
    # Minimum circumscribed rectangle is calculated
    max_gpsx = gpspoints[:,0].max()
    max_gpsy = gpspoints[:,1].max()
    min_gpsx = gpspoints[:,0].min()
    min_gpsy = gpspoints[:,1].min()
    
    tmp = [[min_gpsx, max_gpsy],[max_gpsx, max_gpsy],[min_gpsx, min_gpsy],[max_gpsx, min_gpsy]]
    print type(tmp)
    rect_geodata = np.array(tmp)
    rect_locs, rect_gpspoints = pn_coordinate(img_all.shape, corner, rect_geodata)
    x_bias = rect_locs[:,0].min()-100
    y_bias = rect_locs[:,1].min()-100
    x_range = rect_locs[:,0].max() - rect_locs[:,0].min() + 200
    y_range = rect_locs[:,1].max() - rect_locs[:,1].min() + 200
    
    cover = np.zeros_like(img_all)
    # print 'points.shape: ' + str(points.shape)
    max_x = locs[:, 0].max()
    min_x = locs[:, 0].min()
    max_y = locs[:, 1].max()
    min_y = locs[:, 1].min()
    print 'poly min_x: ' + str(min_x) + '\t' + 'rect min_x: ' + str(x_bias)
    print 'poly max_x: ' + str(max_x) + '\t' + 'rect min_x: ' + str(x_bias + x_range)
    print 'poly min_y: ' + str(min_y) + '\t' + 'rect min_y: ' + str(y_bias)
    print 'poly max_y: ' + str(max_y) + '\t' + 'rect min_y: ' + str(y_bias + y_range)
    
    
    
    for i in range(x_bias, x_bias+x_range):     #range(img_all.shape[0]):
        if i < min_x or i > max_x:
            continue
        # print to show process
        if  i%10 == 0:
            print '\t' + 'IN imageprocess.pn_poly: ' + str(max_x) + '\t' + str(i) + '...'
        for j in range(y_bias, y_bias+y_range):  #range(img_all.shape[0]):
            
            if j < min_y or j > max_y:
                continue
            flag = False
            for k in range(locs.shape[0]):
                if k == locs.shape[0] - 1:
                    l = 0
                else:
                    l = k + 1
                
                m = (locs[k, 1] > j) != (locs[l, 1] > j)
                tmp = locs[l, 1] - locs[k, 1]
                if tmp == 0:
                    tmp = 0.001
                
                n = i < (locs[l, 0] - locs[k, 0]) * (j - locs[k, 1]) / tmp + locs[k, 0]
                if m and n:
                    flag = not flag
            
            if flag == True:
                cover[j, i] = 1
    
    return cover
                
def bresenham(img, points):

    cover = np.zeros_like(img)
    for i in range(points.shape[0] - 2):
        j = i + 1
        if points[i, 0] != points[j, 0]:
            k = (points[j, 1] - points[i ,1]) / float((points[j, 0] - points[i, 0]))
            flag = False
            if abs(k) > 1:
                flag = True
                k = 1.0 / k
                points[j, 0],points[j, 1] = points[j, 1],points[j, 0]
                points[i, 0],points[i, 1] = points[i, 1],points[i, 0]
            
            mi = min(points[i, 0], points[j, 0])
            ma = max(points[i, 0], points[j, 0])

            if mi == points[i, 0]:
                s = points[i, 1]
            else:
                s = points[j, 1]
            
            d = 0
            for ii in range(mi, ma):
                if flag == False:
                    cover[s, ii] = 1
                else:
                    cover[ii, s] = 1
                
                d = d + k
                if d > 1:
                    d -= 1
                    s += 1
                elif d <= -1:
                    d += 1
                    s -= 1
                
    return cover    






if __name__ == '__main__':
    
    # test sample of mean_filter()
    imgcode = 'LC81280332016320LGN00_B4'
    path = 'testdata/2-12833/'
    picture = scipy.misc.imread('filter_test.png')
    print type(picture)
    new_picture = mean_filter(picture, 10)
    plt.figure()
    plt.imshow(picture)
    plt.figure()
    plt.imshow(new_picture)
    scipy.misc.imsave('filtered.png',new_picture)
    plt.show()
    """
    """

    """
    # test sample of np_poly()
    x = 255 * np.random.rand(1000, 1000)
    x = x.astype(np.uint8)

    points = [[10, 10],[10, 500],[800, 10]]
    points = np.array(points)

    y = pn_poly(x, points)

    plt.imshow(x)
    plt.figure()
    plt.imshow(y)
    plt.show()
    

    img = 255 * np.random.rand(100, 100)
    img = img.astype(np.uint8)

    points = np.array([[10,10],[30,20],[60,60],[40,60],[20,80],[10, 10]])
    aa = bresenham(img, points)
    plt.imshow(aa)
    plt.show()
"""