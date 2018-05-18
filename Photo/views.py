from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from User import models as userModel
from Photo import models as photoModel
import math
import os
from PIL import Image
from PIL.ExifTags import TAGS

# Create your views here.
""" 获取某一用户的所有照片信息
"""
def getPhotosByUser(request, pageNum):
    pageNum = pageNum - 1
    uid = userModel.currentUser(request)
    
    context = {}
    if uid != None:
        context['uid'] = uid
        context['pageNum'] = pageNum+1

        # 获取页数
        photoCount = photoModel.getUserPhotosCount(uid)
        limitCount = 20
        pageLimit = 8
        pageCount = math.ceil(photoCount/limitCount)
        context['count'] = photoCount
        context['pageCount'] = pageCount

        # 设置页码信息
        pageStart = max(1, pageNum-pageLimit)
        pageEnd = min(pageCount, pageNum+pageLimit)
        i = pageStart
        pageIndexs = []
        while i <= pageEnd:
            pageIndexs.append(i)
            i = i + 1
        context['pageIndexs'] = pageIndexs
        
        # 获取照片信息
        photos = photoModel.getPhotosByUser(uid, pageNum, limitCount)
        context['photos'] = [p for p in photos if p['isDelete']==0]

        if request.GET.get('infoType') != None:
            context['hasInfo'] = True
            context['infoType'] = request.GET.get('infoType')
            context['uploadInfo'] = request.GET.get('uploadInfo')
        else:
            context['hasInfo'] = False
        return render(request, 'user_album.html', context)
    else:
        return HttpResponseRedirect('/user/login')

""" 显示一张照片
"""
def getPhotoById(request, photoId):
    uid = userModel.currentUser(request)
    context = {}
    if uid != None:
        context['uid'] = uid

        photo = photoModel.getPhotoById(photoId)
        context['photo'] = photo
        return render(request, 'photo.html', context)
    else:
        return HttpResponseRedirect('/user/login')

""" 显示一张照片的地理信息
"""
def getPhotoGeoById(request, photoId):
    uid = userModel.currentUser(request)
    context = {}
    if uid != None:
        context['uid'] = uid

        photo = photoModel.getPhotoById(photoId)
        context['photo'] = photo
        return render(request, 'photo_map.html', context)
    else:
        return HttpResponseRedirect('/user/login')

""" 上传照片
"""
def uploadPhoto(request):
    uid = userModel.currentUser(request)
    
    context = {}
    if uid != None:
        context['uid'] = uid

        if request.method == 'POST':
            if 'image' in request.FILES:
                imageFile = request.FILES.get('image')
                newImgPath, newImgId = photoModel.uploadPhoto(uid, imageFile)

                # 获取图片 exif 信息
                from TRS import settings as setting
                import exifread
                filename = setting.TEMPLATES[0]['DIRS'][0] + newImgPath.url
                
                fd = open(filename, 'rb')
                FIELD = 'EXIF DateTimeOriginal'
                exifTags = exifread.process_file(fd)
                fd.close()
                photoTag = {}
                if FIELD in exifTags:
                    # 照片的拍摄时间
                    if 'EXIF DateTimeOriginal' in exifTags:
                        takenDate = str(exifTags['EXIF DateTimeOriginal']) 
                        photoTag['takenDate'] = takenDate[:4] + '-' + takenDate[5:7] + '-' + takenDate[8:]
                    else:
                        photoTag['takenDate'] = None
                    # 照片的经度、纬度(未考虑正负)
                    if 'GPS GPSLongitude' in exifTags and 'GPS GPSLatitude' in exifTags:
                        longitude = str(exifTags['GPS GPSLongitude'])
                        latitude  = str(exifTags['GPS GPSLatitude'])
                        photoTag['longitude'] = GPSChange(longitude[1:-1])  # 去除左右括号
                        photoTag['latitude']  = GPSChange(latitude[1:-1])  # 去除左右括号
                        photoTag['location'],photoTag['provinceId']  = getLocation(str(photoTag['latitude'])  +"," +  str(photoTag['longitude']))
                    else:
                        photoTag['longitude'] = None
                        photoTag['latitude']  = None
                        photoTag['location']  = None
                        photoTag['provinceId'] = None
                    # 存储照片的 exif 信息
                    photoModel.updatePhotoExifsById(newImgId, photoTag)
                return HttpResponseRedirect('/photo/list/1?infoType=success&uploadInfo=上传成功！')
            else:
                return HttpResponseRedirect('/photo/list/1?infoType=danger&uploadInfo=上传失败，无文件！', )
        else:
            context['hasInfo'] = False
            return HttpResponseRedirect('/photo/list/1/')
    else:
        return HttpResponseRedirect('/user/login')

""" 转换经纬度格式，将度分秒的形式转换为小数形式
    117°6'21.492" -> 117.10597
@param 
    angle: 角度形式的数据，逗号空格分割，如 '117, 6, 21.492'
@return
    分数形式数据，如 117.10597
"""
def GPSChange(angle):
    angle = angle.split(', ')
    angle[2] = angle[2].split('/')
    return float(angle[0])+float(angle[1])/60+float(angle[2][0])/float(angle[2][1])/3600

""" 根据经纬度获取地址
@param
    coordinate: 经纬度地址，维度在前，经度在后，逗号分割，如 '41.92555397222222,123.39999797222222'
@return
    地址，如 '中国, 辽宁省, 沈阳市 / Shenyang, 沈北新区 / Shenbei, 道义镇, 蒲南路'
    省份id，如 1
"""
def getLocation(coordinate):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim()
    location = geolocator.reverse(coordinate)
    if location.address == None:
        return None, None
    else:
        address = location.address.split(', ')
        address = ', '.join(address)
        pId = 0
        # 获取省份id
        provinceIds = photoModel.getAllProvince()
        for provinceName, provinceId in provinceIds.items():
            if(address.find(provinceName) != -1):
                pId = provinceId
                break
        return address, pId

""" 删除图片
"""
def deletePhotoById(request, photoId):
    uid = userModel.currentUser(request)
    
    context = {}
    if uid != None:
        context['uid'] = uid

        if request.method == 'POST':
            # 获取待删除照片的信息
            photo = photoModel.getPhotoById(photoId)
            # 验证用户
            if photo['userName'] == uid:
                photoModel.deletePhotoById(photoId)
                return HttpResponseRedirect('/photo/list/1?infoType=success&uploadInfo=操作成功！')
            else:
                return HttpResponseRedirect('/photo/list/1?infoType=danger&uploadInfo=操作失败，您没有权限删除非您上传的照片！', )
        else:
            context['hasInfo'] = False
            return HttpResponseRedirect('/photo/list/1/')
    else:
        return HttpResponseRedirect('/user/login')

# 按地址搜索图片
def searchPhotoByLocation(request):
    uid = userModel.currentUser(request)
    
    context = {}
    if uid != None:
        # 搜索信息
        searchInfo = request.GET['searchInfo'].strip()
        pageNum = int(request.GET['page'].strip())-1
        photos = photoModel.searchPhotoByLocation(searchInfo, pageNum, 20)
        context['photos'] = photos
        context['searchInfo'] = searchInfo
        
        context['pageNum'] = pageNum+1
        # 获取页数
        photoCount = photoModel.getSearchPhotoCount(searchInfo)
        limitCount = 20
        pageLimit = 8
        pageCount = math.ceil(photoCount/limitCount)
        context['count'] = photoCount
        context['pageCount'] = pageCount

        # 设置页码信息
        pageStart = max(1, pageNum-pageLimit)
        pageEnd = min(pageCount, pageNum+pageLimit)
        i = pageStart
        pageIndexs = []
        while i <= pageEnd:
            pageIndexs.append(i)
            i = i + 1
        context['pageIndexs'] = pageIndexs

        return render(request, 'search_result.html', context)

    else:
        return HttpResponseRedirect('/user/login')
