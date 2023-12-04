import requests

URL = 'https://dirtyauditions.com/models?page=2'

response = requests.get(URL)
html = response.text
