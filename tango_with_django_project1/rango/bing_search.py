import json
import urllib, urllib2

BING_API_KEY='+AqsZIGqNBDfbJlqUgynic/JkuPZ2GxVd0ejTnjMiQI'

def run_query(search_terms):
	#specify the base
	root_url = 'https://api.datamarket.azure.com/Bing/Search/'
	source='Web'

	#Specify how many results we wish to be returned per page
	#offset specifies where in the results list to start from
	#with results_per_page = 10 and offset = 11, this would start from page 2
	results_per_page = 10
	offset =0

	#wrap quotes around our query terms as required by the Bing api
	#the query we will then use is stored within variable query
	query = "'{0}'".format(search_terms)
	query=urllib.quote(query)

	#construct the latter part of our requests URL
	#Sets the format of the response to JSON and sets other properties
	search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
		root_url,
		source,
		results_per_page,
		offset,
		query)
	#setup authentication with the Bing servers
	#the username must be a blank string 

	username = ''

	#create a password manager which handles authentication for us
	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, search_url, username, BING_API_KEY)

	#create our results list which we will then populate
	results = []

	try:
		#prepare for connecting to Bing's servers
		handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)

		#connect to the server(Bing API) and read the response generated
		response = urllib2.urlopen(search_url).read()

		#convert the string response to a Python dictionary object using the json package
		json_response = json.loads(response)

		#Loop through each page returned, populating out results list
		#for each result we take the title,url,summary and add to the results dictionary
		for result in json_response['d']['results']:
			results.append({
				'title': result['Title'],
				'link': result['Url'],
				'summary': result['Description']})

	#catch a URLError exception (something went wrong when connecting)
	except urllib2.URLError as e:
		print "Error when querying the Bing API: ", e

	#return the list of results to the calling function
	return results