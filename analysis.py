# -*- coding: utf-8 -*-
import datainterface
import numpy as np
import matplotlib.pyplot as plt

def get_plant(imgcode, path=None):
    """
    例如:LC81280332016208LGN00
    """
    b4_img = datainterface.get_band(imgcode, 4, path).astype(np.float)
    b5_img = datainterface.get_band(imgcode, 5, path).astype(np.float)
    gain4, bias4 = datainterface.get_reflectance(imgcode, 4, path)
    gain5, bias5 = datainterface.get_reflectance(imgcode, 5, path)

    b4 = b4_img * gain4 + bias4
    b5 = b5_img * gain5 + bias5
    b4 = b4_img * gain4
    b5 = b5_img * gain5
    summery = b4 + b5
    summery[summery == 0] = 0.0001
    ndvi = (b5 - b4) / summery
    
    ndvi_max = ndvi[ndvi != 1].max()
    ndvi_min = ndvi[ndvi != -1].min()
    if ndvi_max <= 0.9:
        ndvi[ndvi == 1] = ndvi_max
    if ndvi_min >= -0.9:
        ndvi[ndvi == -1] = ndvi_min
    
    vfc = np.zeros_like(ndvi)
    vfc[ndvi < 0.05] = 0
    vfc[ndvi >= 0.05] = (ndvi[ndvi >= 0.05] - 0.05)/0.65

    return ndvi, vfc

def get_temperature(imgcode, path=None):

    b11_img = datainterface.get_band(imgcode, 11, path).astype(np.float)
    K1, K2 = datainterface.get_thermalconst(imgcode, 11, path)
    gain, bias = datainterface.get_radiance(imgcode, 11, path)
    b11 = b11_img * gain + bias
    Tb = np.zeros_like(b11)
    Tb[b11 != 0] = K2 / np.log(K1 / b11[b11 != 0] + 1)
    Ts=Tb/(1+12.5*10 ** -6*Tb*1.38*10**-23/(6.626*10**-34*2.998*10**8)*np.log(0.965))-273.15
    Ts[Ts < -80] = 0
    return Ts

def get_drought(ndvi, Ts, bqa):#未确定是否添加BQA图层
    """ 
    """
    bqa_cover = np.zeros_like(bqa)
    count = np.unique(bqa)
    count = np.sort(count)
    bqa_cover[bqa > count[2]] = 1#bqa
    bqa_cover[ndvi < 0] = 1#water
    Ts_cover = np.zeros_like(Ts)
    ndvi_cover = np.zeros_like(ndvi)
    Ts_cover[Ts != 0] = 1
    ndvi_cover[ndvi != 0] = 1
    print 'Ts cover\t',
    print Ts_cover.mean()
    print 'ndvi_cover\t',
    print ndvi_cover.mean()
    if Ts_cover.mean() < ndvi_cover.mean():
        cover = Ts_cover
    else:
        cover = ndvi_cover
    ndvi_tmp = np.floor(ndvi * 255)/255
    ndvi_tmp =ndvi_tmp * cover
    ndvi_tmp[cover == 0] = 99
    Ts = Ts * cover + bqa_cover * 1000.0
    select = np.unique(ndvi_tmp[ndvi_tmp != 99])
    select = select[select >= 0]#排除水体
    select = select.tolist()
    Ts_max = np.zeros_like(select)
    Ts_min = np.zeros_like(select)
    TVDI = np.zeros_like(ndvi)
    for index in range(len(select)):
        tmp = ndvi_tmp == select[index]
        xx = Ts[tmp]
        # print xx.shape
        # print index
        try:
            Ts_max[index] = xx[xx < 200].max()
            Ts_min[index] = Ts[tmp].min()
        except ValueError:
            Ts_max[index] = 0
            Ts_min[index] = 0
        if xx.shape[0] != 0:
            pass
        else:
            pass
        #TODO may need revision
        # xx = Ts[tmp]
        # cover1 = cover.copy()
        # cover1[ndvi_tmp < 0] = 0
        # Ts_min[index] = xx[xx > 0].min()
        TVDI[tmp] = (Ts[tmp] - Ts_min[index]) / (Ts_max[index] - Ts_min[index] + 0.0001)
    TVDI = TVDI * (1 - bqa_cover)
    TVDI = TVDI * cover
    return TVDI, cover

def  vfc_divide(vfc, ndvi):
    #覆盖度低于0.1视为裸土，0.1-0.2视为低覆盖，0.2-0.5为中覆盖，0.5以上为高覆盖
    
    rows = vfc.shape[0]
    cols = vfc.shape[1]
    vfc_f = np.zeros((rows, cols, 3))

    water_color = [49, 16, 248]
    mud_color = [164, 129, 100]
    little_grass = [118, 216, 134]
    median_grass = [56, 194, 79]
    alotof_grass = [37, 127, 52]

    cover = np.zeros_like(ndvi)
    cover[ndvi != 0] = 1
    vfc[cover == 0] = -1

    vfc_f[vfc >= 0,:] = np.array(mud_color)
    vfc_f[vfc > 0.1, :] = np.array(little_grass)
    vfc_f[vfc > 0.2, :] = np.array(median_grass)
    vfc_f[vfc > 0.5, :] = np.array(alotof_grass)
    vfc_f[ndvi < 0, :] = np.array(water_color)

    return vfc_f.astype(np.uint8)

def tvdi_divide(tvdi, ndvi, cover):
    # 0~0.2水体；0.2~0.4湿润；0.4~0.6正常；0.6~0.8干旱；0.8~1.0严重干旱
    # http://tool.oschina.net/commons?type=3
    rows = tvdi.shape[0]
    cols = tvdi.shape[1]
    tvdi_f = np.zeros((rows, cols, 3))
    
    water_color = [49, 16, 248]
    humid_color = [0, 205, 102]
    norm_color = [84, 255, 159]
    drought_color = [255, 130, 71]
    severe_color = [205, 85, 85]
    
    tvdi[cover == 0] = -1
    tvdi_f[tvdi >= 0,:] = np.array(water_color)
    tvdi_f[tvdi > 0.2, :] = np.array(humid_color)
    tvdi_f[tvdi > 0.4, :] = np.array(norm_color)
    tvdi_f[tvdi > 0.6, :] = np.array(drought_color)
    tvdi_f[tvdi > 0.8, :] = np.array(severe_color)
    
    return tvdi_f.astype(np.uint8)




if __name__ == '__main__':
    imgcode = 'LC81280332016208LGN00_B7'
    path = 'testdata/2-12833/'
    ndvi, vfc = get_plant(imgcode, path)
    print 'complete ndvi calculation.'
    Ts = get_temperature(imgcode, path)
    print 'complete Ts calculation.'
    bqa = datainterface.get_bqa(imgcode, path)
    TVDI, cover = get_drought(ndvi, Ts, bqa)
    print 'complete TVDI calculation.'
    vfc_f = vfc_divide(vfc, ndvi)
    print 'complete vfc divide.'
    TVDI_f = tvdi_divide(TVDI, ndvi, cover)
    plt.imshow(vfc_f)
    plt.figure()
    plt.imshow(TVDI_f)
    plt.show()
