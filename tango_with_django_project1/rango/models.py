from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

class Category(models.Model):
	name = models.CharField(max_length = 128, unique=True) ##unique=true makes it so every category name is unique(different)
	views = models.IntegerField(default=0)
	likes=models.IntegerField(default=0)
	slug = models.SlugField()

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Category, self).save(*args, **kwargs)

	def __unicode__(self): ##provides a representation of a model instance
		return self.name

class Page(models.Model):
	category = models.ForeignKey(Category)##ForeignKey is a field which lets us create a one-to many-relationship
	title = models.CharField(max_length=128) ##charfield, a field for storing char data. max_length is the length of the chars
	url = models.URLField() ##urlField stores resource URLS, can specify max length if you wish
	views = models.IntegerField(default=0) ##stores ints


	def __unicode__(self):
		return self.title
class UserProfile(models.Model):
	#Links UserProfile to User model
	user = models.OneToOneField(User)

	#additional attributes which we are adding
	#blank=True allows both fields to be blank if necessary
	website = models.URLField(blank=True)
	#upload_to specifies the directory where images will be saved /media/profile_images/
	picture = models.ImageField(upload_to='profile_images', blank=True)

	def __unicode__(self):
		return self.user.username
