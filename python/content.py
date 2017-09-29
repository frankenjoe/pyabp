import wikipedia

book = 'Hakan Nesser Die Perspektive des Gartners'
lang = 'de'

wikipedia.set_lang(lang)

result = wikipedia.search(book, results=1, suggestion=False)  

if not result:
    print ('Seite nicht gefunden')
    exit()

try:    
    page = wikipedia.page(result[0])
except:
    print ('seite nicht gefunden')
    exit()

content = page.section('Handlung')
if not content:
    content = page.section('Inhalt')
if not content:
    print ('Inhalt nicht gefunden')
    exit()

print (content.encode('utf-8'))



