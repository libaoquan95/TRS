## TRS - 基于照片分享的旅游景点推荐系统

### 1.web 系统启动
系统基于 Django 2.0(python 3.6), Mysql.

```
# 运行内置服务器
>>> python manage.py runserver 0.0.0.0:8000

# Django 数据库配置
DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql',
        'NAME'    : 'TRS',
        'USER'    : 'root',
        'PASSWORD': 'root',
        'HOST'    : 'localhost',
        'PORT'    : '3306',
        'charset' : "utf8"
    }
}
```

部分页面使用百度地图 API 构造地图功能，需要自行配置百度地图 API 秘钥

*部分照片数据源自于 flickr 数据集*

### 2.数据分析
首先最根本的数据是照片数据集，见 Analyse/photo.rar (因为文件大小的限制，本地运行序解压为 photo.csv 文件)。此文件部分照片数据源自于 flickr 数据集，为了和 web 数据一致，可以选择从数据库文件导出。

之后执行数据分析
```
# 执行数据分析，从照片数据获取景点相似度信息
>>> python Analyse/main.py
```
最终生成的景点相似度信息存放于 Analyse/attraction-similarity.csv 中，可以导入数据库中用于 web 系统，也可以在 itemCF.py 中测试推荐结果。

### 3.依赖库安装
```
pip install PyMySQL
pip install django
pip install geopy
pip install extfread
```