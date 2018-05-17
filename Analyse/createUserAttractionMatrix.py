#-*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
from sklearn.preprocessing import StandardScaler

# 构建照片-用户关联矩阵
# param  geoFile：geo数据集
#        phontUserFile：写入照片-用户关联矩阵的文件
# return none
def createPhotoUserMatrix(dataSets, phontUserFile):
    dataSets[['userName','takenDate']].to_csv(phontUserFile, encoding='utf-8', index=True)
    
    
# 构建照片-景点关联矩阵，即合并所有省份的分类信息
# param  culstersFolder：照片聚类后的文件夹，
#        phontUserFile：写入照片-用户景点矩阵的文件
# return none
def createPhotoAttractionMatrix(provinceFile, culstersFolder, phontAttractionFile):
    provinceFrame =  pd.read_csv(provinceFile, index_col=0)

    data = []
    for i in provinceFrame.index:
        oneFrame = pd.read_csv(culstersFolder + str(i) + '.csv', index_col=0)
        oneFrame['province'] = provinceFrame.loc[int(i),['pingyingName']]['pingyingName']
        data.append(oneFrame)

    # 合并
    phontAttractionFrame = pd.concat(data)
    # 写入照片-用户景点矩阵文件
    phontAttractionFrame[['clusterId','province']].to_csv(phontAttractionFile,encoding='utf-8', index=True)
    
    
# 构建用户-景点矩阵
# param:照片-景点关联文件, 照片-用户关联文件
# return none
def createUserAttractionMatrix(phontAttractionFile, phontUserFile, userAttractionFile):
    phontAttractionFrame = pd.read_csv(phontAttractionFile, index_col=0)
    phontUserFrame = pd.read_csv(phontUserFile, index_col=0)
    #print(phontAttractionFrame)
    #print(phontUserFrame)
    
    # 找出所有的用户
    usersFrame = phontUserFrame.drop_duplicates('userName')
    users = np.array(usersFrame['userName'])
    
    # 构建用户-景点矩阵
    # 遍历用户信息
    userAttractionData = []
    printCount = 0
    for userId in users:
        # 找到与此用户关联的照片id
        photoIds = np.array(phontUserFrame[phontUserFrame['userName'] == userId].index.drop_duplicates())
        # 找到照片ID相关联的景点信息
        attractions = phontAttractionFrame.loc[photoIds, ['clusterId', 'province']]
        # 筛除噪音数据(clusterId == -1)
        attractions = attractions[attractions['clusterId'] != -1]
        
        if(len(attractions) != 0):
            # 获取景点id(省标识_聚类id)
            #attractionIds = attractions.drop_duplicates()
            for (clusterId, province), group in attractions.groupby([attractions['clusterId'],attractions['province']]):
                attractionId = ('%s_%s' % (province, int(clusterId)))
                userAttractionData.append([userId, attractionId, len(group)])

        if printCount % 100 == 0:
            print ('%d complete' % (printCount))
        printCount = printCount + 1

    # 将用户-景点-照片数量关系写入DataFrame
    userAttractionData = np.array(userAttractionData)
    data = {'userName': userAttractionData[:, 0],    \
            'attractionId': userAttractionData[:, 1], \
            'photoCount': userAttractionData[:, 2]}
    userAttraction = DataFrame(data, columns=['userName', 'attractionId', 'photoCount'])
    
    # 写入照片-用户景点矩阵文件
    userAttraction.to_csv(userAttractionFile, encoding='utf-8', index=False)

def countToRating(userAttractionFile):
    df = pd.read_csv(userAttractionFile)
    mean = df['photoCount'].mean()
    df['rating'] = df['photoCount']*(5/mean)
    df.loc[df['rating'] >10,'rating']=10
    
    """
    ss = StandardScaler()
    df['ssCount'] = ss.fit_transform(df['photoCount'])
    df['ssRating'] = ss.fit_transform(df['rating'])
    """
    df.to_csv(userAttractionFile, encoding='utf-8', index=False)

# 结果统计
def statistics(userAttractionFile, statisticsFile):
    userAttractionFrame = pd.read_csv(userAttractionFile, index_col=0)
    # 找出所有的景点ID
    #attractionIdsFrame = userAttractionFrame.drop_duplicates('attractionId')
    attractionIdsGroup = userAttractionFrame.groupby('attractionId')
    
    attractionIdsGroup.count().to_csv(statisticsFile, encoding='utf-8', index=False)

def main(PhotoFile, photoUserFile, photoAttractionFile, userAttractionFile, provinceFile, culsterFiles):
    
    # 读取数据集
    dataSets = pd.read_csv(PhotoFile, index_col=0)

    createPhotoUserMatrix(dataSets, photoUserFile)
    print ("构建照片-用户关联矩阵完成")
    
    createPhotoAttractionMatrix(provinceFile, culsterFiles, photoAttractionFile)
    print ("构建照片-景点关联矩阵完成")
    
    createUserAttractionMatrix(photoAttractionFile, photoUserFile, userAttractionFile)
    print ("构建用户-景点矩阵完成")
    
    countToRating(userAttractionFile)
    print ("统计评分完成")

    p1 = pd.read_csv(photoUserFile)
    userCount = len(p1.drop_duplicates('userName'))
    p1 = pd.read_csv(photoAttractionFile)
    attractionCount = len(p1.drop_duplicates(['clusterId', 'province']))
    print ('用户数量：%d，景点数量：%d' % (userCount, attractionCount-34))
