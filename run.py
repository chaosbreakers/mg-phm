# -*- coding: utf-8 -*-
import numpy as np
import cv2
from scipy.misc import imsave
import matplotlib.pyplot as plt
import analysis
import imageprocess
import datainterface
import imagemosaicking


town_names = ['昂素镇', '敖勒召其镇', '布拉格苏木', '城川镇', '二道川乡', \
                '毛盖图苏木', '三段地镇', '上海庙镇', '珠和苏木']
for index in range(len(town_names)):
    town_names[index] = unicode(town_names[index], 'utf8')
geojson_path = 'testdata/'

#12月
winter12933 = 'LC81290332016343LGN00_MTL'
winter12833 = 'LC81280332016336LGN00_MTL'
winter12834 = 'LC81280342016336LGN00_MTL'
winter12 = (winter12933, winter12833, winter12834)
#01月
winter12933 = 'LC81290332017025LGN00_MTL'
winter12833 = 'LC81280332017002LGN00_MTL'
winter12834 = 'LC81280342017002LGN00_MTL'
winter01 = (winter12933, winter12833, winter12834)
#02月
winter12933 = 'LC81290332017089LGN00_MTL'#3月，2月数据不可用
winter12833 = 'LC81280332017034LGN00_MTL'
winter12834 = 'LC81280342017034LGN00_MTL'
winter02 = (winter12933, winter12833, winter12834)

#06
summer12933 = 'LC81290332016151LGN00_MTL'
summer12833 = 'LC81280332016176LGN00_MTL'
summer12834 = 'LC81280342016176LGN00_MTL'
summer06 = (summer12933, summer12833, summer12834)
#07
summer12933 = 'LC81290332016183LGN00_MTL'
summer12833 = 'LC81280332016208LGN00_MTL'
summer12834 = 'LC81280342016208LGN00_MTL'
summer07 = (summer12933, summer12833, summer12834)
#08
summer12933 = 'LC81290332016247LGN00_MTL'
summer12833 = 'LC81280332016240LGN00_MTL'
summer12834 = 'LC81280342016240LGN00_MTL'
summer08 = (summer12933, summer12833, summer12834)

cases = (summer08,)
case_name = ('Aug',)
#cases = (winter12, winter01, winter02, summer06, summer07, summer08)
#case_name = ('Nov','Jan','Feb','Jun','Jul','Aug',)
#cases = (wintercode,)
#case_name = ('winter')

for ii in range(len(cases)):
    case = cases[ii]

    # image load
    imgcode1 = case[0]
    imgcode2 = case[1]
    imgcode3 = case[2]
    path1 = 'testdata/1-12933/'
    path2 = 'testdata/2-12833/'
    path3 = 'testdata/3-12834/'
    corner1 = datainterface.get_corner(imgcode1, path1)
    corner2 = datainterface.get_corner(imgcode2, path2)
    corner3 = datainterface.get_corner(imgcode3, path3)
    img1 = datainterface.get_band(imgcode1, 4, path1)
    img2 = datainterface.get_band(imgcode2, 4, path2)
    img3 = datainterface.get_band(imgcode3, 4, path3)
    bqa1 = datainterface.get_bqa(imgcode1, path1)
    bqa2 = datainterface.get_bqa(imgcode2, path2)
    bqa3 = datainterface.get_bqa(imgcode3, path3)
    file_date1 = datainterface.get_date(imgcode1, path1)
    file_date2 = datainterface.get_date(imgcode2, path2)
    file_date3 = datainterface.get_date(imgcode3, path3)
    
    # image analysis
    ndvi1, vfc1 = analysis.get_plant(imgcode1, path1)
    ndvi2, vfc2 = analysis.get_plant(imgcode2, path2)
    ndvi3, vfc3 = analysis.get_plant(imgcode3, path3)

    print 'complete ndvi calculation...'
    Ts1 = analysis.get_temperature(imgcode1, path1)
    Ts2 = analysis.get_temperature(imgcode2, path2)
    Ts3 = analysis.get_temperature(imgcode3, path3)
    print 'complete Ts calculation...'
    tvdi1, cover1 = analysis.get_drought(ndvi1, Ts1, bqa1)
    tvdi2, cover2 = analysis.get_drought(ndvi2, Ts2, bqa2)
    tvdi3, cover3 = analysis.get_drought(ndvi3, Ts3, bqa3)
    print 'complete tvdi calculation...'

    ndvi1_d = cv2.resize(ndvi1,None,fx=0.1,fy=0.1)
    ndvi2_d = cv2.resize(ndvi2,None,fx=0.1,fy=0.1)
    ndvi3_d = cv2.resize(ndvi3,None,fx=0.1,fy=0.1)

    vfc1_d = cv2.resize(vfc1,None,fx=0.1,fy=0.1)
    vfc2_d = cv2.resize(vfc2,None,fx=0.1,fy=0.1)
    vfc3_d = cv2.resize(vfc3,None,fx=0.1,fy=0.1)

    Ts1_d = cv2.resize(Ts1,None,fx=0.1,fy=0.1)
    Ts2_d = cv2.resize(Ts2,None,fx=0.1,fy=0.1)
    Ts3_d = cv2.resize(Ts3,None,fx=0.1,fy=0.1)

    tvdi1_d = cv2.resize(tvdi1,None,fx=0.1,fy=0.1)
    tvdi2_d = cv2.resize(tvdi2,None,fx=0.1,fy=0.1)
    tvdi3_d = cv2.resize(tvdi3,None,fx=0.1,fy=0.1)
    print 'complete image analyzing...'



    save_filename = 'output/' + case_name[ii] + '_' + 'ndvi1' + '.png'
    imsave(save_filename, ndvi1)
    save_filename = 'output/' + case_name[ii] + '_' + 'vfc1' + '.png'
    imsave(save_filename, vfc1)
    save_filename = 'output/' + case_name[ii] + '_' + 'ndvi2' + '.png'
    imsave(save_filename, ndvi2)
    save_filename = 'output/' + case_name[ii] + '_' + 'vfc2' + '.png'
    imsave(save_filename, vfc2)
    save_filename = 'output/' + case_name[ii] + '_' + 'ndvi3' + '.png'
    imsave(save_filename, ndvi3)
    save_filename = 'output/' + case_name[ii] + '_' + 'vfc3' + '.png'
    imsave(save_filename, vfc3)

    save_filename = 'output/' + case_name[ii] + '_' + 'Ts1' + '.png'
    imsave(save_filename, Ts1)
    save_filename = 'output/' + case_name[ii] + '_' + 'Ts2' + '.png'
    imsave(save_filename, Ts2)
    save_filename = 'output/' + case_name[ii] + '_' + 'Ts3' + '.png'
    imsave(save_filename, Ts3)
    save_filename = 'output/' + case_name[ii] + '_' + 'tvdi1' + '.png'
    imsave(save_filename, tvdi1)
    save_filename = 'output/' + case_name[ii] + '_' + 'tvdi2' + '.png'
    imsave(save_filename, tvdi2)
    save_filename = 'output/' + case_name[ii] + '_' + 'tvdi3' + '.png'
    imsave(save_filename, tvdi3)


    save_filename = 'output/d' + case_name[ii] + '_' + 'ndvi1_d' + '.png'
    imsave(save_filename, ndvi1_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'vfc1_d' + '.png'
    imsave(save_filename, vfc1_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'ndvi2_d' + '.png'
    imsave(save_filename, ndvi2_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'vfc2_d' + '.png'
    imsave(save_filename, vfc2_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'ndvi3_d' + '.png'
    imsave(save_filename, ndvi3_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'vfc3_d' + '.png'
    imsave(save_filename, vfc3_d)

    save_filename = 'output/d' + case_name[ii] + '_' + 'Ts1_d' + '.png'
    imsave(save_filename, Ts1_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'Ts2_d' + '.png'
    imsave(save_filename, Ts2_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'Ts3_d' + '.png'
    imsave(save_filename, Ts3_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'tvdi1_d' + '.png'
    imsave(save_filename, tvdi1_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'tvdi2_d' + '.png'
    imsave(save_filename, tvdi2_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'tvdi3_d' + '.png'
    imsave(save_filename, tvdi3_d)







    # image mosaicking
    imgall_origin, corner_origin = imagemosaicking.cut_img_easy(img1, img2, img3, corner1, corner2, corner3)
    imgall_ndvi, corner_ndvi = imagemosaicking.cut_img_easy(ndvi1, ndvi2, ndvi3, corner1, corner2, corner3)
    imgall_vfc, corner_vfc = imagemosaicking.cut_img_easy(vfc1, vfc2, vfc3, corner1, corner2, corner3)
    imgall_Ts, corner_Ts = imagemosaicking.cut_img_easy(Ts1, Ts2, Ts3, corner1, corner2, corner3)
    imgall_tvdi, corner_tvdi = imagemosaicking.cut_img_easy(tvdi1, tvdi2, tvdi3, corner1, corner2, corner3)
    imgall_tvdi_cover, corner_cover = imagemosaicking.cut_img_easy(cover1, cover2, cover3, corner1, corner2, corner3)




    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_origin' + '.png'
    imsave(save_filename, imgall_origin)
    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_ndvi' + '.png'
    imsave(save_filename, imgall_ndvi)
    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_vfc' + '.png'
    imsave(save_filename, imgall_vfc)
    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_Ts' + '.png'
    imsave(save_filename, imgall_Ts)
    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_tvdi' + '.png'
    imsave(save_filename, imgall_tvdi)

    


    imgall_origin_d = cv2.resize(imgall_origin, None, fx=0.2, fy=0.2)
    imgall_ndvi_d = cv2.resize(imgall_ndvi, None, fx=0.2, fy=0.2)
    imgall_vfc_d = cv2.resize(imgall_vfc, None, fx=0.2, fy=0.2)
    imgall_Ts_d = cv2.resize(imgall_Ts, None, fx=0.2, fy=0.2)
    imgall_tvdi_d = cv2.resize(imgall_tvdi, None, fx=0.2, fy=0.2)
    imgall_tvdi_cover_d = cv2.resize(imgall_tvdi_cover, None, fx=0.2, fy=0.2)


    save_filename = 'output/d' + case_name[ii] + '_' + 'imgall_origin_d' + '.png'
    imsave(save_filename, imgall_origin_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'imgall_ndvi_d' + '.png'
    imsave(save_filename, imgall_ndvi_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'imgall_vfc_d' + '.png'
    imsave(save_filename, imgall_vfc_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'imgall_Ts_d' + '.png'
    imsave(save_filename, imgall_Ts_d)
    save_filename = 'output/d' + case_name[ii] + '_' + 'imgall_tvdi_d' + '.png'
    imsave(save_filename, imgall_tvdi_d)





    print 'complete image mosaicking...'
    # image filtering
    filter_box = 20
    imgall_origin_filtered = imageprocess.mean_filter(imgall_origin_d, filter_box)
    imgall_ndvi_filtered = imageprocess.mean_filter(imgall_ndvi_d, filter_box)
    imgall_vfc_filtered = imageprocess.mean_filter(imgall_vfc_d, filter_box)
    imgall_Ts_filtered = imageprocess.mean_filter(imgall_Ts_d, filter_box)
    imgall_tvdi_filtered = imageprocess.mean_filter(imgall_tvdi_d, filter_box)
    print 'complete image filtering...'
    

    """
    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_origin_filtered' + '.png'
    imsave(save_filename, imgall_origin_filtered)
    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_ndvi_filtered' + '.png'
    imsave(save_filename, imgall_ndvi_filtered)
    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_vfc_filtered' + '.png'
    imsave(save_filename, imgall_vfc_filtered)
    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_Ts_filtered' + '.png'
    imsave(save_filename, imgall_Ts_filtered)
    save_filename = 'output/' + case_name[ii] + '_' + 'imgall_tvdi_filtered' + '.png'
    imsave(save_filename, imgall_tvdi_filtered)
    """

    filter_box = 5
    imgall_origin = imageprocess.mean_filter(imgall_origin_d, filter_box)
    imgall_ndvi = imageprocess.mean_filter(imgall_ndvi_d, filter_box)
    imgall_vfc = imageprocess.mean_filter(imgall_vfc_d, filter_box)
    imgall_Ts = imageprocess.mean_filter(imgall_Ts_d, filter_box)
    imgall_tvdi = imageprocess.mean_filter(imgall_tvdi_d, filter_box)
    print 'complete image filtering...'

    # density divide
    vfc_3d = analysis.vfc_divide(imgall_vfc, imgall_ndvi)
    tvdi_3d = analysis.tvdi_divide(imgall_tvdi, imgall_ndvi, imgall_tvdi_cover_d)
    print 'complete density divide...'



    save_filename = 'output/' + case_name[ii] + '_' + 'vfc_3d' + '.png'
    imsave(save_filename, vfc_3d)
    save_filename = 'output/' + case_name[ii] + '_' + 'tvdi_3d' + '.png'
    imsave(save_filename, tvdi_3d)

"""
    #pn_poly
    county_cover = np.zeros_like(imgall_origin)
    for town_num in range(len(town_names)):
        print town_num + 1

        geo_filename = geojson_path + town_names[town_num] + '.geojson'
        geodata = datainterface.geojson_read(geo_filename)

        town_cover = imageprocess.pn_poly(imgall_origin, corner_origin, geodata)
        county_cover += town_cover

        town_origin = town_cover * imgall_origin
        town_vfc = town_cover * imgall_vfc
        town_Ts = town_cover * imgall_Ts
        town_tvdi = town_cover * imgall_tvdi

        town_vfc_4d = np.zeros((vfc_3d.shape[0], vfc_3d.shape[1], 4))
        town_tvdi_4d = np.zeros((tvdi_3d.shape[0], tvdi_3d.shape[1], 4))
        for i in range(3):
            town_vfc_4d[:, :, i] = vfc_3d[:, :, i] / 255.0
            town_tvdi_4d[:, :, i] = tvdi_3d[:, :, i] / 255.0
        town_vfc_4d[:,:,3] = town_cover
        town_tvdi_4d[:,:,3] = town_cover            

        var_names = ('town_origin', 'town_vfc', 'town_Ts', 'town_tvdi',\
                     'town_vfc_4d', 'town_tvdi_4d')
        for var_name in var_names:
            save_filename = 'output/' + case_name[ii] + town_names[town_num] + var_name  + '_' + '.png'
            print 'saving images of '+ town_names[town_num] + var_name   + '...'
            if (var_name != 'town_vfc_4d') and (var_name != 'town_tvdi_4d'):
                imsave(save_filename, eval(var_name) * town_cover)
            else:
#                img_temp = np.zeros((town_cover.shape[0], town_cover.shape[1],4))
#                img_temp[:,:,0:3] = eval(var_name)
#                img_temp[:,:,3] = town_cover
#                imsave(save_filename, img_temp)
                imsave(save_filename, eval(var_name))

    print 'saving images of county...'
    county_origin = county_cover * imgall_origin
    county_vfc = county_cover * imgall_vfc
    county_Ts = county_cover * imgall_Ts
    county_tvdi = county_cover * imgall_tvdi

    county_vfc_4d = np.zeros((vfc_3d.shape[0], vfc_3d.shape[1], 4))
    county_tvdi_4d = np.zeros((tvdi_3d.shape[0], tvdi_3d.shape[1], 4))
    for i in range(3):
        county_vfc_4d[:, :, i] = vfc_3d[:, :, i] / 255.0
        county_tvdi_4d[:, :, i] = tvdi_3d[:, :, i] / 255.0
    county_vfc_4d[:,:,3] = county_cover
    county_tvdi_4d[:,:,3] = county_cover 
    # save county
    var_names = ('county_origin', 'county_vfc', 'county_Ts', 'county_tvdi',\
                 'county_vfc_4d', 'county_tvdi_4d')
    for var_name in var_names:
        print var_name
        save_filename = 'output/' + case_name[ii] + var_name + '_' +  '.png'
        print 'saving images of ' + var_name  +'...'
        if (var_name != 'county_vfc_4d') and (var_name != 'county_tvdi_4d'):
            imsave(save_filename, eval(var_name) * county_cover)
        else:
            imsave(save_filename, eval(var_name))
#            img_temp = np.zeros((county_cover.shape[0], county_cover.shape[1],4))
#            img_temp[:,:,0:3] = eval(var_name)
#            img_temp[:,:,3] = county_cover
#            imsave(save_filename, img_temp)

"""
