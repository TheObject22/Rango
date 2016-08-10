from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from rango.models import UserProfile
from django.contrib.auth.models import User
from rango.bing_search import run_query
from django.shortcuts import redirect
from django.template import RequestContext
from django.shortcuts import render_to_response
def encode_url(str):
    return str.replace(' ', '_')

def decode_url(str):
    return str.replace('_', ' ')
def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if (len(cat_list) > max_results):
            cat_list = cat_list[:max_results]

    for cat in cat_list:
        cat.url = encode_url(cat.name)
    
    return cat_list


def index(request):
	# Query the database for a list of all catagories currently stored
	# order the categories by no. of likes in descending order
	# retrieve the top 5 only- or all if less than 5
	# place the list in our context_dict dictionary which will be passed to the template engine
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'categories': category_list}

	# render the response and send it back
	page_list = Page.objects.order_by('-views')[:5]
	context_dict['pages'] = page_list


	##Get the number of visits to the site
	##COOKIES.get() obtains the visits cookie
	#if the cookie exists, the value returned is cast to an int
	##else, we default to 0 
	visits = request.session.get('visits')
	if not visits:
		visits = 1
	reset_last_visit_time = False

	last_visit = request.session.get('last_visit')
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now()-last_visit_time).seconds>0:
			visits = visits + 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True

	if reset_last_visit_time:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits
	context_dict['visits'] = visits

	response = render(request, 'rango/index.html', context_dict)
	return response

	
    
def about(request):
	context_dict = {}
	about_visits = request.session.get('about_visits')
	if not about_visits:
		about_visits = 1
	reset_last_visit_time = False

	about_last_visit = request.session.get('about_last_visit')
	if about_last_visit:
		last_visit_time = datetime.strptime(about_last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now() - last_visit_time).seconds>5:
			about_visits = about_visits + 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True

	if reset_last_visit_time:
		request.session['about_last_visit'] = str(datetime.now())
		request.session['about_visits'] = about_visits
	context_dict['about_visits'] = about_visits
	response = render(request, 'rango/about.html', context_dict)
	return response
	

	##return render(request, 'rango/about.html')

def category(request, category_name_slug):

	context_dict =  {}


	try:

		#can we find a category name slug with the given name?
		# if we can't, the .get() method raises a doesnotexist exception
		# so the .get() method returns one model instance or raises an exception
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name
		context_dict['category_name_slug'] = category_name_slug
		#retriveve all of the associated pages.
		#note that filter returns >=1 model instance

		pages = Page.objects.filter(category=category)

		#adds our results list to the template context under name pages
		context_dict['pages'] = pages
		#we also add the category object from the database to the conext dictionary
		# we use this in the template to verify if the category exists
		context_dict['category']=category
	except Category.DoesNotExist:
		pass

	if request.method == 'POST':
		query = request.POST.get('query')
		if query:
			query = query.strip()
			result_list = run_query(query)
			context_dict['result_list'] = result_list


		#render the response and return it to the client
	return render(request, 'rango/category.html', context_dict)


def add_category(request):
	#is it a HTTP GET or POST. Show form if GET or process form data if POST
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		#Have we been provided with a valie form?
		if form.is_valid():
			#save the new category to the database.
			form.save(commit=True)

			#now call the index() view
			#the user will be shown to the homepage
			return index(request)
		else:
			#the form contained errors
			print form.errors
	else:
		#if the request was not a POST, display the form to enter details
		form = CategoryForm()
	#render the form with error messages(if any)
	return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
	try:
		cat = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
				cat=None
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				return category(request, category_name_slug)
		else:
			print form.errors	
	else:
		form = PageForm()

	context_dict = {'form': form, 'category': cat, 'category_name_slug': category_name_slug}

	return render(request, 'rango/add_page.html', context_dict)	

def register(request):
	
	registered = False

	# if it's a HTTP POST, we're interested in processing a form
	if request.method == 'POST':
		#Grab info from the raw form
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			#save the user's form data to the database
			user = user_form.save()

			#Now let's hash the password
			user.set_password(user.password)
			user.save()


			#since we set the user attributes ourselves, commit=False
			profile = profile_form.save(commit=False)
			profile.user=user

			#did the user provide a profile image
			# if so, we need to get it from the input form and put it in the UserProfile model
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			#save the userprofile model instance	
			profile.save()

			registered = True
		#invalid form	
		else:
			print user_form.errors, profile_form.errors
	#not an HTTP POST, so we render our form using 2 ModelForm instances
	#these forms will be blank, ready for user input
	else:
		user_form=UserForm()
		profile_form=UserProfileForm()
	return render(request,
			'rango/register.html',
			{'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):

	if request.method == 'POST':
		#gather the username and password provided by the user
		username=request.POST.get('username')
		password=request.POST.get('password')

		#see if the combination if is_valid
		user = authenticate(username=username, password=password)

		#if we get a user object the details are correct
		if user:
			#is the account active?
			if user.is_active:
				#now we can log the user in
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse('Your account is disabled')
		else:
			print "invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("invalid login details supplied.")
	else:
		return render(request, 'rango/login.html', {})

#this is a django decorator which checks to see if the user is logged in
@login_required
def restricted(request):
	return HttpResponse("you must be logged out to see this")

@login_required
def user_logout(request):
	logout(request)

	return HttpResponseRedirect('/rango/')

def search(request):

	result_list=[]

	if request.method=='POST':
		query = request.POST['query'].strip()

		if query:
			#run our bing function to get the results list!
			result_list = run_query(query)

	return render(request, 'rango/search.html',{'result_list':result_list})

def track_url(request):
	page_id = None
	url = '/rango/'
	if request.method=="GET":
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views+1
				page.save()
				url = page.url
			except:
				pass


	return redirect(url)

@login_required
def profile(request):
	context = RequestContext(request)
	cat_list = get_category_list()
	context_dict = {'cat_list': cat_list}
	u = User.objects.get(username=request.user)

	try:
		up = UserProfile.objects.get(user=u)
	except:
		up = None

	context_dict['user'] = u
	context_dict['UserProfile'] = up
	return render_to_response('rango/profile.html', context_dict, context)
	
def register_profile(request):
    registered = False
    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)
        if profile_form.is_valid():
            # as the same time..??
            user = User.objects.order_by('-pk')[0]

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True

            return HttpResponseRedirect(reverse('rango:index'))
        else:
            print profile_form.errors
    else:
        profile_form = UserProfileForm()

    return render(request, 'rango/profile_registration.html',
        {'profile_form': profile_form,
         'registered': registered})