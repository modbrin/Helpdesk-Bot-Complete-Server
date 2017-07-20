import requests
resp1 = requests.post('http://127.0.0.1:8000/db/', data={'text': 'this is text', 'keywords': 'some keywords'}, auth=('admin', 'qwerty123'))

resp2 = requests.get('http://127.0.0.1:8000/db/') #All articles
print(resp2.json())

resp5 = requests.get('http://127.0.0.1:8000/db/1/') #Article with chosen id
print(resp5.json())

resp6 = requests.get('http://127.0.0.1:8000/db/keyword/') #Article where keywords contain keyword
print(resp6.json())

resp3 = requests.put('http://127.0.0.1:8000/db/1/', data={'text': 'changed text', 'keywords': 'new keywords'}, auth=('admin', 'qwerty123')) 

#resp4 = requests.delete('http://127.0.0.1:8000/db/1')
