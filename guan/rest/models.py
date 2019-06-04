from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.urls import reverse


class Restaurant(models.Model):
    #DEST_CHOICES = (('北京', 'one'), ('广州', 'two'), ('武汉', 'three'), ('南京', 'four'), ('长沙', 'five'))
    #rating = models.PositiveSmallIntegerField('Rating (stars)', blank=False, default='北京', choices=DEST_CHOICES)
    name = models.TextField()
    address = models.TextField(blank=True, default='')
    telephone = models.TextField(blank=True, default='')
    #is_arrive = models.BooleanField(default=False)
    #url = models.URLField(blank=True, null=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('rest:restaurant_detail', args=[str(self.id)])


class Dish(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True, default='')
    price = models.DecimalField('USD amount', max_digits=8, decimal_places=2, blank=True, null=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    image = models.ImageField(upload_to="rest", blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, null=True, related_name='dishes', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('rest:dish_detail', args=[str(self.restaurant.id), str(self.id)])


# This Abstract Review can be used to create RestaurantReview and DishReview
class Review(models.Model):
    RATING_CHOICES = ((1, 'one'), (2, 'two'), (3, 'three'), (4, 'four'), (5, 'five'))
    rating = models.PositiveSmallIntegerField('Rating (stars)', blank=False, default=3, choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)

    class Meta:
        abstract = True
class Deliver(models.Model):
    DEST_CHOICES = ((1, 'one'), (2, 'two'), (3, 'three'), (4, 'four'), (5, 'five'))
    rating = models.PositiveSmallIntegerField('Rating (stars)', blank=False, default=1, choices=DEST_CHOICES)
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(Restaurant, default=1, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)

    class Meta:
        abstract = True
class DeliverReview(Deliver):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="deliver_reviews")

    def __str__(self):
        return "{} review".format(self.restaurant.name)
class RestaurantReview(Review):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reviews")

    def __str__(self):
        return "{} review".format(self.restaurant.name)

