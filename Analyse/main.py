import attractionCulster as ac
import createUserAttractionMatrix as cm
import itemCF as rc

photoCsv     = 'dataset/photo.csv'
culsterDir   = 'dataset/culsters/'
provinceCsv  = 'dataset/province.csv'
photoUserCsv = 'dataset/photo-user.csv'
userAttractionCsv       = 'dataset/user-attraction.csv'
photoAttractionCsv      = 'dataset/photo-attraction.csv'
attractionSimilarityCsv = 'dataset/attraction-similarity.csv'

""" photo.csv 预处理，去除不符合条件的数据 """
ac.fliterDatabase(photoCsv)
print ("数据清洗完成")

""" 照片聚类，获取景点 """
ac.beginCulster(photoCsv, provinceCsv, culsterDir, 0.0005, 15)
print ("照片聚类完成")

""" 获取用户-景点矩阵 """
cm.main(photoCsv, photoUserCsv, photoAttractionCsv, userAttractionCsv, provinceCsv, culsterDir)

""" 景点相似度矩阵 """
itemcf = rc.ItemBasedCF(10,5)
itemcf.generateDataset(userAttractionCsv, pivot=1)
itemcf.calculateAttractionSim()
itemcf.saveAttractionSimMatrix(attractionSimilarityCsv)
print ("生成景点相似度矩阵完成")

