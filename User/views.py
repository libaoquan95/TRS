from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from . import models as userModel

# Create your views here.
""" 登录 """
def login(request):
    context = {}
    if request.POST:
        userName = request.POST['userName'].strip()
        password = request.POST['password'].strip()
        # 验证用户和密码是否可以登录
        loginResult = userModel.canLogin(userName, password)
        if(loginResult):
            # 登录，设置cookie
            response = HttpResponseRedirect('/')
            userModel.login(response, userName, password)
            return response
        else:
            # 不可以登录
            context['hasError'] = True
            context['loginError'] = '错误的用户名或密码'
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html', context)

""" 注册 """
def register(request):
    context = {}
    if request.POST:
        userName = request.POST['userName'].strip()
        password = request.POST['password'].strip()
        password2 = request.POST['password2'].strip()
    else:
        return render(request, 'register.html', context)

""" 注出 """
def logout(request):
    response = HttpResponseRedirect('/user/login')
    userModel.logout(response)
    return response