# -*- coding: utf-8 -*-
from datainterface import *
import numpy as np
import matplotlib.pyplot as plt
import cv2
from skimage import exposure
import matplotlib.image as mpimg
from scipy import misc

def butter2d_lp(shape, f, n, pxd=1):
    """Designs an n-th order lowpass 2D Butterworth filter with cutoff
   frequency f. pxd defines the number of pixels per unit of frequency (e.g.,
   degrees of visual angle)."""
    pxd = float(pxd)
    rows, cols = shape
    x = np.linspace(-0.5, 0.5, cols)  * cols / pxd
    y = np.linspace(-0.5, 0.5, rows)  * rows / pxd
    radius = np.sqrt((x**2)[np.newaxis] + (y**2)[:, np.newaxis])
    filt = 1 / (1.0 + (radius / f)**(2*n))
    return filt

def cloud_remove(img, bandnumber):
    """
    img: image
    bandnumber: bandnumber
    """
    if bandnumber < 1 | bandnumber > 11:
        print 'ValueError: bandnumber should be 1~11.'
        return 0
    # TODO D中元素表示各通道截至频率，需要修改一下
    D = [0.4, 0.4, 0.4, 0.4, 0.4, 0.4,\
        0.4, 0.4, 0.4, 0.4, 0.4]
    img1 = np.log(img + 1)

    fft_img = np.fft.fft2(img1)
    fft_img_shifted = np.fft.fftshift(fft_img)
    d0 = D[bandnumber - 1]
    h = butter2d_lp(img.shape, d0, 2)
    h = 1- h
    fft_new = fft_img_shifted * h
    new_image = np.real(np.fft.ifft2(np.fft.ifftshift(fft_new)))
    new_image = np.exp(new_image) + 1

    return new_image


if __name__ == '__main__':
    img = tiff_read('yun.tif').astype(np.double)
    img = cv2.resize(img, None, fx = 0.1, fy = 0.1)
    new_image = cloud_remove(img, 1)
    plt.figure()
    plt.imshow(new_image,'gray')
    plt.title('filtered')
    plt.figure()
    plt.imshow(img,'gray')
    plt.title('original')
    plt.show()