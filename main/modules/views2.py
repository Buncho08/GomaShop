from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import secrets
# Create your views here.
from .models import UserTable
from .forms import CreateForm

class CreateUser(TemplateView):
    template_name = 'main/AccountPage.html'

    def __init__(self):
        self.params = {
            'title' : 'ごますけ商店',
            'status' : False,
            'form' : CreateForm(),
            'message' : '',
            'icon' : '',
            'st_title' : ''
        }
    
    def get(self, request):
        # if 'redirect' in request.GET:
        #     self.params['message'] = "クッソエラー！"
        # else:
        self.params['form'] = CreateForm()
        self.params['status'] = 0
        self.params['title'] = 'ごますけ商店'
        self.params['st_title'] = '新規登録'
        return render(request, self.template_name, context=self.params)
    


class CompleteView(TemplateView):

    template_name = 'main/Complete.html'

    def __init__(self):
        self.params = {
            'title' : 'ごますけ商店',
            'status' : False,
            'message' : '',
            'icon' : ''
        }
    
    def get(self, request):
        self.params['status'] = False
        return render(request, self.template_name, context=self.params)
    
    def post(self, request, *args, **kwargs):
        self.params['form'] = CreateForm(data=request.POST)
        # self.params['status'] = bool(request.POST['secret'])
        if self.params['form'].is_valid():
            account = self.params['form'].save()
            account.set_password(account.password)
            if 'icon' in request.FILES:
                account.icon = request.FILES['icon']
            else:
                account.icon = 'media/main/default_icon.png'
            account.save()
            self.params["status"] = True
            self.params['st_title'] = '登録完了'


        return render(request,"main/Complete.html",context=self.params)


# def index(request):

#     return render(request, 'main/index.html')

# def index2(request):

#     if request.method == "POST":
#         model = get_object_or_404(UserTable, username='buncho08')
#         # 画像ファイルの削除
#         model.icon.delete()
    
#     return HttpResponse('完了です。')

# def createUserTop(request):

#     return (request, 'main/createUserTop.html')