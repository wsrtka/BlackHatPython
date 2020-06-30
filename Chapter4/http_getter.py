import urllib.request


url = 'https://agh.iaeste.pl'

headers = {}
headers['User-Agent'] = 'Googlebot'

request = urllib.request.Request(url, headers=headers)
response = urllib.request.urlopen(request)

print(response.read())
response.close()