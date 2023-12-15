from django.db import models
import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib import auth
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from PIL import Image
import io

def savePath(model, filename):
    ext = filename.split('.')[-1]
    new_name = model.username + "_icon"
    # ルートはGomaShop/らしい
    path = f'.{settings.MEDIA_URL}main/icon/{model.username}_icon.{ext}'
    print(path)
    if os.path.exists(path):
        os.remove(path)

    return f'main/icon/{new_name}.{ext}'

def saveItemPath(model, filename):
    ext = filename.split('.')[-1]
    new_name = model.item_name_eng + "_img"
    path = f'.{settings.MEDIA_URL}main/item/{new_name}.{ext}'
    print(path)
    if os.path.exists(path):
        os.remove(path)
    return f'main/item/{new_name}.{ext}'



class MyUserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, username, email, password=None, **extra_fields):
            if not username:
                raise ValueError('ユーザー名は必須項目です')
            if not email:
                raise ValueError('メールアドレスは必須項目です')

            user = self.model(
                username=username,
                email=self.normalize_email(email),
                # 受け取った値をフィールドにぶち込んでいる extra_fields.get()はフィールドの値を取り出している
                # ないとcreatesuperuserしてもスタッフユーザーにならないです
                is_staff=extra_fields.get("is_staff"),
                is_superuser=extra_fields.get("is_superuser")
            )   
            user.set_password(password)
            user.save(using=self._db)
            print('success!')
            return user
            # returnされたらSuperuser created successfully.が表示される
    
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        # ↑指定しない限りdefaultでこれが入るという指定
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        # ここはis_staffとかのデフォルト値をセットしているだけ
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # createsuperuserの入力がすべて終わったらprint()された
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        # 例外処理、実際になることはない
        # extra_fields.setdefault("is_staff", Flase)ってすると出てきます（ValueError("")の文字変えると分かると思う
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)

    # with_permはコピペしなくてだいじょうぶ！（特に変更する箇所はないため）

class UserTable(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        (1, '女性'),
        (2, '男性'),
        (3, 'その他')
    ]
    # ユーザーID
    username = models.CharField(verbose_name="ユーザーID", max_length=16, unique=True, validators=[MinLengthValidator(5,16), RegexValidator(r'^[a-zA-Z0-9_]*$',)])
    # メールアドレス
    email = models.EmailField(verbose_name="メールアドレス", unique=True, null=True, blank=False)
    # 誕生日
    birthday = models.DateField(verbose_name="誕生日", null=True, blank=True, default='1900-12-30')
    # アイコン
    icon = models.ImageField(verbose_name="アイコン", default=f'main/icon/default_icon.png', upload_to=savePath, null=True, blank=True)
    # 登録日
    date_joined = models.DateField(verbose_name="登録日", auto_now_add=True)
    # 性別
    gender = models.IntegerField(verbose_name='性別', choices=GENDER_CHOICES, unique=False, default=1, blank=True, null=True)
    # 姓
    myouji = models.CharField(verbose_name="姓", max_length=255)
    # 名
    namae = models.CharField(verbose_name='名', max_length=255)
    # 郵便番号
    post = models.CharField(verbose_name='郵便番号', max_length=9, validators=[RegexValidator(r'^[0-9]{3}-[0-9]{4}$',)])
    # 都道府県
    pref = models.CharField(verbose_name='都道府県名', max_length=255)
    # 市町村
    town = models.CharField(verbose_name='市町村', max_length=255, default='')
    # 住所詳細
    prefDetail = models.CharField(verbose_name='住所詳細', max_length=400)
    # ポイント
    points = models.IntegerField(verbose_name='保有ポイント', default=100)
    mail_deriv = models.BooleanField(verbose_name='メール配信希望', default=False)
    # アクティブユーザーか, 運用停止 -> False
    is_active = models.BooleanField(default=True)
    # adminサイトにははいれる
    is_staff = models.BooleanField(default=False)
    # admin権限あり　わたししかいませ～～～～～～～～～～～～ん
    is_superuser = models.BooleanField(default=False)
    # ユーザーマネージャー
    objects = MyUserManager()
    # emailで識別します
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    # ユーザー作成時のフィールド
    REQUIRED_FIELDS = [
        'email',
    ]
    class Meta:
        verbose_name = _('ユーザーテーブル')
        verbose_name_plural = _('ユーザーテーブル')

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        full_name = '%s %s' % (self.myouji, self.namae)
        return full_name.strip()

    def get_short_name(self):
        return self.namae

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def iconResizer(self):
        img = Image.open(self.icon)
        img_resize = img.resize((256, 256))
        img.close()
        bf = io.BytesIO()
        img_resize.save(fp=bf, format=img.format)
        self.icon.save(name=self.icon.path, content=bf)

class CartTable(models.Model):
    class Meta:
        verbose_name = _('カートテーブル')
        verbose_name_plural = _('カートテーブル')
    
    # フィールド
    cart_id = models.AutoField(primary_key=True, unique=True, verbose_name='カートID', editable=False)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    create = models.DateField(auto_now_add=True, verbose_name='カート作成日時')
    update = models.DateField(auto_now=True, verbose_name='カート更新日時')
    ordered = models.BooleanField(default=False, verbose_name='注文状況')
    def __str__(self):
        return f"最終更新日:{self.update} | カートid:{self.cart_id} | ユーザーid:{self.user_id}"
    
    def get_total(self):
        total = 0
        for item in self.related_cart.all():
            total += item.get_total_price()
        return total

class ItemTable(models.Model):
    class Meta:
        verbose_name = _('商品テーブル')
        verbose_name_plural = _('商品テーブル')
        
    # フィールド
    item_id = models.AutoField(primary_key=True, unique=True, verbose_name='商品ID', editable=False)
    item_name = models.TextField(max_length=30, unique=True, verbose_name='商品名')
    item_name_eng = models.TextField(default=f'',max_length=50, verbose_name='商品名(english)')
    item_img = models.ImageField(default='main/item/default_img.jpg', upload_to=saveItemPath)
    price = models.IntegerField(verbose_name='値段/個')
    sale_flg = models.BooleanField(default=True, verbose_name='販売ステータス')
    slug = models.SlugField(null=True, blank=True, max_length=20, default=f'')
    def __str__(self):
        return f'商品ID:{self.item_id} | 商品名:{self.item_name} | 価格/個:{self.price} | 販売ステータス:{self.sale_flg}'

class CartDetailTable(models.Model):
    class Meta:
        verbose_name = _('カート詳細テーブル')
        verbose_name_plural = _('カート詳細テーブル')

    detail_id = models.AutoField(primary_key=True, unique=True, verbose_name='カート詳細ID', editable=False)
    # username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart_id = models.ForeignKey(CartTable, on_delete=models.CASCADE, verbose_name='カートID', related_name='related_cart', unique=False)
    item_id = models.ForeignKey(ItemTable, on_delete=models.CASCADE, verbose_name='商品ID', related_name='related_cart_item')
    quantity = models.IntegerField(verbose_name='数量', default=1, validators=[MinValueValidator(1), MaxValueValidator(1000)])
    def get_total_price(self):
        return self.quantity * self.item_id.price
    def __str__(self):
        return f'カート詳細ID:{self.detail_id} | カートID:{self.cart_id} |  商品ID:{self.item_id} | 数量:{self.quantity}'
    

from datetime import datetime
class OrderTable(models.Model):
    class Meta:
        verbose_name = _('注文テーブル')
        verbose_name_plural = _('注文テーブル')


    PAY_CHOICE = [
        (1, 'クレジットカード'),
        (2, '代金引換'),
        (3, '後払い決済'),
        (4, '振込')
    ]

    order_id = models.AutoField(primary_key=True, unique=True, verbose_name='注文ID', editable=False)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.TextField(verbose_name='郵便番号', default='', max_length=84, blank=False, validators=[RegexValidator(r'^[0-9]{3}-[0-9]{4}$',)])
    pref = models.TextField(verbose_name='都道府県', default='', max_length=20, blank=False)
    address = models.TextField(verbose_name='住所詳細', default='', max_length=255, blank=False)
    postage = models.IntegerField(verbose_name='送料', default=0, validators=[MinValueValidator(1), MaxValueValidator(9999)])
    town = models.CharField(verbose_name='市町村', max_length=255, default='')
    to_firstname = models.TextField(verbose_name='送り先(名前)',default='', blank=False)
    to_lastname = models.TextField(verbose_name='送り先(苗字)', default='',blank=False)
    create = models.DateField(auto_now_add=True, verbose_name='注文確定日')
    ordered = models.BooleanField(default=False, verbose_name='発送状況')
    arrive = models.DateField(verbose_name='到着予定日')
    pay = models.IntegerField(verbose_name='支払方法', choices=PAY_CHOICE, unique=False, default=1, blank=False)
    total_pay = models.IntegerField(verbose_name='合計金額', default=1)

    def get_total(self):
        total = 0
        for item in self.related_order.all():
            total += item.get_total_price()
        return int(total)
    
    def __str__(self):
        return f'注文ID:{self.order_id} | ユーザーID:{self.user_id}'
    
class OrderDetailTable(models.Model):
    class Meta:
        verbose_name = _('注文詳細テーブル')
        verbose_name_plural = _('注文詳細テーブル')

    detail_id = models.AutoField(primary_key=True, unique=True, verbose_name='注文詳細ID', editable=False)
    order_id = models.ForeignKey(OrderTable, on_delete=models.CASCADE, verbose_name='注文ID', related_name='related_order')
    item_id = models.ForeignKey(ItemTable, on_delete=models.CASCADE, verbose_name='商品ID', related_name='related_order_item')
    quantity = models.IntegerField(verbose_name='数量', default=0, validators=[MinValueValidator(0), MaxValueValidator(1000)])
    def get_total_price(self):
        return self.quantity * self.item_id.price
    def __str__(self):
        return f'注文詳細ID:{self.detail_id} | 注文ID:{self.order_id} |  商品ID:{self.item_id} | 数量:{self.quantity}'