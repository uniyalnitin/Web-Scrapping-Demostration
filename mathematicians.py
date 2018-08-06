from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):

	try:
		with closing(get(url,stream =True)) as resp:
			if is_good_response(resp):
				return resp.content

			else:
				return None


	except RequestException as e:
		log_error('Error during requests to {0} : {1}'.format(url,str(e)))
		return None

def is_good_response(resp):
	'''
	Returns True if response seems to be HTML, False otherwise.
	'''
	content_type = resp.headers['Content-Type'].lower()
	return (resp.status_code == 200 and content_type is not None and content_type.find('html') > -1)

def log_error(e):
	print(e)

def get_names():
	url = 'http://www.fabpedigree.com/james/mathmen.htm'
	response = simple_get(url)

	if response is not None:
		html = BeautifulSoup(response, 'html.parser')
		names = set()
		for li in html.select('li'):
			for name in li.text.split('\n'):
				if len(name)>0:
					names.add(name.strip())
		return list(names)
	return Exception('Error retrieving contents at {}'.format(url))

def get_hits_on_name(name):
	url_root = 'https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/{}'.format(name)
	response = simple_get(url_root)

	if response is not None:
		html = BeautifulSoup(response,'html.parser')

		hit_link = [a for a in html.select('a') if a['href'].find('latest-60') > -1]

		if len(hit_link) > 0:
			#strip commas
			link_text = hit_link[0].text.replace(',','')
			try:
				return int(link_text)
			except:
				log_error(" could'nt parse {} as an int".format(link_text))
	log_error('No pageviews found for {}'.format(name))
	return None


if __name__ == '__main__':
	print('Getting the list of names.....')
	names = get_names()
	print('....done\n')

	results =[]

	print('Getting stats for each name ....')

	for name in names:
		try:
			hits = get_hits_on_name(name)
			if hits is None:
				hits = -1
			results.append((hits,name))
		except Exception as e:
			print(e)
			results.append((-1, name))
			log_error('error encountered while processing {},skipping'.format(name))

	print('....done\n')

	results.sort()
	results.reverse()

	if len(results)>5:
		top_marks = results[:5]
	else:
		top_marks = results

	print('\nThe most popular mathematicians of are:\n')
	for (mark, mathematician) in top_marks:
		print('{} with {} pageviews'.format(mathematician, mark))

	no_results = len([res for res in results if res[0] == -1])
	print('\nBut we did not find results for {} mathematicians on the list'.format(no_results))
