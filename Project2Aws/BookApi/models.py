from django.db import models
# Create your models here.


class Book(models.Model):
    name = models.CharField(max_length=250)
    isbn = models.CharField(max_length=13)
    publisher = models.CharField(max_length=200)
    publisher_year = models.CharField(max_length=4)
    date_created = models.DateField(auto_now=True)
    date_modified = models.DateField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='books', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


