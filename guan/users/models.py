from django.db import models
from django.contrib.auth.models import User

from datetime import date
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    org = models.CharField('Organization', max_length=128, blank=True)
    org_id =models.CharField('Org_id',max_length=5,blank=True)
    telephone = models.CharField('Telephone', max_length=50, blank=True)
    mod_date = models.DateTimeField('Last modified', auto_now=True)
    class Meta:
        verbose_name = 'User Profile'
    def __str__(self):
        return "{}".format(self.user.__str__())

class Goods(models.Model):
    gname = models.CharField(max_length=32)
    rname =models.CharField(max_length=32)#收件人名字
    stel =models.CharField(max_length=11) #发件人电话
    scity =models.CharField(max_length=10) #发件人城市
    saddress =models.CharField(max_length=11) #发件人地址
    rtel =models.CharField(max_length=11) #收件人电话
    gweight = models.FloatField()
    gdest =models.CharField(max_length=20)#目的地城市
    detail =models.CharField(max_length=30) #填写具体地址
    is_active = models.BooleanField() #快递是否签收
    is_cancel =models.BooleanField()  #快递是否被用户取消
    status =models.IntegerField(blank=True)#物流状态 0创建成功 1揽件2入库3出库4路上5入库6出库7派件8签收
    judge = models.CharField(max_length=100,blank=True)#用户评论
    cname = models.CharField(max_length=20,blank=True) #所选上海快递员姓名
    oname = models.CharField(max_length=20,blank=True)#非上海地区快递员姓名
    cs = models.ForeignKey(User, on_delete=models.CASCADE) #外键连接用户
    #ws = models.ForeignKey(Ware, on_delete=models.CASCADE)  #外键连接车辆
    #sas =models.ForeignKey(Trans,blank=True,on_delete=models.CASCADE) #外键连接物流
class Ware(models.Model):
    wname =models.CharField(max_length=10,blank=True)
    capacity =models.IntegerField(default=1000, blank=True)
    restroom =models.IntegerField(blank=True)
    location =models.CharField(max_length=30, blank=True)
    ws =models.ForeignKey(User,on_delete=models.CASCADE)
class GoodsPrice(models.Model):
    prices = models.FloatField()
    ps = models.ForeignKey(Goods, on_delete=models.CASCADE)
class Wage(models.Model):
    wage = models.FloatField(blank=True)
    ps = models.ForeignKey(User, on_delete=models.CASCADE)
class Cars(models.Model):
    cname =models.CharField(max_length=20) #司机名字
    capacity = models.IntegerField(default=1000, blank=True) #车辆的容量
    chu = models.CharField(max_length=20, blank=True) #出发城市
    di = models.CharField(max_length=20, blank=True) #到达城市
    real = models.CharField(max_length=20, blank=True)#目前所在城市
    cc =models.ForeignKey(User, on_delete=models.CASCADE) #外键连接调度员
class Trans(models.Model):
    is_re =models.BooleanField()  #是否揽收
    is_rukush =models.BooleanField() #是否入上海库
    is_chukush = models.BooleanField()  # 是否揽收
    is_chufa = models.BooleanField()  # 是否揽收
    daona = models.CharField(max_length=20, blank=True)  # 到哪儿了
    is_rukuqita = models.BooleanField()  # 是否入其他地方库
    is_chukuqita = models.BooleanField()  # 是否出其他地方库
    is_sign = models.BooleanField()  # 是否签收
    gs =models.ForeignKey(Goods,on_delete=models.CASCADE)

class Deliver(models.Model):
    DEST_CHOICES = ((1, 'one'), (2, 'two'), (3, 'three'), (4, 'four'), (5, 'five'))
    rating = models.PositiveSmallIntegerField('Rating (stars)', blank=False, default=1, choices=DEST_CHOICES)
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(Goods, default=1, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)

    class Meta:
        abstract = True
class DeliverReview(Deliver):
    good = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name="deliver_reviews")