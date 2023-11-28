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
        fields = ( 'to_lastname', 'to_firstname','post', 'pref', 'address', 'pay')
        labels = {'to_firstname':'名前', 'to_lastname':'苗字', 'post':'郵便番号', 'pref':'都道府県', 'address':'住所詳細', 'pay':'支払い方法'}