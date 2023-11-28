from typing import Any
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from urllib.parse import urlencode
from django.urls import reverse
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CreateForm, CartDetailForm
from .models import ItemTable, CartDetailTable, CartTable, UserTable
# post受け取ったあとはgetにリダイレクトしたほうがよさそう。

class CreateUser(TemplateView):
    template_name = 'main/createUser.html'
    params = {
        'title' : 'Chirp Cakes',
        'status' : False,
        'form' : '',
        'message' : '',
        'icon' : '',
        'st_title' : '',
    }

    def get(self, request):
        form = CreateForm(label_suffix="")
        self.params['form'] = form
        self.params['status'] = False
        self.params['title'] = 'Chirp Cakes'
        self.params['st_title'] = '新規登録'
        if request.user.id is None:
            return render(request, self.template_name, context=self.params)
        else:
            return redirect('main:index')
    
    def post(self, request):
        form = CreateForm(label_suffix="", data=request.POST)
        # self.params['form'] = form
        if form.is_valid():
            account = form.save()
            account.set_password(account.password)
            if 'icon' in request.FILES:
                account.icon = request.FILES['icon']
            else:
                account.icon = 'media/main/default_icon.png'
            account.save()
            userData = UserTable.objects.get(username=account.username)
            # 初回でカートを作る
            CartTable.objects.create(user_id=userData)
            login(self.request, account)

            # 登録出来たら別ページにリダイレクト、クエリパラメータは特に意味がない数字(意味を持たせたほうがよいのか？)
            # ユーザーごとにユニークな値を持たせて、リダイレクト先で照合するといった方法を取ったほうがよさそうだけど、
            # セキュリティに問題がある…といったわけでもないしいいかという気持ち
            redirect_url = reverse('main:complete')
            url_param = urlencode({'param':122})
            url = f'{redirect_url}?{url_param}'
            return redirect(url)
        else:
            self.params['form'] = form
            return render(request,"main/createUser.html",context=self.params)

class UserComplete(TemplateView):
    def get(self, request, *args, **kwargs):
        if 'param' in request.GET:
            redirect_url = reverse('main:index')
            return render(request, 'main/complete.html', context={'status':request.GET['param'], 'redirect_url':redirect_url})
        else:
            return redirect('main:CreateUser')

def index(request):
    params = {
        'user':0,
        'st_title':'TOP'
    }
    if request.user.id is not None:
        params['user'] = 1
    return render(request, 'main/index.html', params)


class Login(TemplateView):
    params = {
        'status':0,
        'st_title':'ログイン'
    }
    def get(self, request):
        if request.user.id is None:
            return render(
                request,
                'main/login.html',
                self.params,
            )
        else:
            return redirect('main:index')

    def post(self, request):
        userid = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=userid, password=password)
        if user is not None:
            login(request, user)
            self.params['username'] = userid
            redirect_url = reverse('main:index')
            self.params['redirect_url'] = redirect_url
            return render(request, 'main/login_success.html', self.params)
        else:
            self.params['status'] = 1
            return render(request, 'main/login.html', self.params)

class ItemPage(TemplateView):
    template_name = 'main/itempage.html'
    item = ItemTable.objects.all()
    params = {
        'title':'ChirpCakes',
        'item':item,
        'st_title':'商品'
    }
    def get(self, request):
        return render(request, self.template_name, context=self.params)

class ItemDetail(TemplateView):
    template_name = 'main/product.html'
    params = {
        'st_title': '',
        'form':CartDetailForm
    }
    def get(self, request, *args, **kwargs):
        item_slug = self.kwargs['slug']
        self.params['item'] = ItemTable.objects.get(slug=item_slug)
        self.params['st_title'] = ItemTable.objects.get(slug=item_slug).item_name
        return render(request, self.template_name, self.params)


# from django.core.exceptions import ObjectDoesNotExist

class Order(TemplateView):
    template_name = 'main/order.html'
    params = {
        'title' : 'ChirpCakes',
        'status':0,
        'data':'',
        'st_title':'カート'
    }

    def get(self, request, *args, **kwargs):
        if request.user.id is not None:
            order = CartTable.objects.get(user_id=request.user, ordered=False)
            if CartDetailTable.objects.filter(cart_id=order).exists():
                detail = CartDetailTable.objects.filter(cart_id=order).all()
                self.params['data'] = detail
                self.params['status'] = 1
                return render(request, self.template_name, context=self.params)
            else:
                self.params['status'] = 0
                return render(request, self.template_name, context=self.params)
        else:
            return redirect('main:login')
    
    def post(self, request, *args, **kwargs):
        if request.user.id is not None:
            item_id = request.POST['item_id']
            item = ItemTable.objects.get(item_id=item_id)
            quantity = request.POST['quantity']
            # カート追加処理2回目以降
            if CartTable.objects.filter(user_id=request.user, ordered=False).exists():
                order = CartTable.objects.get(user_id=request.user, ordered=False)
                # 既に同じ商品がカートにあった場合
                if CartDetailTable.objects.filter(cart_id=order, item_id=item).exists():
                    detail = CartDetailTable.objects.get(cart_id=order, item_id=item)
                    detail.quantity = quantity
                    detail.save()
                # なかった時
                else:
                    CartDetailTable.objects.create(cart_id=order, item_id=item, quantity=quantity)
            # カート追加処理、初回
            else:
                CartTable.objects.create(user_id=request.user)
                order = CartTable.objects.get(user_id=request.user, ordered=False)
                CartDetailTable.objects.create(cart_id=order, item_id=item, quantity=quantity)

            order = CartTable.objects.get(user_id=request.user, ordered=False)
            detail = CartDetailTable.objects.filter(cart_id=order).all()
            # 戻るボタンを押してもフォームの内容が残ってしまっているためgetでリダイレクトをかける
            # getならだいじょうぶかな
            return redirect('main:order')
        else:
            return redirect('main:login')



from django.http import Http404
class ItemDelete(TemplateView):
    def get(self, request, *args, **kwargs):
        item_slug = self.kwargs['slug']
        item = ItemTable.objects.get(slug=item_slug)
        if CartTable.objects.filter(user_id=request.user, ordered=False).exists():
            order = CartTable.objects.get(user_id=request.user, ordered=False)
            # 既に同じ商品がカートにあった場合
            if CartDetailTable.objects.filter(cart_id=order, item_id=item).exists():
                detail = CartDetailTable.objects.get(cart_id=order, item_id=item).delete()
                return redirect('main:order')
            # なかった時
            else:
                return redirect('main:order')
        else:
            # これが通る時ってやばいとき
            raise Http404
        
