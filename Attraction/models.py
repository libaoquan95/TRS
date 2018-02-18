from django.db import models

# Create your models here.
class Attraction(models.Model):
    attractionId = models.AutoField(primary_key=True)
    provinceId   = models.IntegerField()
    clusterId    = models.IntegerField()
    description  = models.TextField(null=True)

    class Meta:
        db_table = 'attraction'

class UserAttraction(models.Model):
    uaId       = models.AutoField(primary_key=True)
    userName   = models.CharField(max_length=255,default='')
    provinceId = models.IntegerField(default=0)
    clusterId  = models.IntegerField(default=0)
    photoCount = models.IntegerField(default=0)
    rating     = models.FloatField(default=0.0)

    class Meta:
        db_table = 'user_attraction'

class PhotoAttraction(models.Model):
    paId       = models.AutoField(primary_key=True)
    photoId    = models.IntegerField()
    provinceId = models.IntegerField()
    clusterId  = models.IntegerField()

    class Meta:
        db_table = 'photo_attraction'

class AttractionSimilarityMatrix(models.Model):
    asmId      = models.AutoField(primary_key=True)
    province1Id = models.IntegerField()
    cluster1Id  = models.IntegerField()
    province2Id = models.IntegerField()
    cluster2Id  = models.IntegerField()
    similarity  = models.FloatField()

    class Meta:
        db_table = 'attraction_similarity_matrix'

""" 获取某用户关联的景点
@param
    userName: 用户名
    limitCount: 数量
@return
    景点信息的数组，格式是：[{'' : '' ... } ... {}]
"""
def getAttractionByUser(userName, limitCount=10):
    results = UserAttraction.objects.filter(userName=userName).values_list('provinceId', \
              'clusterId').order_by('-rating')[:limitCount]

    attractions = []
    for r in results:
        temp = {}
        temp['provinceId'] = r[0]
        temp['clusterId']  = r[1]
        attractions.append(temp)
    return attractions

""" 获取某景点的相似景点
@param
    provinceId: 景点省份id
    clusterId: 聚类id
    limitCount: 数量
@return
    相似景点(provinceId, clusterId)的数组
"""
def getSimAttraction(provinceId, clusterId, limitCount=10):
    results = AttractionSimilarityMatrix.objects.filter(province1Id=provinceId, \
              cluster1Id=clusterId).values_list('province2Id', 'cluster2Id').order_by('-similarity')[:limitCount]
    
    simAttractions = []
    for r in results:
        temp = {}
        temp['provinceId'] = r[0]
        temp['clusterId']  = r[1]
        simAttractions.append(temp)
    return simAttractions

""" 获取某景点的关联照片id
@param
    provinceId: 景点省份id
    clusterId: 聚类id
@return
    照片id的数组
"""
def getAttractionPhotoIds(provinceId, clusterId, pageNum, limitCount=20):
    results = PhotoAttraction.objects.filter(provinceId=provinceId, \
              clusterId=clusterId).values_list('photoId')[pageNum*limitCount:pageNum*limitCount+limitCount]

    photoIds = []
    for r in results:
        photoIds.append(r[0])
    return photoIds

""" 获取某景点的所有关联照片id
@param
    provinceId: 景点省份id
    clusterId: 聚类id
@return
    照片id的数组
"""
def getAllAttractionPhotoIds(provinceId, clusterId):
    results = PhotoAttraction.objects.filter(provinceId=provinceId, clusterId=clusterId).values_list('photoId')

    photoIds = []
    for r in results:
        photoIds.append(r[0])
    return photoIds

""" 获取某景点的关联照片的数量
@param
    provinceId: 景点省份id
    clusterId: 聚类id
@return
    数量
"""
def getAttractionPhotosCount(provinceId, clusterId):
    results = PhotoAttraction.objects.filter(provinceId=provinceId, clusterId=clusterId).count()
    return results