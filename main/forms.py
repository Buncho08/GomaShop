from django import forms
from .models import UserTable, CartDetailTable, OrderDetailTable, OrderTable

# フォームクラス作成
class CreateForm(forms.ModelForm):
    class Meta():
        # ユーザー認証
        model = UserTable
        # フィールド指定
        fields = ('username','email','password', 'mail_deriv')
        # フィールド名指定
        labels = {'username':"ユーザーID",'email':"メール", 'mail_deriv':"メール配信希望"}

    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(),label="パスワード")

class CartDetailForm(forms.ModelForm):
    class Meta():
        model = CartDetailTable
        fields = ('item_id', 'quantity')
        labels = {'item_id':'商品', 'quantity':'数量'}

class OrderForm(forms.ModelForm):
    class Meta():
        model = OrderTable
        fields = ('to_lastname', 'to_firstname','post', 'pref', 'town', 'address', 'pay')
        labels = {
            'to_firstname':'名前',
            'to_lastname':'苗字', 
            'post':'郵便番号', 
            'pref':'都道府県',
            'town':'市町村',
            'address':'住所詳細', 
            'pay':'支払い方法'
            }

    def __init__(self, initial=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['to_firstname'].initial = initial['to_firstname']
        self.fields['to_lastname'].initial = initial['to_lastname']
        self.fields['post'].initial = initial['post']
        self.fields['pref'].initial = initial['pref']
        self.fields['town'].initial = initial['town']
        self.fields['address'].initial = initial['address']
        self.fields['pay'].initial = initial['pay']
        print(initial['post'])
        print('u')



class EditUserForm(forms.ModelForm):
    class Meta():
        model = UserTable
        fields = ('email', 'birthday', 'icon', 'myouji', 'namae', 'post', 'pref', 'town', 'prefDetail', 'mail_deriv')
        labels = {
            'email':'メールアドレス', 
            'birthday':'生年月日', 
            'icon':'アイコン', 
            'myouji':'姓', 
            'namae':'名', 
            'post':'郵便番号', 
            'pref':'都道府県', 
            'town':'市町村', 
            'prefDetail':'以下住所', 
            'mail_deriv':'メール配信希望'
        }

    def __init__(self, usermodel=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(EditUserForm, self).__init__(*args, **kwargs)
        if usermodel.email:
            self.fields['email'].initial = usermodel.email
        if usermodel.birthday:
            self.fields['birthday'].initial = usermodel.birthday
        if usermodel.icon:
            self.fields['icon'].initial = usermodel.icon
        if usermodel.myouji:
            self.fields['myouji'].initial = usermodel.myouji
        if usermodel.namae:
            self.fields['namae'].initial = usermodel.namae
        if usermodel.post:
            self.fields['post'].initial = usermodel.post
        if usermodel.pref:
            self.fields['pref'].initial = usermodel.pref
        if usermodel.town:
            self.fields['town'].initial = usermodel.town
        if usermodel.prefDetail:
            self.fields['prefDetail'].initial = usermodel.prefDetail
        if usermodel.mail_deriv:
            self.fields['mail_deriv'].initial = usermodel.mail_deriv
    