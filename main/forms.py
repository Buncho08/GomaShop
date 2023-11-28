from django import forms
from .models import UserTable, ItemTable, CartTable, CartDetailTable

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
    