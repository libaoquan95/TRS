from django.db import models
import urllib

# Create your models here.
class Photo(models.Model):
    photoId       = models.AutoField(primary_key=True)            # 照片id
    userName      = models.CharField(max_length=255)              # 用户名
    takenDate     = models.CharField(max_length=255, null=True)   # 拍摄日期
    title         = models.TextField(null=True)                   # 照片标题
    description   = models.TextField(null=True)                   # 照片描述
    longitude     = models.FloatField(null=True)                  # 经度
    latitude      = models.FloatField(null=True)                  # 纬度
    pageURL       = models.CharField(max_length=255, null=True)   # 照片在flicker的页面URL
    downloadURL   = models.CharField(max_length=255, null=True)   # 照片在flicker的下载URL
    image         = models.ImageField(upload_to='image',null=True)# 照片在服务器的存储路径
    provinceId    = models.IntegerField(null=True)                # 照片的拍摄地址的省位置
    location      = models.TextField(null=True)                   # 照片的拍摄地址
    isVideo       = models.BooleanField(default=False)            # 是否是视频
    isDelete      = models.BooleanField(default=False)            # 是否删除
    #filePath      = models.CharField(max_length=255, null=True)   
    #photoFlikerId = models.CharField(max_length=20, null=True)    # 照片在fliker中的id

    class Meta:
        db_table = 'photo'

class Province(models.Model):
    provinceId   = models.AutoField(primary_key=True)  
    nameInFile   = models.CharField(max_length=255,default='')
    provinceName = models.CharField(max_length=255)
    pingyingName = models.CharField(max_length=255,null=True)
    class Meta:
        db_table = 'province'

""" 获取某一用户的照片的信息
@param
    userName: 用户名
@return
    照片信息数组，每个照片信息是一个字典，格式是： [{'id':1,'longitude':2,...} ... {}]
"""
def getPhotosByUser(userName, pageNum=0, limitCount=20):
    if limitCount == 0:
        results = Photo.objects.filter(userName=userName, isVideo=0).values_list('photoId', 'longitude',\
             'latitude', 'userName', 'takenDate', 'location', 'downloadURL', 'image', 'isDelete').order_by('-takenDate')
    else:
        results = Photo.objects.filter(userName=userName, isVideo=0).values_list('photoId', 'longitude',\
             'latitude', 'userName', 'takenDate', 'location', 'downloadURL', 'image', 'isDelete').order_by('-takenDate')\
             [pageNum*limitCount:pageNum*limitCount+limitCount]
    
    photos = []
    for r in results:
        temp = {}
        temp['id'] = r[0]
        temp['longitude'] = r[1]
        temp['latitude'] = r[2]
        temp['userName'] = r[3]
        if r[4] == '' or r[4] == None:
            temp['takenDate'] = '无时间信息'
        else:
            temp['takenDate'] = r[4][:16]
        if r[5] == '' or r[5] == None:
            temp['location'] = '无位置信息'
        else:
            temp['location'] = urllib.parse.unquote(r[5])
        if(r[7] == '' or r[7] == None):
            temp['imageUrl'] = r[6]
        else:
            from TRS import settings as setting
            temp['imageUrl'] = setting.MEDIA_URL + r[7]
        temp['isDelete'] = r[8]
        photos.append(temp)

    return photos

""" 获取用户的关联照片的数量
@param
    userName: 用户名
@return
    数量, int
"""
def getUserPhotosCount(userName):
    results = Photo.objects.filter(userName=userName).count()
    return results

""" 根据省份id获取省名称
@param
    provinceId: 省信息id
@return
    省名称，string
"""
def getProvinceById(provinceId):
    results = Province.objects.filter(provinceId=provinceId).values_list('provinceName')
    return results[0][0]

""" 根据id获取照片信息
@param
    photoId: 照片id
@return
    照片信息字典
"""
def getPhotoById(photoId):
    results = Photo.objects.filter(photoId=photoId).values_list('userName','takenDate',\
             'location','longitude','latitude', 'downloadURL', 'image', 'isDelete')
    
    photo = {}
    if results.exists():
        photo['id'] = photoId
        photo['userName'] = results[0][0]
        if results[0][1] == '' or results[0][1] == None:
            photo['takenDate'] = '无时间信息'
        else:
            photo['takenDate'] = results[0][1][:16]
        if results[0][2] == '' or results[0][2] == None:
            photo['location'] = '无位置信息'
        else:
            photo['location'] = urllib.parse.unquote(results[0][2])
        photo['longitude'] = results[0][3]
        photo['latitude'] = results[0][4]
        if(results[0][6] == '' or results[0][6] == None):
            photo['imageUrl'] = results[0][5]
        else:
            from TRS import settings as setting
            photo['imageUrl'] = setting.MEDIA_URL + results[0][6]
        photo['isDelete'] = results[0][7]

    return photo
    
""" 上传图片
@param
    userName: 上传者
    imageFie: 上传图片文件
@return
    图片文件，图片id
"""
def uploadPhoto(userName, imageFie):
    new_img = Photo(userName = userName,isVideo = 0,image = imageFie)
    new_img.save()
    return new_img.image, new_img.photoId

""" 获取省份名和id,省份名是geopy中返回的
@return
    字典形式 {省份名: 省份id}
"""
def getAllProvince():
    results = Province.objects.all().values_list('provinceId','nameInFile')
    provinces = {}
    for r in results:
        provinces[r[1]] = r[0]

    provinces['廣東省'] = provinces['广东省']
    return provinces

""" 获取省份名和id
@return
    数组形式，每个元素输一个字典 {省份名，省份id}
"""
def getAllProvinceNameAndId():
    results = Province.objects.all().values_list('provinceId','provinceName').order_by('pingyingName')
    provinces = []
    for r in results:
        temp = {}
        temp['id'] = r[0]
        temp['name'] = r[1]
        provinces.append(temp)
    return provinces

""" 更新照片 exif 信息
@param
    photoId: 照片id
    photoExifs: 照片 exif 信息
"""
def updatePhotoExifsById(photoId, photoExifs):
    newImg = Photo.objects.get(photoId=photoId)
    newImg.takenDate = photoExifs['takenDate']
    newImg.longitude = photoExifs['longitude']
    newImg.latitude  = photoExifs['latitude']
    newImg.provinceId = photoExifs['provinceId']
    if photoExifs['location'] == None:
        newImg.location  = ''
    else:
        newImg.location  = urllib.parse.quote(photoExifs['location'])
    newImg.save()

""" 删除照片，假删除，修改 isDelete 属性
@param
    photoId: 照片id
"""
def deletePhotoById(photoId):
    photo = Photo.objects.get(photoId=photoId)
    #if photo.exists():
    photo.isDelete = 1
    photo.save()