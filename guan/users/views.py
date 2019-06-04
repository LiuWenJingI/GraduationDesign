from django.contrib.auth.models import Permission,ContentType,Group
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import ListView
from .models import UserProfile,Wage,Cars
from django.contrib import auth
from .forms import RegistrationForm, LoginForm, ProfileForm, PwdChangeForm, LoginFor, RegisterFormm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.views.decorators.http import require_POST
from utils import restful
from django.shortcuts import redirect,reverse
from utils.captcha.xfzcaptcha import Captcha
from io import BytesIO
from django.http import HttpResponse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import User
from .forms import LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import User, Goods ,GoodsPrice ,Ware
from django.db import connection
from users import models
from .models import Deliver,DeliverReview
User = get_user_model()

# 一般我是这样去设计的：
# {"code":400,"message":"","data":{}}

@require_POST
def log_register(request):
    form = RegisterFormm(request.POST)
    if form.is_valid():
        telephone = form.cleaned_data.get('telephone')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = User.objects.create_user(telephone=telephone,username=username,password=password)
        login(request, user)
        return restful.ok()
    else:
        print(form.get_errors())
        return restful.params_error(message=form.get_errors())
def login_view(request):
    form = LoginFor(request.POST)
    if form.is_valid():
        telephone = form.cleaned_data.get('telephone')
        password = form.cleaned_data.get('password')
        remember = form.cleaned_data.get('remember')
        user = authenticate(request,username=telephone,password=password)
        if user:
            if user.is_active:
                login(request,user)
                if remember:
                    request.session.set_expiry(None)
                else:
                    request.session.set_expiry(0)
                return restful.ok()
            else:
                return restful.unauth(message="您的账号已经被冻结了！")
        else:
            return restful.params_error(message="手机号或者密码错误！")
    else:
        return HttpResponse("错误")
       # return  redirect(reverse('users/loginn.html'))
# errors = form.get_errors()
        # {"password":['密码最大长度不能超过20为！','xxx'],"telephone":['xx','x']}
        #return restful.params_error(message=errors)

def logout_view(request):
    logout(request)
    return redirect(reverse('users/index'))


@require_POST



def img_captcha(request):
    text,image = Captcha.gene_code()
    # BytesIO：相当于一个管道，用来存储图片的流数据
    out = BytesIO()
    # 调用image的save方法，将这个image对象保存到BytesIO中
    image.save(out,'png')
    # 将BytesIO的文件指针移动到最开始的位置
    out.seek(0)

    response = HttpResponse(content_type='image/png')
    # 从BytesIO的管道中，读取出图片数据，保存到response对象上
    response.write(out.read())
    response['Content-length'] = out.tell()

    # 12Df：12Df.lower()
    cache.set(text.lower(),text.lower(),5*60)

    return response


def sms_captcha(request):
    # /sms_captcha/?telephone=xxx
    telephone = request.GET.get('telephone')
    code = Captcha.gene_text()
    cache.set(telephone,code,5*60)
    print('短信验证码：',code)
    # result = aliyunsms.send_sms(telephone,code)
    return restful.ok()


def cache_test(request):
    cache.set('username','zhiliao',60)
    result = cache.get('username')
    print(result)
    return HttpResponse('success')

def register(request):
    if request.method == 'POST':

        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']

            # 使用内置User自带create_user方法创建用户，不需要使用save()
            user = User.objects.create_user(username=username, password=password, email=email)

            # 如果直接使用objects.create()方法后不需要使用save()
            user_profile = UserProfile(user=user)
            user_profile.save()

            return HttpResponseRedirect("/accounts/login/")

    else:
        form = RegistrationForm()

    return render(request, 'users/registration.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('users:profile', args=[user.id]))
            else:
                # 登陆失败
                  return render(request, 'users/login.html', {'form': form,
                               'message': 'Wrong password. Please try again.'})
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})
@login_required
def profile(request, pk):
   user = get_object_or_404(User, pk=pk)
   return render(request, 'users/profile.html', {'user': user})

@login_required
def profile_update(request, pk):
   user = get_object_or_404(User, pk=pk)
   user_profile = get_object_or_404(UserProfile, user=user)

   if request.method == "POST":
       form = ProfileForm(request.POST)

       if form.is_valid():
           user.first_name = form.cleaned_data['first_name']
           user.last_name = form.cleaned_data['last_name']
           user.save()

           user_profile.org = form.cleaned_data['org']
           user_profile.telephone = form.cleaned_data['telephone']
           user_profile.save()

           return HttpResponseRedirect(reverse('users:profile', args=[user.id]))
   else:
       default_data = {'first_name': user.first_name, 'last_name': user.last_name,
                        'org': user_profile.org, 'telephone': user_profile.telephone, }
       form = ProfileForm(default_data)

   return render(request, 'users/profile_update.html', {'form': form, 'user': user})

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/accounts/login/")
@login_required
def pwd_change(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = PwdChangeForm(request.POST)

        if form.is_valid():

            password = form.cleaned_data['old_password']
            username = user.username

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                new_password = form.cleaned_data['password2']
                user.set_password(new_password)
                user.save()
                return HttpResponseRedirect("/accounts/login/")

            else:
                return render(request, 'users/pwd_change.html', {'form': form,
                                                                 'user': user,
                                                                 'message': 'Old password is wrong. Try again'})
    else:
        form = PwdChangeForm()
    return render(request, 'users/pwd_change.html', {'form': form, 'user': user})



def fingoods_list(request):
    c = request.session.get('_auth_user_id')
    g_list = models.Goods.objects.get(cs_id=c)
    #gos_list = models.Goods.objects.all()
    return render(request, 'users/get_goods.html', {'gs_list': g_list})
def new_goods(request):
    if request.method == 'GET':
        gos_list = models.Goods.objects.all()
        return render(request, 'users/new_goods.html', {'gos_list': gos_list})
    elif request.method == 'POST':
        u = request.POST.get('gname', '')
        rn = request.POST.get('rname', '')
        stel =request.POST.get('stel','')
        scity =request.POST.get('scity','')
        saddress =request.POST.get('saddress','')
        rtel =request.POST.get('stel','')
        w = request.POST.get('gweight', '')
        d = request.POST.get('gdest', '')
        de =request.POST.get('detail','')
        ii =0
        i = 1
        cname = request.POST.get('cname', '')
        # u_list = models.User.objects.all(pk)
        c = request.session.get('_auth_user_id')
        print(c)
        models.Goods.objects.create(
            gname=u,
            rname=rn,
            stel=stel,
            scity=scity,
            saddress=saddress,
            rtel=rtel,
            gweight=w,
            gdest=d,
            detail=de,
            is_active=i,
            is_cancel=ii,
            status=0,
            cname=cname,
            cs_id=c,
        )
        az =models.Goods.objects.filter(cs_id=c).order_by('-id').first()
        ad =az.id
        print(ad)
        #az = request.session.get('_users_goods_id')
        models.Trans.objects.create(
            is_re=0,
            is_rukush=0,
            is_chukush=0,
            is_chufa=0,
            is_rukuqita=0,
            is_chukuqita=0,
            is_sign=0,
            gs_id=ad,
        )
        return HttpResponseRedirect(reverse('users:get_prices'))
        #return HttpResponseRedirect(reverse('users:profile', args=c))


class GoodsList(ListView):
    #c = request.session.get('_auth_user_id')
    queryset = Goods.objects.all().order_by('-date')
    context_object_name = 'goods_list'
    template_name = 'users/get_goods.html'
#获取未完成订单列表
def goods_list(request):
    c = request.session.get('_auth_user_id')
    goods_list = Goods.objects.filter(cs_id=c, is_active=1, is_cancel=0).values('id', 'gdest','status', 'gname','gweight').distinct()
    for re in goods_list:
        print(re)
    return render(request, 'users/get_goods.html', {'goods_list': goods_list})
#用户查看已完成订单
def fin_goods_list(request):
    c = request.session.get('_auth_user_id')
    print('sss'+c)
    #cgoods_list = Goods.objects.filter(cname=t, is_active=1).values('id', 'gdest', 'gname', 'gweight').distinct()
    g_list = Goods.objects.filter(cs_id=c, is_active=0, status=8).values('id','judge', 'gdest', 'gname', 'gweight','is_active').distinct()
    for re in g_list:
        print(re)
    return render(request, 'users/get_fingoods.html', {'gs_list': g_list})
#用户添加评论
def judge(request):
    if request.method == 'GET':
        nid = request.GET.get('nid', '')
        gs_list = models.Goods.objects.all()
        return render(request, 'users/judge.html')
    elif request.method == 'POST':
        nid = request.GET.get('nid', '')
        j = request.POST.get('judge', '')
        c = request.session.get('_auth_user_id')
        print(c)
        models.Goods.objects.filter(id=nid).update(
            judge=j)
        gs_list = Goods.objects.filter(cs_id=c,status=8, is_active=0).values('id','judge', 'gdest', 'gname', 'gweight','is_active').distinct()
        for re in gs_list:
            print(re)
        #gs_list =models.Goods.objects.all()
        print('judge')
        return render(request, 'users/get_fingoods.html', {'gs_list': gs_list})
#查看已取消订单
def is_cancel(request):
    c = request.session.get('_auth_user_id')
    # cgoods_list = Goods.objects.filter(cname=t, is_active=1).values('id', 'gdest', 'gname', 'gweight').distinct()
    g_list = Goods.objects.filter(cs_id=c, is_cancel=1).values('id', 'judge', 'gdest', 'gname', 'gweight','is_active').distinct()
    for re in g_list:
        print(re)
    return render(request, 'users/get_cancellsit.html', {'g_list': g_list})

#计算订单金额

def get_prices(request):
    c = request.session.get('_auth_user_id')
    print(c)
    students = Goods.objects.filter(cs_id=c).order_by('-id').first()
    d =students.id
    print(d)
    print(students.gdest)
    print(students.gweight)
    print(students.scity)
    pricess = 0
    if students.scity == '1':
        if students.gdest == '1':
            pricess = (students.gweight - 1) * 3 + 8
        elif students.gdest == '2':
            pricess = (students.gweight - 1) * 2 + 5
        elif students.gdest == '3':
            pricess = (students.gweight - 1) * 9 + 10
        elif students.gdest == '4':
            pricess = (students.gweight - 1) * 2 + 5
        elif students.gdest == '5':
            pricess = (students.gweight - 1) * 6 + 9
        elif students.gdest == '6':
            pricess = (students.gweight - 1) * 6 + 9
    elif students.scity == '2':
        if students.gdest == '1':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 10
        elif students.gdest == '2':  # 北京到北京
            pricess = (students.gweight - 1) * 2 + 5
        elif students.gdest == '3':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 10
        elif students.gdest == '4':  # 北京到北京
            pricess = (students.gweight - 1) * 2 + 6
        elif students.gdest == '5':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 10
        elif students.gdest == '6':  # 北京到北京
            pricess = (students.gweight - 1) * 10 + 12
    elif students.scity == '3':
        if students.gdest == '1':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 13
        elif students.gdest == '2':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 9
        elif students.gdest == '3':  # 北京到北京
            pricess = (students.gweight - 1) * 5 + 8
        elif students.gdest == '4':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 9
        elif students.gdest == '5':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 11
        elif students.gdest == '6':  # 北京到北京
            pricess = (students.gweight - 1) * 7 + 11
    elif students.scity == '4':
        if students.gdest == '1':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 13
        elif students.gdest == '2':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 9
        elif students.gdest == '3':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 10
        elif students.gdest == '4':  # 北京到北京
            pricess = (students.gweight - 1) * 2 + 8
        elif students.gdest == '5':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 11
        elif students.gdest == '6':  # 北京到北京
            pricess = (students.gweight - 1) * 6 + 11
    elif students.scity == '5':
        if students.gdest == '1':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 13
        elif students.gdest == '2':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 9
        elif students.gdest == '3':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 10
        elif students.gdest == '4':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 9
        elif students.gdest == '5':  # 北京到北京
            pricess = (students.gweight - 1) * 2 + 8
        elif students.gdest == '6':  # 北京到北京
            pricess = (students.gweight - 1) * 6 + 11
    elif students.scity == '6':
        if students.gdest == '1':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 13
        elif students.gdest == '2':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 9
        elif students.gdest == '3':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 10
        elif students.gdest == '4':  # 北京到北京
            pricess = (students.gweight - 1) * 4 + 9
        elif students.gdest == '5':  # 北京到北京
            pricess = (students.gweight - 1) * 8 + 11
        elif students.gdest == '6':  # 北京到北京
            pricess = (students.gweight - 1) * 2 + 8
    print(pricess)
    models.GoodsPrice.objects.create(
        prices=pricess,
        ps_id=d)
    prices_list = GoodsPrice.objects.filter(ps_id=d).order_by('-id')
    return render(request, 'users/get_prices.html', {'prices_list': prices_list})
#快递员查看自己工资
def view_wage(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    f_list = Wage.objects.filter(ps_id=t).order_by('-id')
    return render(request,'users/view_wage.html', {'f_list': f_list})
#普通用户寄件取消
def cancerorder(request):
    nid = request.GET.get('nid', '')
    dels = Goods.objects.filter(id=nid).order_by('-id').first()
    t = dels.is_active
    print(t)
    if (t):
        print(nid)
        models.Goods.objects.filter(id=nid).update(
            is_cancel=1)#is_cancel =1 代表取消
        #models.Goods.objects.filter(id=nid).delete()
    return render(request, 'users/sss.html')
#调度员分配快递员
def fen_pei_courier(request):
    nid = request.GET.get('nid', '')
    dels = Goods.objects.filter(id=nid).order_by('-id').first()
    t = dels.scity
    d = dels.gdest
    print('scity'+t)
    print('gdest'+d)
    #1-2北京 3-4上海 5-6深圳 7-8南京 9-10 武汉11-12长沙
    # 1北京 2上海 3深圳 4南京 5武汉6长沙
    if dels.scity == '1':
        if dels.gdest == '1':
            models.Goods.objects.filter(id=nid).update(cname=1,oname=2)
        elif dels.gdest == '2':
            models.Goods.objects.filter(id=nid).update(cname=1,oname=4)
        elif dels.gdest == '3':
            models.Goods.objects.filter(id=nid).update(cname=1, oname=6)
        elif dels.gdest == '4':
            models.Goods.objects.filter(id=nid).update(cname=1, oname=8)
        elif dels.gdest == '5':
            models.Goods.objects.filter(id=nid).update(cname=1, oname=10)
        elif dels.gdest == '6':
            models.Goods.objects.filter(id=nid).update(cname=1, oname=12)
    elif dels.scity == '2':
        if dels.gdest == '1':
            models.Goods.objects.filter(id=nid).update(cname=3, oname=2)
        elif dels.gdest == '2':
            models.Goods.objects.filter(id=nid).update(cname=3, oname=4)
        elif dels.gdest == '3':
            models.Goods.objects.filter(id=nid).update(cname=3, oname=6)
        elif dels.gdest == '4':
            models.Goods.objects.filter(id=nid).update(cname=3, oname=8)
        elif dels.gdest == '5':
            models.Goods.objects.filter(id=nid).update(cname=3, oname=10)
        elif dels.gdest == '6':
            models.Goods.objects.filter(id=nid).update(cname=3, oname=12)
    elif dels.scity == '3':
        if dels.gdest == '1':
            models.Goods.objects.filter(id=nid).update(cname=5, oname=2)
        elif dels.gdest == '2':
            models.Goods.objects.filter(id=nid).update(cname=5, oname=4)
        elif dels.gdest == '3':
            models.Goods.objects.filter(id=nid).update(cname=5, oname=6)
        elif dels.gdest == '4':
            models.Goods.objects.filter(id=nid).update(cname=5, oname=8)
        elif dels.gdest == '5':
            models.Goods.objects.filter(id=nid).update(cname=5, oname=10)
        elif dels.gdest == '6':
            models.Goods.objects.filter(id=nid).update(cname=5, oname=12)
    elif dels.scity == '4':
        if dels.gdest == '1':
            models.Goods.objects.filter(id=nid).update(cname=7, oname=2)
        elif dels.gdest == '2':
            models.Goods.objects.filter(id=nid).update(cname=7, oname=4)
        elif dels.gdest == '3':
            models.Goods.objects.filter(id=nid).update(cname=7, oname=6)
        elif dels.gdest == '4':
            models.Goods.objects.filter(id=nid).update(cname=7, oname=8)
        elif dels.gdest == '5':
            models.Goods.objects.filter(id=nid).update(cname=7, oname=10)
        elif dels.gdest == '6':
            models.Goods.objects.filter(id=nid).update(cname=7, oname=12)
    elif dels.scity == '5':
        if dels.gdest == '1':
            models.Goods.objects.filter(id=nid).update(cname=9, oname=2)
        elif dels.gdest == '2':
            models.Goods.objects.filter(id=nid).update(cname=9, oname=4)
        elif dels.gdest == '3':
            models.Goods.objects.filter(id=nid).update(cname=9, oname=6)
        elif dels.gdest == '4':
            models.Goods.objects.filter(id=nid).update(cname=9, oname=8)
        elif dels.gdest == '5':
            models.Goods.objects.filter(id=nid).update(cname=9, oname=10)
        elif dels.gdest == '6':
            models.Goods.objects.filter(id=nid).update(cname=9, oname=12)
    elif dels.scity == '6':
        if dels.gdest == '1':
            models.Goods.objects.filter(id=nid).update(cname=11, oname=2)
        elif dels.gdest == '2':
            models.Goods.objects.filter(id=nid).update(cname=11, oname=4)
        elif dels.gdest == '3':
            models.Goods.objects.filter(id=nid).update(cname=11, oname=6)
        elif dels.gdest == '4':
            models.Goods.objects.filter(id=nid).update(cname=11, oname=8)
        elif dels.gdest == '5':
            models.Goods.objects.filter(id=nid).update(cname=11, oname=10)
        elif dels.gdest == '6':
            models.Goods.objects.filter(id=nid).update(cname=11, oname=12)
    if (t):
        print(nid)
        models.Goods.objects.filter(id=nid).update(status=1)#status=1 代表快递员已揽件
        #models.Goods.objects.filter(id=nid).delete()
    c = request.session.get('_auth_user_id')
    print(c)
    # goods_list =
    cgoods_list = Goods.objects.filter(is_active=1, status=0, is_cancel=0).values('id', 'gdest', 'gname',
                                                                                  'gweight').distinct()
    return render(request, 'users/fen_pei.html', {'cgoods_list': cgoods_list})
#获取未分配订单
def fen_pei(request):
    c = request.session.get('_auth_user_id')
    e = models.UserProfile.objects.filter(user_id=c).first()
    f = e.org_id
    print(c)
    print(f)
    #goods_list =
    cgoods_list = Goods.objects.filter(is_active=1, scity=f, status=0, is_cancel=0).values('id', 'gdest', 'gname', 'gweight').distinct()
    return render(request, 'users/fen_pei.html', {'cgoods_list': cgoods_list})
#调度员查看本地车辆
def view_cars(request):
    c = request.session.get('_auth_user_id')
    e = models.UserProfile.objects.filter(user_id=c).first()
    f = e.org_id
    print(f)
    if f == '1':
        cgoods_list = models.Cars.objects.filter(real='beijing').values('id','real').distinct()
    elif f == '2':
        cgoods_list = models.Cars.objects.filter(real='shanghai').values('id','real').distinct()
    elif f == '3':
        cgoods_list = models.Cars.objects.filter(real='shenzhen').values('id','real').distinct()
    elif f == '4':
        cgoods_list = models.Cars.objects.filter(real='nanjing').values('id','real').distinct()
    elif f == '5':
        cgoods_list = models.Cars.objects.filter(real='wuhan').values('id','real').distinct()
    elif f == '6':
        cgoods_list = models.Cars.objects.filter(real='changsha').values('id','real').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/view_cars.html', {'cgoods_list': cgoods_list})
#显示专属快递员的专属订单
def edit_goods(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t =students.org_id
    print(t)
    print('id is '+c)
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    cgoods_list = Goods.objects.filter(cname=t, is_active=1).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/cget_goods.html', {'cgoods_list': cgoods_list})
    #return render(request, 'users/cget_goods.html', {'cgoods_list': cgoods_list})
#显示快递员揽收之后入库订单
def ru_ku_goods(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t =students.org_id #先拿到快递员的工号 还是即将派发的入库
    print(t)
    print('id is '+c)
    # 快递是揽收之后入库，
    cgoods_list = Goods.objects.filter(cname=t, is_active=1,status=1).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/cget_goods.html', {'cgoods_list': cgoods_list})
#显示快递员揽收之后出库订单
def chu_ku_goods(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t =students.org_id #先拿到快递员的工号 还是即将派发的入库
    print(t)
    print('id is '+c)
    # 快递是揽收之后入库，
    cgoods_list = Goods.objects.filter(cname=t, is_active=1,status=2).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/c_chu_ku_goods.html', {'cgoods_list': cgoods_list})
#显示快递派送未入库快递
def ru_ku_p_goods(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t =students.org_id #先拿到快递员的工号 还是即将派发的入库
    print(t)
    print('显示快递派送未入库快递')
    print('入库id is '+c)
    cgoods_list = Goods.objects.filter(oname=t, is_active=1, status=4).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/ru_p.html', {'cgoods_list': cgoods_list})
#调度员发工资
def pay_wage(request):
    c = request.session.get('_auth_user_id')
    e = models.UserProfile.objects.filter(user_id=c).first()
    r = models.UserProfile.objects.filter(org='courier').first()
    v = int(e.org_id)
    print("vvv")
    print(type(v))
    print(type(e.org_id))
    #e = models.UserProfile.filter(user_id=c)
    t = e.org_id
    print('org  '+t)
    print('wage' + c)
    if t == '1':
        #print('t' +1)
        models.Wage.objects.create(wage=0,ps_id=v,)
        models.Wage.objects.create(wage=0,ps_id=v+1,)
    elif t == '2':
        models.Wage.objects.create(wage=0, ps_id=v + 1, )
        models.Wage.objects.create(wage=0, ps_id=v + 2, )
    elif t == '3':
        models.Wage.objects.create(wage=0, ps_id=v + 2, )
        models.Wage.objects.create(wage=0, ps_id=v + 3, )
    elif t == '4':
        models.Wage.objects.create(wage=0, ps_id=v + 3, )
        models.Wage.objects.create(wage=0, ps_id=v + 4, )
    elif t == '5':
        models.Wage.objects.create(wage=0, ps_id=v + 4, )
        models.Wage.objects.create(wage=0, ps_id=v + 5, )
    elif t == '6':
        models.Wage.objects.create(wage=0, ps_id=v + 5, )
        models.Wage.objects.create(wage=0, ps_id=v + 6, )
    #models.Wage.objects.filter(id=c).create(wage=0,ps_id=c,)
    return render(request, 'users/baby.html')
#def cal_wage(request):

#真正入库揽收订单
def ru_ku_done_goods(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    f = Wage.objects.filter(ps_id=t).order_by('-id').first()
    g = f.wage
    y = f.id
    models.Wage.objects.filter(id=y).update(
        wage=g + 1)
    nid = request.GET.get('nid', '') #获得订单id
    models.Goods.objects.filter(id=nid).update(
        status=2)
    #操作仓库
    ss =Goods.objects.get(id=nid)
    sq =Ware.objects.filter(location=ss.scity).first()
    b = sq.restroom
    print('chu fa city is'+ss.scity)
    print('真正入库揽收订单')
    if ss.scity == '1':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b-1)
    elif ss.scity == '2':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b - 1)
    elif ss.scity == '3':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b - 1)
    elif ss.scity == '4':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b - 1)
    elif ss.scity == '5':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b - 1)
    elif ss.scity == '6':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b - 1)
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    print(t)
    print('id is ' + c)
    cgoods_list = Goods.objects.filter(cname=t, is_active=1,status=1).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/cget_goods.html', {'cgoods_list': cgoods_list})
#入库派送订单
def ru_ku_p_o(request):
    nid = request.GET.get('nid', '')  # 获得订单id
    models.Goods.objects.filter(id=nid).update(
        status=5)
    # 操作仓库
    ss = Goods.objects.get(id=nid)
    sq = Ware.objects.filter(location=ss.gdest).first()
    b = sq.restroom
    print('b')
    print(b)
    print('chu fa city is' + ss.scity)
    print(ss.gdest)
    print('真正订单')
    if ss.gdest == '1':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
    elif ss.gdest == '2':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
    elif ss.gdest == '3':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
    elif ss.gdest == '4':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
    elif ss.gdest == '5':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
    elif ss.gdest == '6':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    print(t)
    print('id is ' + c)
    cgoods_list = Goods.objects.filter(oname=t, is_active=1, status=4).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/ru_p.html', {'cgoods_list': cgoods_list})
def ru_ku_p_done_goods(request):
    nid = request.GET.get('nid', '') #获得订单id
    d = request.session.get('_auth_user_id')
    d = int(d)
    models.Goods.objects.filter(id=nid).update(
        status=5)
    #操作仓库
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    f = int(students.org_id)
    c = f/2
    print('部门编号除以二')
    print(f)
    ss =Goods.objects.get(id=nid)
    sq =Ware.objects.filter(location=ss.scity).first()
    b = sq.restroom
    print('chu fa city is'+ss.scity)
    if ss.gdest == '1':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
        print(1)
    elif ss.gdest == '2':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
        print(2)
    elif ss.gdest == '3':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
        print(3)
    elif ss.gdest == '4':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
        print(4)
    elif ss.gdest == '5':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
        print(5)
    elif ss.gdest == '6':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b - 1)
        print(6)
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    print(t)
    print('id is ' + c)
    cgoods_list = Goods.objects.filter(oname=t, is_active=1,status=4).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/ru_p.html', {'cgoods_list': cgoods_list})
#显示快递派送未出库快递
def chu_ku_p_goods(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t =students.org_id #先拿到快递员的工号 还是即将派发的入库
    print('显示快递派送未出库快递')
    print(t)
    print('入库id is '+c)
    # 快递是揽收之后入库，
    cgoods_list = Goods.objects.filter(oname=t, is_active=1, status=5).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/chu_p.html', {'cgoods_list': cgoods_list})
#出库派送订单
def chu_ku_p_done_goods(request):
    nid = request.GET.get('nid', '') #获得订单id
    d = request.session.get('_auth_user_id')
    print('出库派送订单')
    d = int(d)
    c = d/2
    models.Goods.objects.filter(id=nid).update(
        status=6)
    #操作仓库
    ss =Goods.objects.get(id=nid)
    sq =Ware.objects.filter(location=ss.gdest).first()
    b = sq.restroom
    print('chu fa city is'+ss.scity)
    if ss.gdest == '1':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b + 1)
    elif ss.gdest == '2':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b + 1)
    elif ss.gdest == '3':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b + 1)
    elif ss.gdest == '4':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b + 1)
    elif ss.gdest == '5':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b + 1)
    elif ss.gdest == '6':
        models.Ware.objects.filter(location=ss.gdest).update(
            restroom=b + 1)
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    print(t)
    print('id is ' + c)
    cgoods_list = Goods.objects.filter(oname=t, is_active=1,status=5).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/chu_p.html',{'cgoods_list': cgoods_list})
#显示待派送快递
def p_goods(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t =students.org_id #先拿到快递员的工号 还是即将派发的入库
    print(t)
    print('入库id is '+c)
    # 快递是揽收之后入库，
    cgoods_list = Goods.objects.filter(oname=t, is_active=1, status=6).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/p.html', {'cgoods_list': cgoods_list})
#获得待签收订单列表
def get_sign_list(request):
    c = request.session.get('_auth_user_id')
    students = User.objects.filter(id=c).order_by('-id').first()
    t =students.username #
    print(t)
    print('获得待签收订单列表name is '+c)
    # 快递是揽收之后入库，
    cgoods_list = Goods.objects.filter(rname=t,is_active=0, status=7).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/signing.html', {'cgoods_list': cgoods_list})
#用户签收派送订单
def user_p_done_goods(request):
    nid = request.GET.get('nid', '') #获得订单id

    models.Goods.objects.filter(id=nid).update(
        status=8, is_active=0)
    c = request.session.get('_auth_user_id')
    students = User.objects.filter(id=c).order_by('-id').first()
    t = students.username  #
    print(t)
    print('入库id is ' + c)
    # 快递是揽收之后入库，
    cgoods_list = Goods.objects.filter(oname=t, is_active=1, status=7).values('id', 'gdest', 'gname','gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/signing.html', {'cgoods_list': cgoods_list})
#快递员签收派送订单
def p_done_goods(request):
    nid = request.GET.get('nid', '') #获得订单id
    d = request.session.get('_auth_user_id')
    d = int(d)
    c = d / 2
    print('快递员签收派送订单')
    models.Goods.objects.filter(id=nid).update(
        status=7, is_active=0)
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id  # 先拿到快递员的工号 还是即将派发的入库
    print(t)
    print('入库id is ' + c)
    o = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    f = Wage.objects.filter(ps_id=t).order_by('-id').first()
    g = f.wage
    y = f.id
    models.Wage.objects.filter(id=y).update(
        wage=g + 1)
    # 快递是揽收之后入库，
    cgoods_list = Goods.objects.filter(oname=t, is_active=1, status=6).values('id', 'gdest', 'gname','gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/p.html', {'cgoods_list': cgoods_list})
#司机发车
def fa_che(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id  # 先拿到司机的编号
    print(t)
    print('id is ' + c)
    # 快递是揽收之后入库，
    if t == '1':
        models.Cars.objects.filter(cname='beijing1').update(real='shanghai')
    elif t == '2':
        models.Cars.objects.filter(cname='beijing2').update(real='shenzhen')
    elif t == '3':
        models.Cars.objects.filter(cname='beijing3').update(real='nanjing')
    elif t == '4':
        models.Cars.objects.filter(cname='beijing4').update(real='wuhan')
    elif t == '5':
        models.Cars.objects.filter(cname='beijing5').update(real='changsha')
    elif t == '6':
        models.Cars.objects.filter(cname='shanghai1').update(real='shenzhen')
    elif t == '7':
        models.Cars.objects.filter(cname='shanghai2').update(real='nanjing')
    elif t == '8':
        models.Cars.objects.filter(cname='shanghai3').update(real='wuhan')
    elif t == '9':
        models.Cars.objects.filter(cname='shanghai4').update(real='changsha')
    elif t == '10':
        models.Cars.objects.filter(cname='shenzhen1').update(real='nanjing')
    elif t == '11':
        models.Cars.objects.filter(cname='shenzhen2').update(real='wuhan')
    elif t == '12':
        models.Cars.objects.filter(cname='shenzhen3').update(real='changsha')
    elif t == '13':
        models.Cars.objects.filter(cname='nanjing1').update(real='wuhan')
    elif t == '14':
        models.Cars.objects.filter(cname='nanjing2').update(real='changsha')
    elif t == '15':
        models.Cars.objects.filter(cname='wuhan1').update(real='changsha')
    return render(request, 'users/cars.html')
def hui_cheng(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id  # 先拿到司机的编号
    print(t)
    print('huicheng id is ' + c)
    # 快递是揽收之后入库，
    if t == '1':
        models.Cars.objects.filter(cname='beijing1').update(real='beijing')
    elif t == '2':
        models.Cars.objects.filter(cname='beijing2').update(real='beijing')
    elif t == '3':
        models.Cars.objects.filter(cname='beijing3').update(real='beijing')
    elif t == '4':
        models.Cars.objects.filter(cname='beijing4').update(real='beijing')
    elif t == '5':
        models.Cars.objects.filter(cname='beijing5').update(real='beijing')
    elif t == '6':
        models.Cars.objects.filter(cname='shanghai1').update(real='shanghai')
    elif t == '7':
        models.Cars.objects.filter(cname='shanghai2').update(real='shanghai')
    elif t == '8':
        models.Cars.objects.filter(cname='shanghai3').update(real='shanghai')
    elif t == '9':
        models.Cars.objects.filter(cname='shanghai4').update(real='shanghai')
    elif t == '10':
        models.Cars.objects.filter(cname='shenzhen1').update(real='shenzhen')
    elif t == '11':
        models.Cars.objects.filter(cname='shenzhen2').update(real='shenzhen')
    elif t == '12':
        models.Cars.objects.filter(cname='shenzhen3').update(real='shenzhen')
    elif t == '13':
        models.Cars.objects.filter(cname='nanjing1').update(real='nanjing')
    elif t == '14':
        models.Cars.objects.filter(cname='nanjing2').update(real='nanjing')
    elif t == '15':
        models.Cars.objects.filter(cname='wuhan1').update(real='wuhan')
    return render(request, 'users/cars.html')
#司机查看装卸快递
def zh_xie_goods(request):
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id  # 先拿到司机的编号
    print(t)
    print('id is ' + c)
    # 快递是揽收之后入库，
    if t == '1':
        cgoods_list = Goods.objects.filter(cname=1,oname=4, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                  'gweight').distinct()
        j = models.Cars.objects.filter(cname='beijing1').order_by('-id').first()
        x = j.real
        if x == 'shanghai':
            rgoods_list = Goods.objects.filter(cname=3, oname=2, is_active=1, status=3)
        elif x == 'beijing':
            rgoods_list = {}
    elif t == '2':
        cgoods_list = Goods.objects.filter(cname=1,oname=6, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='beijing2').order_by('-id').first()
        x = j.real
        if x == 'shenzhen':
            rgoods_list = Goods.objects.filter(cname=5, oname=2, is_active=1, status=3)
        elif x == 'beijing':
            rgoods_list = {}
    elif t == '3':
        cgoods_list = Goods.objects.filter(cname=1,oname=8,is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='beijing3').order_by('-id').first()
        x = j.real
        if x == 'nanjing':
            rgoods_list = Goods.objects.filter(cname=7,oname=2,is_active=1,status=3)
        elif x == 'beijing':
            rgoods_list = {}
    elif t == '4':
        cgoods_list = Goods.objects.filter(cname=1,oname=10, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='beijing4').order_by('-id').first()
        x = j.real
        if x == 'wuhan':
            rgoods_list = Goods.objects.filter(cname=9, oname=2, is_active=1, status=3)
        elif x == 'beijing':
            rgoods_list = {}
    elif t == '5':
        cgoods_list = Goods.objects.filter(cname=1,oname=12, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='beijing5').order_by('-id').first()
        x = j.real
        if x == 'changsha':
            rgoods_list = Goods.objects.filter(cname=11, oname=2, is_active=1, status=3)
        elif x == 'beijing':
            rgoods_list = {}
    elif t == '6':
        cgoods_list = Goods.objects.filter(cname=3,oname=6, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='shanghai1').order_by('-id').first()
        x = j.real
        if x == 'shenzhen':
            rgoods_list = Goods.objects.filter(cname=5, oname=4, is_active=1, status=3)
        elif x == 'shanghai':
            rgoods_list = {}
    elif t == '7':
        cgoods_list = Goods.objects.filter(cname=3,oname=8, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='shanghai2').order_by('-id').first()
        x = j.real
        if x == 'nanjing':
            rgoods_list = Goods.objects.filter(cname=7, oname=4, is_active=1, status=3)
        elif x == 'shanghai':
            rgoods_list = {}
    elif t == '8':
        cgoods_list = Goods.objects.filter(cname=3,oname=10, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='shanghai3').order_by('-id').first()
        x = j.real
        if x == 'wuhan':
            rgoods_list = Goods.objects.filter(cname=9, oname=4, is_active=1, status=3)
        elif x == 'shanghai':
            rgoods_list = {}
    elif t == '9':
        cgoods_list = Goods.objects.filter(cname=3,oname=12, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='shanghai4').order_by('-id').first()
        x = j.real
        if x == 'changsha':
            rgoods_list = Goods.objects.filter(cname=11, oname=4, is_active=1, status=3)
        elif x == 'shanghai':
            rgoods_list = {}
    elif t == '10':
        cgoods_list = Goods.objects.filter(cname=5,oname=8,is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='shenzhen1').order_by('-id').first()
        x = j.real
        if x == 'nanjing':
            rgoods_list = Goods.objects.filter(cname=7, oname=6, is_active=1, status=3)
        elif x == 'shenzhen':
            rgoods_list = {}
    elif t == '11':
        cgoods_list = Goods.objects.filter(cname=5,oname=10, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='shenzhen2').order_by('-id').first()
        x = j.real
        if x == 'wuhan':
            rgoods_list = Goods.objects.filter(cname=9, oname=6, is_active=1, status=3)
        elif x == 'shenzhen':
            rgoods_list = {}
    elif t == '12':
        cgoods_list = Goods.objects.filter(cname=5,oname=12, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='shenzhen3').order_by('-id').first()
        x = j.real
        if x == 'changsha':
            rgoods_list = Goods.objects.filter(cname=11, oname=6, is_active=1, status=3)
        elif x == 'shenzhen':
            rgoods_list = {}
    elif t == '13':
        cgoods_list = Goods.objects.filter(cname=7,oname=10,  is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='nanjing1').order_by('-id').first()
        x = j.real
        if x == 'wuhan':
            rgoods_list = Goods.objects.filter(cname=9, oname=8, is_active=1, status=3)
        elif x == 'nanjing':
            rgoods_list = {}
    elif t == '14':
        cgoods_list = Goods.objects.filter(cname=7,oname=12,  is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='nanjing2').order_by('-id').first()
        x = j.real
        if x == 'changsha':
            rgoods_list = Goods.objects.filter(cname=11, oname=8, is_active=1, status=3)
        elif x == 'nanjing':
            rgoods_list = {}
    elif t == '15':
        cgoods_list = Goods.objects.filter(cname=9,oname=12,  is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                              'gweight').distinct()
        j = models.Cars.objects.filter(cname='wuhan1').order_by('-id').first()
        x = j.real
        if x == 'changsha':
            rgoods_list = Goods.objects.filter(cname=11, oname=10, is_active=1, status=3)
        elif x == 'wuhan':
            rgoods_list = {}
    for re in cgoods_list:
        print(re)
    return render(request, 'users/v_zh_xie_goods.html', {'cgoods_list': cgoods_list,'rgoods_list':rgoods_list})
#真正装卸
def zh_xie_goods_done(request):
    nid = request.GET.get('nid', '')  # 获得订单id
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id  # 先拿到司机的编号
    print(t)
    print('id is ' + c)
    # 快递是揽收之后入库，
    if t == '1':
        cgoods_list = Goods.objects.filter(cname=1, oname=3, is_active=1, status=3).values('id', 'gdest', 'gname','gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '2':
        cgoods_list = Goods.objects.filter(cname=1, oname=6, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                           'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '3':
        cgoods_list = Goods.objects.filter(cname=1, oname=8, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                           'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '4':
        cgoods_list = Goods.objects.filter(cname=1, oname=10, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                            'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '5':
        cgoods_list = Goods.objects.filter(cname=1, oname=12, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                            'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '6':
        cgoods_list = Goods.objects.filter(cname=3, oname=6, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                           'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '7':
        cgoods_list = Goods.objects.filter(cname=3, oname=8, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                           'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '8':
        cgoods_list = Goods.objects.filter(cname=3, oname=10, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                            'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '9':
        cgoods_list = Goods.objects.filter(cname=3, oname=12, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                            'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '10':
        cgoods_list = Goods.objects.filter(cname=5, oname=8, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                           'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '11':
        cgoods_list = Goods.objects.filter(cname=5, oname=10, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                            'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '12':
        cgoods_list = Goods.objects.filter(cname=5, oname=12, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                            'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '13':
        cgoods_list = Goods.objects.filter(cname=7, oname=10, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                            'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '14':
        cgoods_list = Goods.objects.filter(cname=7, oname=12, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                            'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    elif t == '15':
        cgoods_list = Goods.objects.filter(cname=9, oname=12, is_active=1, status=3).values('id', 'gdest', 'gname',
                                                                                            'gweight').distinct()
        models.Goods.objects.filter(id=nid).update(status=4)
    return render(request, 'users/v_zh_xie_goods.html', {'cgoods_list': cgoods_list})
#真正出库揽收订单
def chu_ku_done_goods(request):
    nid = request.GET.get('nid', '') #获得订单id
    models.Goods.objects.filter(id=nid).update(
        status=3)

    #操作仓库
    ss =Goods.objects.get(id=nid)
    sq =Ware.objects.filter(location=ss.scity).first()
    b = sq.restroom
    print('chu fa city is'+ss.scity)
    if ss.scity == '1':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b + 1)
    elif ss.scity == '2':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b + 1)
    elif ss.scity == '3':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b + 1)
    elif ss.scity == '4':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b + 1)
    elif ss.scity == '5':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b + 1)
    elif ss.scity == '6':
        models.Ware.objects.filter(location=ss.scity).update(
            restroom=b + 1)
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    print(t)
    print('id is ' + c)
    cgoods_list = Goods.objects.filter(cname=t, is_active=1,status=2).values('id', 'gdest', 'gname', 'gweight').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/c_chu_ku_goods.html', {'cgoods_list': cgoods_list})
#初始化仓库
def init_wares(request):
    c = request.session.get('_auth_user_id')
    print(c)
    b ='bj_ware'
    s ='sh_ware'
    shen ='sz_ware'
    n ='nj_ware'
    w ='wh_ware'
    cs ='cs_ware'
    #students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    e =students.org_id
    print('id is'+e)
    if e == '1':
        models.Ware.objects.create(
            wname=b,
            capacity=1000,
            restroom=1000,
            location=1,
            ws_id=e,
        )
    elif e == '2':
        models.Ware.objects.create(
            wname=s,
            capacity=1000,
            restroom=1000,
            location=2,
            ws_id=e,
        )
    elif e == '3':
        models.Ware.objects.create(
            wname=shen,
            capacity=1000,
            restroom=1000,
            location=3,
            ws_id=e,
        )
    elif e == '4':
        models.Ware.objects.create(
            wname=n,
            capacity=1000,
            restroom=1000,
            location=4,
            ws_id=e,
        )
    elif e == '5':
        models.Ware.objects.create(
            wname=w,
            capacity=1000,
            restroom=1000,
            location=5,
            ws_id=e,
        )
    elif e == '6':
        models.Ware.objects.create(
            wname=cs,
            capacity=1000,
            restroom=1000,
            location=6,
            ws_id=e,
        )
    return render(request, 'users/baby.html')
#初始化车辆
def init_cars(request):
    z = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=z).order_by('-id').first()
    e = students.org_id
    b = 'beijing'
    s = 'shanghai'
    sh = 'shenzhen'
    n = 'nanjing'
    w = 'wuhan'
    c = 'changsha'
    b1 = 'beijing1'
    b2 = 'beijing2'
    b3 = 'beijing3'
    b4 = 'beijing4'
    b5 = 'beijing5'
    s1 = 'shanghai1'
    s2 = 'shanghai2'
    s3 = 'shanghai3'
    s4 = 'shanghai4'
    sh1 = 'shenzhen1'
    sh2 = 'shenzhen2'
    sh3 = 'shenzhen3'
    n1 = 'nanjing1'
    n2 = 'nanjing2'
    w1 = 'wuhan1'
    if e == '1':
        models.Cars.objects.create(
            cname=b1,
            capacity=1000,
            chu=b,
            di=s,
            real=b,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=b2,
            capacity=1000,
            chu=b,
            di=sh,
            real=b,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=b3,
            capacity=1000,
            chu=b,
            di=n,
            real=b,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=b4,
            capacity=1000,
            chu=b,
            di=w,
            real=b,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=b5,
            capacity=1000,
            chu=b,
            di=c,
            real=b,
            cc_id=e,
        )
    if e == '2':
        models.Cars.objects.create(
            cname=s1,
            capacity=1000,
            chu=s,
            di=sh,
            real=s,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=s2,
            capacity=1000,
            chu=s,
            di=n,
            real=s,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=s3,
            capacity=1000,
            chu=s,
            di=w,
            real=s,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=s4,
            capacity=1000,
            chu=s,
            di=c,
            real=s,
            cc_id=e,
        )
    if e == '3':
        models.Cars.objects.create(
            cname=sh1,
            capacity=1000,
            chu=sh,
            di=n,
            real=sh,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=sh2,
            capacity=1000,
            chu=sh,
            di=w,
            real=sh,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=sh3,
            capacity=1000,
            chu=sh,
            di=c,
            real=sh,
            cc_id=e,
        )
    if e == '4':
        models.Cars.objects.create(
            cname=n1,
            capacity=1000,
            chu=n,
            di=w,
            real=n,
            cc_id=e,
        )
        models.Cars.objects.create(
            cname=n2,
            capacity=1000,
            chu=n,
            di=c,
            real=n,
            cc_id=e,
        )
    if e == '5':
        models.Cars.objects.create(
            cname=w1,
            capacity=1000,
            chu=w,
            di=c,
            real=w,
            cc_id=e,
        )
    return render(request, 'users/baby.html')
#查看所有货物价格
def view_all_price(request):
    price_list = models.GoodsPrice.objects.all()
    return render(request,'users/view_all_price.html',{'price_list': price_list})
#计算本月盈余
def cal_monthly(request):
    r = 0
    rt = 0
    price_list = models.GoodsPrice.objects.all()
    for re in price_list:
        r = r + re.prices
    print('sum money')
    print(r)
    for i in range(1, 12):
        c_list = Wage.objects.filter(ps_id=i).order_by('-id').first()
        a = c_list.wage
        rt = rt+a
    print('aaaaa')
    print(rt)
    rest = r - rt
    rest = rest - 12000
    return render(request, 'users/view.html', locals())
#快递员完成订单
def fin(request):
    nid = request.GET.get('nid', '')
    i = 0
    models.Goods.objects.filter(id=nid).update(
        is_active=i)
    c = request.session.get('_auth_user_id')
    students = UserProfile.objects.filter(user_id=c).order_by('-id').first()
    t = students.org_id
    f = Wage.objects.filter(ps_id=t).order_by('-id').first()
    g = f.wage
    y = f.id
    models.Wage.objects.filter(id=y).update(
        wage=g + 1)
    cgoods_list = Goods.objects.filter(cname=t, is_active=1).values('id', 'gdest', 'gname', 'gweight','is_active').distinct()
    for re in cgoods_list:
        print(re)
    return render(request, 'users/cget_goods.html', {'cgoods_list': cgoods_list})
    #return render(request, 'users/cget_goods.html')
def review_create(request,pk):
    if request.method == 'GET':
        print("reget")
        print(pk)
        #gos_list = models.Goods.objects.all()
        comment = request.GET.get('comment','')
        rating = request.GET.get('rating', '')
        review = models.DeliverReview.objects.create(
            rating=rating,
            comment=comment,
            user=request.user,
            good=pk)
        review.save()
        gre_list = models.DeliverReview.objects.all()
        return render(request, 'users/s.html', {'gre_list': gre_list})
    elif request.method == 'POST':
        print("repost")
        print(pk)
        rating = request.POST.get('rating', '')
        comment = request.POST.get('comment', '')
        # u_list = models.User.objects.all(pk)
        #c = request.session.get('_auth_user_id')
        #print(c)
        review = DeliverReview(
            rating=request.POST.get['rating'],
            comment=request.POST.get['comment'],
            user=request.user,
            good=pk)
        review.save()
        review_list = models.DeliverReview.objects.all()
        return render(request, 'users/s.html', {'review_list': review_list})
        #return HttpResponseRedirect(reverse('users:review_create'))
def del_reviews(request,pk):
    if request.method == "GET":
        print("delget")
        print(pk)
        #obj = models.Goods.objects.get(id=pk)
        #return render(request, '/users/s.html', {'obj': obj})
        return HttpResponseRedirect(reverse('users:review_create', args=[pk]))
    elif request.method == "POST":
        print("delpost")
        print(pk)
        return HttpResponseRedirect(reverse('users:review_create', args=[pk]))
#快递员中心
def courier(request):
    return render(request, 'users/courier.html')
#会计财务中心
def couriers(request):
    return render(request, 'users/couriers.html')
#调度员中心
def cour(request):
    return render(request, 'users/baby.html')
def cars(request):
    return render(request, 'users/cars.html')
def kuai(request):
    pass
def new_account(request):
    co_list = models.GoodsPrice.objects.all()
    return render(request, 'users/account.html', {'co_list': co_list})
