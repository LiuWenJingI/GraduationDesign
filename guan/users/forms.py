import re
from django import forms
from django.core.cache import cache
from .models import User

class FormMixin(object):
    def get_errors(self):
        if hasattr(self,'errors'):
            errors = self.errors.get_json_data()
            new_errors = {}
            for key, message_dicts in errors.items():
                messages = []
                for message in message_dicts:
                    messages.append(message['message'])
                new_errors[key] = messages
            return new_errors
        else:
            return {}
#不是这个
class RegisterFormm(forms.Form,FormMixin):
    telephone = forms.CharField(max_length=11)
    username = forms.CharField(max_length=20)
    password1 = forms.CharField(max_length=20, min_length=6,
                               error_messages={"max_length": "密码最多不能超过20个字符！", "min_length": "密码最少不能少于6个字符！"})
    password2 = forms.CharField(max_length=20, min_length=6,
                                error_messages={"max_length": "密码最多不能超过20个字符！", "min_length": "密码最少不能少于6个字符！"})
    img_captcha = forms.CharField(min_length=4,max_length=4)
    sms_captcha = forms.CharField(min_length=4,max_length=4)

    def clean(self):
        cleaned_data = super(RegisterFormm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError('两次密码输入不一致！')

        img_captcha = cleaned_data.get('img_captcha')
        cached_img_captcha = cache.get(img_captcha.lower())
        if not cached_img_captcha or cached_img_captcha.lower() != img_captcha.lower():
            raise forms.ValidationError("图形验证码错误！")

        telephone = cleaned_data.get('telephone')
        sms_captcha = cleaned_data.get('sms_captcha')
        cached_sms_captcha = cache.get(telephone)

        if not cached_sms_captcha or cached_sms_captcha.lower() != sms_captcha.lower():
            raise forms.ValidationError('短信验证码错误！')

        exists = User.objects.filter(telephone=telephone).exists()
        if exists:
            forms.ValidationError('该手机号码已经被注册！')

        return cleaned_data


#不是这个
class LoginFor(forms.Form,FormMixin):
    telephone = forms.CharField(max_length=11)
    password = forms.CharField(max_length=20,min_length=6,error_messages={"max_length":"密码最多不能超过20个字符！","min_length":"密码最少不能少于6个字符！"})
    remember = forms.IntegerField(required=False)
class RegistrationForm(forms.Form):
    username = forms.CharField(label='用户名 ', max_length=50)
    email = forms.EmailField(label='电子邮件',)
    password1 = forms.CharField(label='密码  ', widget=forms.PasswordInput)
    password2 = forms.CharField(label='重复密码', widget=forms.PasswordInput)
    # Use clean methods to define custom validation rules
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 6:
            raise forms.ValidationError("用户名不能少于6个字符")
        elif len(username) > 50:
            raise forms.ValidationError("用户名太长了.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if len(filter_result) > 0:
                raise forms.ValidationError("用户名已存在")
        return username
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email_check(email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) > 0:
                raise forms.ValidationError("邮箱已存在")
        else:
            raise forms.ValidationError("邮箱格式不正确")
        return email
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 6:
            raise forms.ValidationError("密码不能少于6个字符")
        elif len(password1) > 20:
            raise forms.ValidationError("密码不能大于20个字符")
        return password1
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次密码输入不一致，请重新输入！")
        return password2
def email_check(email):
    pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
    return re.match(pattern, email)


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=50)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    # Use clean methods to define custom validation rules
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if email_check(username):
            filter_result = User.objects.filter(email__exact=username)
            if not filter_result:
                raise forms.ValidationError("邮箱不存在")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if not filter_result:
                raise forms.ValidationError("用户名不存在，请先注册！")
        return username
class ProfileForm(forms.Form):
   first_name = forms.CharField(label='名', max_length=50, required=False)
   last_name = forms.CharField(label='姓', max_length=50, required=False)
   org = forms.CharField(label='部门', max_length=50, required=False)
   org_id = forms.CharField(label='部门编号', max_length=5, required=False)
   telephone = forms.CharField(label='电话号码', max_length=50, required=False)
class PwdChangeForm(forms.Form):
    old_password = forms.CharField(label='老密码', widget=forms.PasswordInput)
    password1 = forms.CharField(label='新密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='重复新密码', widget=forms.PasswordInput)
    # Use clean methods to define custom validation rules
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 6:
            raise forms.ValidationError("密码太短了，请输入6个字符以上.")
        elif len(password1) > 20:
            raise forms.ValidationError("密码太长了，请输入20个字符以下.")
        return password1
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次密码不匹配，请重输！")
        return password2
