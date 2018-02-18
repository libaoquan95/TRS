from django.db import models
import hashlib

# Create your models here.
class User(models.Model):
    userId       =  models.AutoField(primary_key=True)            # 用户id
    userName     =  models.CharField(max_length=255, unique=True) # 用户名
    password     =  models.CharField(max_length=255)              # 密码
    userGroup    =  models.CharField(max_length=255, null=True)   # 用户组

    class Meta:
        db_table = 'user'

""" 判断用户身份，是否允许用户登录
@param
    userName: 用户名
    password: 密码
@return
    True: 可以登录
    False: 不允许登录
"""
def canLogin(userName, password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    result = User.objects.filter(userName=userName,password=password)
    if result.exists():
        return True
    else:
        return False

""" 登录，设置cookie
@param
    response: http回复
    userName: 用户名
    password: 密码
@return
    response: http回复
"""
def login(response, userName, password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    response.set_cookie('UID',userName,3600)
    response.set_cookie('token',hashlib.md5((userName+password).encode('utf-8')).hexdigest(),3600)
    return response

""" 登出，清除cookie
@param
    response: http回复
    userName: 用户名
    password: 密码
@return
    response: http回复
"""
def logout(response):
    response.set_cookie('UID',"",0)
    response.set_cookie('token',"",0)
    return response

""" 验证当前用户cookie
@param
    request: http请求
@return
    uid: 是用户
    None: 不是用户
"""
def currentUser(request):
    uid = request.COOKIES.get('UID','')
    token = request.COOKIES.get('token','')

    # cookie没有用户信息
    if uid == '' or token== '':
        return None
    # 判断信息有效性
    result = User.objects.filter(userName=uid)
    if result.exists():
        if token != hashlib.md5((uid+result[0].password).encode('utf-8')).hexdigest():
            return None
        else:
            return uid
    else:
        return None


