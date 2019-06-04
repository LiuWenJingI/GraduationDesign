from django.urls import path, re_path
from . import views
# 查看餐厅列表
# 查看餐厅详情, 如/myrestaurants/restaurant/1/
# 创建餐厅, 如：/myrestaurants/restaurant/create/
# 编辑餐厅详情, 如: /myrestaurants/restaurant/1/edit/
# 前4个功能性页面的URL见教程第一部分
# 创建菜品 ex.: /myrestaurants/restaurant/1/dishes/create/
# 编辑菜品, ex.: /myrestaurants/restaurant/1/dishes/1/edit/
# 查看菜品信息 ex: /myrestaurants/restaurants/1/dishes/1/
# 创建餐厅评论, /myrestaurants/restaurant/1/reviews/create/
# namespace
app_name = 'rest'
urlpatterns = [
    re_path(r'^rest/$', views.RestaurantList.as_view(), name='restaurant_list'),
    re_path(r'^rest/list/$', views.res_list, name='res_list'),
    re_path(r'^rest/createreview/$', views.rest_review, name='createreview'),
    re_path(r'^rest/(?P<pkk>\d+)/create_review/$', views.rest_review, name='create_review'),
    re_path(r'^rest/(?P<pk>\d+)/$',views.RestaurantDetail.as_view(), name='restaurant_detail'),
    re_path(r'^rest/create/$', views.RestaurantCreate.as_view(), name='restaurant_create'),
    re_path(r'^rest/(?P<pk>\d+)/edit/$',views.RestaurantEdit.as_view(), name='restaurant_edit'),
    re_path(r'^rest/(?P<pk>\d+)/dishes/create/$',views.DishCreate.as_view(), name='dish_create'),
    re_path(r'^rest/(?P<pkr>\d+)/dishes/(?P<pk>\d+)/edit/$',views.DishEdit.as_view(), name='dish_edit'),
    re_path(r'^rest/(?P<pkr>\d+)/dishes/(?P<pk>\d+)/$',views.DishDetail.as_view(), name='dish_detail'),
    re_path(r'^rest/(?P<pk>\d+)/reviews/create/$',views.review_create,  name='review_create'),
    re_path(r'^rest/deliver_review/$', views.deliver_review,  name='deliver_review'),

]


