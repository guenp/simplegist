import requests
import json

from config import USERNAME, API_TOKEN

from mygist import Mygist
from do import Do
from comments import Comments

BASE_URL = 'https://api.github.com'
Link_URL = 'https://gist.github.com'

class Simplegist:
	"""
	Gist Base Class

	This class is to used to instantiate the wrapper and authenticate.

	Authenticate with providing Github Username and API-Token to use
	it for all future API requests
	"""

	def __init__(self, **args):
		# Save our username and api_token (If given) for later use.
		if 'username' in args:
			self.username = args['username']
		else:
			if not USERNAME:
				raise Exception('Please provide your Github username.')
			else:
				self.username = USERNAME

		if 'api_token' in args:
			self.api_token = args['api_token']
		else:
			if not API_TOKEN:
				raise Exception('Please provide your Github API Token.')
			else:
				self.api_token = API_TOKEN


        # Set header information in every request.
		self.header = { 'X-Github-Username': self.username,
						'Content-Type': 'application/json',
						'Authorization': 'token %s' %self.api_token
					  }

	def profile(self):
		return Mygist(self)

	def search(self, user):
		return Mygist(self,user=user)

	def do(self):
		return Do(self)

	def comments(self):
		return Comments(self)

	def get_data(self, **args):
		if 'description' in args:
			self.description = args['description']
		else:
			self.description = ''

		if 'name' in args:
			self.gist_name = args['name']
		else:
			self.gist_name = ''

		if 'public' in args:
			self.public = args['public']
		else:
			self.public = 1

		if 'content' in args:
			self.content = args['content']
		else:
			raise Exception('Gist content can\'t be empty')

		data = {"description": self.description,
  				"public": self.public,
  				"files": {
    				self.gist_name: {
      				"content": self.content
    				}
  				}
  		}
		return data

	def create(self, **args):
		data = self.get_data(**args)
		url = '/gists'

		r = requests.post(
			'%s%s' % (BASE_URL, url),
			data=json.dumps(data),
			headers=self.header
		)
		if (r.status_code == 201):
			response = {
			'Gist-Link': '%s/%s/%s' %(Link_URL,self.username,r.json()['id']),
			'Clone-Link': '%s/%s.git' %(Link_URL,r.json()['id']),
			'Embed-Script': '<script src="%s/%s/%s.js"</script>' %(Link_URL,self.username,r.json()['id']),
			'id': r.json()['id'],
			'created_at': r.json()['created_at'],

			}
			return response
		raise Exception('Gist not created.')

class Multigist(Simplegist):
	"""
	Gist Base Class

	Extension to support multiple files

	Example usage:
	GHgist = Multigist(username='USERNAME', api_token='API_TOKEN')
	GHgist.create(description='_ANY_DESCRIPTION', public=0, files={'file1':'_CONTENT_GOES_HERE','file2':'_CONTENT_GOES_HERE'})

	"""

	def __init__(self, **args):
		Simplegist.__init__(self, **args)
		self.files = {}

	def add_file(self, name, content):
		self.files[name] = {
		"content": content
		}

	def get_data(self, **args):
		if 'description' in args:
			self.description = args['description']
		else:
			self.description = ''

		if 'files' in args:
			files = args['files']
			for name in files.keys():
				self.add_file(name, files[name])
		else:
			raise Exception('Gist content can\'t be empty')

		if 'public' in args:
			self.public = args['public']
		else:
			self.public = 1

		data = {"description": self.description,
				"public": self.public,
				"files": self.files
				}
		return data
