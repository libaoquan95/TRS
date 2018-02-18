from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from User import models as userModel
from Attraction import models as attractionModel
from Photo import models as photoModel
import math

# Create your views here.
""" 获取推荐的景点信息
"""
def recommend(request):
    uid = userModel.currentUser(request)
    
    context = {}
    if uid != None:
        context['uid'] = uid
        simAttractions = []
        # 获取某一用户的关联景点
        attractioms = attractionModel.getAttractionByUser(uid, 10)
        for a in attractioms:
            # 获取景点的相似景点
            oneSimAtt = attractionModel.getSimAttraction(a['provinceId'], a['clusterId'], 5)
            for s in oneSimAtt:
                # 相似景点不重复且不再用户的关联景点中
                if s not in simAttractions or s not in attractioms:
                    simAttractions.append(s)

        # 根据景点id获取景点信息
        attractions = []
        for a in simAttractions:
            tempDict = {}
            tempDict['provinceName'] = photoModel.getProvinceById(a['provinceId'])
            tempDict['provinceId']   = a['provinceId']
            tempDict['clusterId']    = a['clusterId']
            # 获取此景点中的一张照片
            tempPhotoId = attractionModel.getAttractionPhotoIds(tempDict['provinceId'], tempDict['clusterId'], 1, 1)
            tempPhoto   = photoModel.getPhotoById(tempPhotoId[0])
            tempDict['imageUrl'] = tempPhoto['imageUrl']
            attractions.append(tempDict)
        context['attractions'] = attractions
        return render(request, 'recommend.html', context)
    else:
        return HttpResponseRedirect('/user/login')

""" 获取景点关联的照片信息
"""
def AttractionAlbum(request, provinceId, clusterId, pageNum=1):
    pageNum = pageNum - 1
    uid = userModel.currentUser(request)
    
    context = {}
    if uid != None:
        context['uid'] = uid
        context['provinceId'] = provinceId
        context['clusterId'] = clusterId
        context['pageNum'] = pageNum+1

        # 获取页数
        photoCount = attractionModel.getAttractionPhotosCount(provinceId, clusterId)
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
        photoIds = attractionModel.getAttractionPhotoIds(provinceId, clusterId, pageNum, limitCount)
        photos = []
        for pid in photoIds:
            photos.append(photoModel.getPhotoById(pid))
        context['photos'] = photos

        return render(request, 'attraction_album.html', context)
    else:
        return HttpResponseRedirect('/user/login')

""" 景点地图
"""
def AttractionMap(request, provinceId, clusterId):
    uid = userModel.currentUser(request)
    
    context = {}
    if uid != None:
        context['uid'] = uid
        
        # 获取照片信息
        photoIds = attractionModel.getAllAttractionPhotoIds(provinceId, clusterId)
        photos = []
        for pid in photoIds:
            photos.append(photoModel.getPhotoById(pid))
        context['photos'] = photos
        return render(request, 'attraction_map.html', context)
    else:
        return HttpResponseRedirect('/user/login')
