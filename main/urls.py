from django.urls import path
from . import views
app_name= 'main'
urlpatterns = [
    path('CreateUser', views.CreateUser.as_view(), name="CreateUser"),
    path('', views.index, name="index"),
    path('index', views.index, name="index"),
    path('login', views.Login.as_view(), name='login'),
    path('item', views.ItemPage.as_view(), name='item'),
    path('product/<slug:slug>', views.ItemDetail.as_view(), name='product'),
    path('order', views.Order.as_view(), name='order'),
    path('itemdelete/<slug:slug>', views.ItemDelete.as_view(), name='itemdelete'),
    path('complete', views.UserComplete.as_view(), name='complete'),
    path('orderCheck', views.OrderCheck.as_view(), name='orderCheck'),
    path('mypage', views.mypage, name='mypage'),
    path('orderhistory', views.OrderHistory.as_view(), name="orderhistory"),
    path('orderdetail/<pk>', views.OrderDetail.as_view(), name='orderdetail'),
    path('edituser', views.EditUser.as_view(), name='edituser'),
    path('orderComplete', views.OrderComplete.as_view(), name='orderComplete'),
]