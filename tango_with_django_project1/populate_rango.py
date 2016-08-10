import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project1.settings')

import django
django.setup()

from rango.models import Category, Page

def populate():
	python_cat = add_cat('Python',128, 64)##adds a python category
	add_page(cat=python_cat,
		title="Official Python Tutorial",
		url="http://docs.python.org/2/tutorial/")
	add_page(cat=python_cat,
		title = "How to think like a Computer Scientist",
		url="http://www.greenteapress.com/thinkpython/")
	add_page(cat=python_cat,
		title="Learn Python in 10 minutes",
		url="http://www.korokithakis.net/tutorials/python/")
	
	django_cat = add_cat("Django",64,32) ##adds a django category

	add_page(cat=django_cat,
		title="Official Django Tutorial",
		url="https://docs.djangoproject.com/en/1.5/intro/tutorial01/")
	add_page(cat=django_cat,
		title="Django Rocks",
		url="http://www.djangorocks.com/")
	add_page(cat=django_cat,
		title="How to Tango with Django",
		url="http://www.tangowithdjango.com/")
	frame_cat = add_cat("Other Frameworks",32,16)

	add_page(cat=frame_cat,
		title="Bottle",
		url="http://bottlepy.org/docs/dev/")
	add_page(cat=frame_cat,
		title="Flask",
		url="http://flask.pocoo.org")
	##Print out what we have added to the user
	for c in Category.objects.all():
		for p in Page.objects.filter(category=c):
			print "- {0} - {1}".format(str(c),str(p))

def add_page(cat, title, url, views=0):
	p = Page.objects.get_or_create(category=cat, title=title)[0] ##get_or_create checks for duplicates of the entry, if it doesn't exist it gets created
	p.url=url
	p.views=views
	p.save()
	return p

def add_cat(name, views, likes):
	c = Category.objects.get_or_create(name=name)[0] ##the [0] retrieves the object port ion of the tuple from get_or_create()
	c.views=views
	c.likes=likes
	c.save()
	return c

##Execution begins here
if __name__ == '__main__':
	print "Beginning Rango population script..."
	populate()