from django.shortcuts import render
from  users.models import GoodsPrice
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView
from .models import RestaurantReview, Restaurant, Dish ,Deliver,DeliverReview
from .forms import RestaurantForm, DishForm
from rest import models
from django.shortcuts import render,redirect
#def get_context_data(self, **kwargs):
   # queryset = Restaurant.objects.all().order_by('-date')
   # context = super(RestaurantDetail, self).get_context_data(**kwargs)
    #return context
#queryset = Restaurant.objects.all().order_by('-date')
#context_object_name = 'latest_restaurant_list'
#template_name = 'myrestaurants/restaurant_list.html'
class RestaurantList(ListView):
    #c = request.session.get('_auth_user_id')
    queryset = Restaurant.objects.all().order_by('-date')
    context_object_name = 'latest_restaurant_list'
    template_name = 'rest/restaurant_list.html'
def res_list(request):
    c = request.session.get('_auth_user_id')
    res_list = Restaurant.objects.filter(user_id=c).values('id', 'name','address','date').distinct()
    for re in res_list:
        print(re)
    return render(request, 'rest/res_list.html', {'res_list': res_list})

def rest_review(request,pkk):
    restaurant = get_object_or_404(Restaurant, pk=pkk)
    print(restaurant)
    review = RestaurantReview(
        rating=request.POST['rating'],
        comment=request.POST['comment'],
        user=request.user,
        restaurant=restaurant)
    review.save()
    return HttpResponseRedirect(reverse('rest:create_review', args=[pkk]))
class RestaurantDetail(DetailView):
    model = Restaurant
    template_name = 'rest/restaurant_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RestaurantDetail, self).get_context_data(**kwargs)
        context['RATING_CHOICES'] = RestaurantReview.RATING_CHOICES
        return context


class RestaurantCreate(CreateView):
    model = Restaurant
    template_name = 'rest/form.html'
    form_class = RestaurantForm

    # Associate form.instance.user with self.request.user
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(RestaurantCreate, self).form_valid(form)


class RestaurantEdit(UpdateView):
    model = Restaurant
    template_name = 'rest/form.html'
    form_class = RestaurantForm

# 其余视图见第一部分教程
class DishDetail(DetailView):
    model = Dish
    template_name = 'rest/dish_detail.html'
class DishCreate(CreateView):
    model = Dish
    template_name = 'rest/form.html'
    form_class = DishForm
    # Associate form.instance.user with self.request.user and get pk value.
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.restaurant = Restaurant.objects.get(id=self.kwargs['pk'])
        return super(DishCreate, self).form_valid(form)
class DishEdit(UpdateView):
    model = Dish
    template_name = 'rest/form.html'
    form_class = DishForm
def review_create(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    print(restaurant)
    print(pk)
    review = DeliverReview(
        rating=request.POST['rating'],
        comment=request.POST['comment'],
        user=request.user,
        restaurant=restaurant)
    review.save()
    return HttpResponseRedirect(reverse('rest:deliver_detail', args=[pk]))
def deliver_review(request):
    #restaurant = get_object_or_404(Restaurant, pk=pko)
    #print(restaurant)
   #print(pko)
    review = RestaurantReview(
        rating=request.POST['rating'],
        comment=request.POST['comment'],
        user=request.user)
        #restaurant=restaurant)
    review.save()
    return HttpResponseRedirect(reverse('rest:deliver_review'))


