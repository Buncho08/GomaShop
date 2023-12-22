from typing import Any
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from urllib.parse import urlencode
from django.urls import reverse
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CreateForm, CartDetailForm, OrderForm, EditUserForm
from .models import ItemTable, CartDetailTable, CartTable, UserTable, OrderTable, OrderDetailTable
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
                account.icon = 'main/icon/default_icon.png'
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

# indexにリダイレクトする
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

def Logout(request):
    if request.user is None:
        return redirect('main:index')
    else:
        user = request.user
        logout(request)
        return render(request, 'main/logout.html', {'user':user})
    

class ItemPage(TemplateView):
    template_name = 'main/itempage.html'
    item = ItemTable.objects.all()
    params = {
        'title':'ChirpCakes',
        'item':item,
        'st_title':'商品',
        'itemCount':[i for i in range(item.count() // 3)]
    }
    def get(self, request):
        return render(request, self.template_name, context=self.params)

class ItemDetail(TemplateView):
    template_name = 'main/product.html'
    params = {
        'st_title': '',
        'form':'',
        'error':''
    }
    def get(self, request, *args, **kwargs):
        item_slug = self.kwargs['slug']
        if ItemTable.objects.filter(slug=item_slug).exists():
            self.params['form'] = CartDetailForm(label_suffix='')
            self.params['item'] = ItemTable.objects.get(slug=item_slug)
            self.params['st_title'] = ItemTable.objects.get(slug=item_slug).item_name
            return render(request, self.template_name, self.params)
        else:
            return redirect('main:index')
    def post(self, request, *args, **kwargs):
        if request.user.id is not None:
            form = CartDetailForm(label_suffix='', data=request.POST)
            item_id = request.POST['item_id']
            item = ItemTable.objects.get(item_id=item_id)
            if form.is_valid():
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
                self.params['form'] = form
                return render(request, self.template_name, context=self.params)
        else:
            return redirect('main:login')

# from django.core.exceptions import ObjectDoesNotExist

class Order(TemplateView):
    template_name = 'main/order.html'
    params = {
        'title' : 'ChirpCakes',
        'status':0,
        'data':'',
        'st_title':'カート',
    }

    def get(self, request, *args, **kwargs):
        if request.user.id is not None:
            if CartTable.objects.filter(user_id=request.user, ordered=False).exists():
                order = CartTable.objects.get(user_id=request.user, ordered=False)
                total = order.get_total()
                point = total // 100
                self.params['get_point'] = point
                if CartDetailTable.objects.filter(cart_id=order).all().exists():
                    detail = CartDetailTable.objects.filter(cart_id=order).all()
                    self.params['data'] = detail
                    self.params['status'] = 1
                    self.params['update'] = order.update
                    self.params['datacount'] = len(detail)
                    self.params['total'] = detail[0].cart_id.get_total
                else:
                    self.params['status'] = 0
            else:
                self.params['status'] = 0
            return render(request, self.template_name, context=self.params)
        else:
            return redirect('main:login')
        
    def post(self, request):
        amount = request.POST.getlist('quantity')
        order = CartTable.objects.get(user_id=request.user, ordered=False)
        detail = CartDetailTable.objects.filter(cart_id=order).all()
        total = order.get_total()
        point = total // 100
        self.params['get_point'] = point
        j = 0
        for i in detail:
            i.quantity = amount[j]
            i.save()
            j += 1
        
        return redirect('main:orderCheck')




from django.http import Http404
class ItemDelete(LoginRequiredMixin, TemplateView):
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

# from datetime import datetime
# from random import random as rd
from django.utils import timezone
class OrderCheck(TemplateView):
    template_name = 'main/orderCheck.html'
    params = {
        'st_title':'注文確認',
    }
    def get(self, request):
        self.params['error'] = 0
        self.params['st_title'] = '注文確認'
        if request.user.id is not None:
            self.params['st_title'] = ''
            if CartTable.objects.filter(user_id=request.user, ordered=False).exists():
                order = CartTable.objects.get(user_id=request.user, ordered=False)
                user = UserTable.objects.get(username=request.user)
                if CartDetailTable.objects.filter(cart_id=order).exists():
                    initial_field = {
                        'to_firstname':user.namae,
                        'to_lastname':user.myouji,
                        'post':user.post,
                        'pref':user.pref,
                        'town':user.town,
                        'address':user.prefDetail,
                        'pay':1,
                    }
                    self.params['user'] = user
                    form = OrderForm(initial_field)
                    self.params['form'] = form
                    return render(request, self.template_name, context=self.params)
                else:
                    return redirect('main:order')
            else:
                return redirect('main:order')
        else:
            return redirect('main:index')
    
    def post(self, request):
        form = OrderForm(label_suffix="", data=request.POST)
        PAY_CHOICE = [
            (1, 'クレジットカード'),
            (2, '代金引換'),
            (3, '後払い決済'),
            (4, '振込')
        ]
        POSTAGE_VALUE = {
            '北海道':5000,
            '沖縄県':5000,
            '福岡県':3000,
            '長野県':6000,
            '熊本県':8000,
            '愛知県':900,
            '大阪府':90000,
        }
        self.params['error'] = 0
        if form.is_valid():
            # データの取得
            order = CartTable.objects.get(user_id=request.user, ordered=False)
            order_detail = CartDetailTable.objects.filter(cart_id=order)
            total = order.get_total()
            point = total // 100
            self.params['get_point'] = point
            # templateに渡す値
            self.params['st_title'] = ''
            pay_select_value = PAY_CHOICE[form.cleaned_data.get('pay') - 1][1]
            self.params['pay'] = pay_select_value
            self.params['items'] = order_detail
            self.params['total'] = order.get_total
            if form.cleaned_data.get('pref') in POSTAGE_VALUE:
                self.params['postage'] = POSTAGE_VALUE[form.cleaned_data.get('pref')]
            else:
                self.params['postage'] = 800
            self.template_name = 'main/orderConfirm.html'
            self.params['form'] = form
        else:
            self.params['st_title'] = 'エラー！！！'
            self.params['error'] = 1
            user = UserTable.objects.get(username=request.user)
            if user.pref:
                initial_field = {
                    'to_firstname':user.namae,
                    'to_lastname':user.myouji,
                    'post':user.post,
                    'pref':user.pref,
                    'town':user.town,
                    'address':user.prefDetail,
                    'pay':1,
                }
                self.params['user'] = user
                form = OrderForm(initial_field)
            self.params['form'] = form

        return render(request,self.template_name, context=self.params)

import datetime as dt
class OrderComplete(TemplateView):
    POSTAGE_VALUE = {
            '北海道':5000,
            '沖縄県':5000,
            '福岡県':3000,
            '長野県':6000,
            '熊本県':8000,
            '愛知県':900,
            '大阪府':90000,
    }
    template_name = 'main/orderComplete.html'
    params = {
    }
    def get(self, request, *args, **kwargs):
        return redirect('main:index')
    
    def post(self, request, *args, **kwargs):
        order = CartTable.objects.get(user_id=request.user, ordered=False)
        order_detail = CartDetailTable.objects.filter(cart_id=order)
        form = OrderForm(label_suffix="", data=request.POST)
        if form.is_valid():
            aft_5_days = dt.timedelta(days=5)
            today = dt.date.today()
            arrive = today + aft_5_days
            print(form.cleaned_data.get('pref'))
            if form.cleaned_data.get('pref') in self.POSTAGE_VALUE:
                postage = self.POSTAGE_VALUE[form.cleaned_data.get('pref')]
            else:
                postage = 800
            OrderTable.objects.create(
                user_id=request.user, 
                pref=form.cleaned_data.get('pref'),
                post=form.cleaned_data.get('post'),
                address=form.cleaned_data.get('address'),
                postage=postage,
                town=form.cleaned_data.get('town'),
                to_firstname=form.cleaned_data.get('to_firstname'),
                to_lastname=form.cleaned_data.get('to_lastname'),
                arrive=arrive,
                pay=form.cleaned_data.get('pay'),
                total_pay=order.get_total()
                )
            
            order_data = OrderTable.objects.filter(user_id=request.user).all().last()
            for item in order_detail:
                OrderDetailTable.objects.create(
                    order_id=order_data,
                    item_id=item.item_id,
                    quantity=item.quantity
                )
            redirect_url = reverse('main:index')
            self.params['redirect_url'] = redirect_url
            user = UserTable.objects.get(username=request.user)
            
            total = order.get_total()
            point = total // 100
            user.points = user.points + point
            if user.post is None:
                user.pref=form.cleaned_data.get('pref'),
                user.post=form.cleaned_data.get('post'),
                user.address=form.cleaned_data.get('address'),
            user.save()
            order.ordered = True
            order.save()
        else:
            self.template_name = 'main/orderConfirm.html'
            self.params['form'] = form
        return render(request, self.template_name, context=self.params)


import random
class MyPage(TemplateView):
    template_name = 'main/mypage.html'
    params = {
    }
    def get(self, request, *args, **kwargs):
        self.params['error'] = False
        if 'error' in request.GET:
            self.params['error'] = True

        if request.user.id is None:
            return redirect('main:login')
        user = UserTable.objects.get(username=request.user)
        form_class = EditUserForm(user)
        point = ((request.user.points // 300 + 1) * 300) - request.user.points
        item = ItemTable.objects.all()
        item_list = []
        random_list = [i for i in range(0, len(item))]
        for i in range(3):
            num = random_list.pop(random.randint(0, len(random_list) - 1))
            item_list.append(item[num])
        self.params['user'] = request.user
        self.params['point'] = point
        self.params['item'] = item_list
        self.params['form'] = form_class

        return render(request, self.template_name, self.params)
    
    def post(self, request, *args, **kwargs):
        user = UserTable.objects.get(username=request.user)
        form = EditUserForm(usermodel=user, instance=user, data=request.POST)
        if form.is_valid():
            if 'icon' in request.FILES:
                footer = request.FILES['icon'].name.split('.')[-1]
                print(footer)
                if not footer.lower() in ['jpg', 'png', 'jpeg', 'gif']:
                    redirect_url = reverse('main:mypage')
                    url_param = urlencode({'error':1})
                    url = f'{redirect_url}?{url_param}'

                    return redirect(url)
                user.icon = request.FILES['icon']
            else:
                user.icon = 'main/icon/default_icon.png'

            form.save()
            user.save()
            user.iconResizer()
            return redirect('main:mypage')
        else:
            self.params['form'] = form
            return render(request, self.template_name, self.params)



class OrderHistory(LoginRequiredMixin, TemplateView):
    template_name = 'main/orderhistory.html'
    params = {
        'status':0
    }
    def get(self, request, *args, **kwargs):
        if OrderTable.objects.filter(user_id=request.user, ordered=False).exists():
            order = OrderTable.objects.prefetch_related('related_order').filter(user_id=request.user, ordered=False)
            if 'filter' in request.GET:
                if request.GET['filter'] == '1':
                    self.params['data'] = order.order_by('total_pay')
                elif request.GET['filter'] == '2':
                    self.params['data'] = order.order_by('-total_pay')
                else:
                    self.params['data'] = order
            else:
                self.params['data'] = order
            self.params['status'] = 1
        else:
            self.params['status'] = 0

        return render(request, self.template_name, context=self.params)
    
class OrderDetail(LoginRequiredMixin, TemplateView):
    template_name = 'main/orderdetail.html'
    params = {
    }

    def get(self, request, *args, **kwargs):
        order_id = self.kwargs['pk']
        if OrderTable.objects.filter(order_id=order_id).exists():
            order = OrderTable.objects.get(order_id=order_id)
            self.params['data'] = OrderDetailTable.objects.filter(order_id=order).all()
            total = order.get_total()
            point = total // 100
            self.params['get_point'] = point
        else:
            return redirect('main:order')
        return render(request, self.template_name, self.params)

class EditUser(LoginRequiredMixin, TemplateView):
    template_name = 'main/editAccount.html'
    params = {
    }

    def get(self, request, *args, **kwargs):
        user = UserTable.objects.get(username=request.user)
        form_class = EditUserForm(user)
        self.params['form'] = form_class
        return render(request, self.template_name, self.params)
    
    def post(self, request):
        user = UserTable.objects.get(username=request.user)
        form = EditUserForm(usermodel=user, instance=user, data=request.POST)
        if form.is_valid():
            if 'icon' in request.FILES:
                footer = request.FILES['icon'].name.split('.')[-1]
                print(footer)
                if not footer.lower() in ['jpg', 'png', 'jpeg', 'gif']:
                    redirect_url = reverse('main:mypage')
                    url_param = urlencode({'error':1})
                    url = f'{redirect_url}?{url_param}'

                    return redirect(url)
                user.icon = request.FILES['icon']
            form.save()
            user.save()
            user.iconResizer()
            return redirect('main:mypage')
        else:
            self.params['form'] = form
            return render(request, self.template_name, self.params)
