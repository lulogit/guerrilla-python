import js

def links(selector='a'):
    '''
    Get all links (<a> tag) in a page
    '''
    return [
        a.href # link url
        for a in js.document.querySelectorAll(selector)
    ]

book_urls = links(selector='article > h3 > a')

def open_new_tab(url):
    js.open(url, "_blank")

for book in book_urls:
    open_new_tab(book)