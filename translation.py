

import http.client, urllib.parse, uuid, json
# **********************************************
# *** Update or verify the following values. ***
# **********************************************

with open('token.txt', 'r') as myfile:
	token = myfile.read().replace('\n', '')
			
# Replace the subscriptionKey string value with your valid subscription key.
subscriptionKey = token

host = 'api.cognitive.microsofttranslator.com'
path = '/translate?api-version=3.0'

# List of supported languages
#https://docs.microsoft.com/en-us/azure/cognitive-services/translator/languages
params = "&to=en";

text = "Podemos começar?"

def translate (content):
    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    conn = http.client.HTTPSConnection(host)
    conn.request ("POST", path + params, content, headers)
    response = conn.getresponse ()
    return response.read ()


requestBody = [{
    'Text' : text,
}]

content = json.dumps(requestBody, ensure_ascii=False).encode('utf-8')

result = translate (content) #Array de bytes

result = result.decode('utf8').replace("'", '"').replace("[", "").replace("]", "") # Lista com caracteres retornados tratados
result = json.loads(result) #Json tratado
print(result['translations']['text'])


#print (result["translations"]["text"])

