from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from User import models as userModel
from Photo import models as photoModel

# Create your views here.
""" 主页 """
def index(request):
    uid = userModel.currentUser(request)

    context = {}
    if uid != None:
        context['uid'] = uid
        # 获取此用户的photo's GEO
        photos = photoModel.getPhotosByUser(uid, limitCount=0)

        context['photos'] = photos
        return render(request, 'footprint.html', context)
    else:
        return HttpResponseRedirect('/user/login')
    