## TRS - 基于照片分享的旅游景点推荐系统

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

部分页面使用百度地图API，需要自行配置百度地图API秘钥

*部分照片数据源自于 flickr 数据集*
