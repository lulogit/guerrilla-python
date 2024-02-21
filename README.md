# Python in your browser

---
### TL;DR: 
- python with deps in 5 seconds https://pyodide.org/en/stable/console.html
  - try importing pandas out of the box ;)
- lib making this possible https://pyodide.org/en/stable/
https://md2pdf.netlify.com/
- Bookmark to inject python in a web page
  - just save it in the bookmark bar, and click it to inject python in the page
```js
javascript:(function(){var script = document.createElement('script');script.src = "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js";document.getElementsByTagName('head')[0].appendChild(script);setTimeout(() => loadPyodide({packages: ['requests', 'lxml', 'html5lib', 'beautifulsoup4', 'pandas']}).then((pyodide) => {window.pyodide = pyodide; console.log("window.pyodide injected !");}), 1000);})()
``` 

---

## What is pyodide
- The python interpreter, and the most popular packages (pandas, numpy, ...) gets compiled to web assembly, to be run in your browser.
- You can install any wheel package (and most are pre-distributed)
```js
loadPyodide({packages: ['requests', 'lxml', 'html5lib', 'beautifulsoup4', 'pandas']})
// OR
pyodide.loadPackage('pandas')
```
See https://pyodide.org/en/stable/usage/loading-packages.html
- You can run the python code with
```js
pyodide.runPython(`
  import sys
  sys.version
`);
```
See https://pyodide.org/en/stable/usage/quickstart.html

## Loading pyodide in a web page
- You just need to load https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js as a script in the page, then call `loadPyodide()` from the Browser's dev tools (console).
- This can be automated with a browser bookmark
   - Save the bookmark with any name, the url should be 
   ```js
   javascript:(function(){var script = document.createElement('script');script.src = "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js";document.getElementsByTagName('head')[0].appendChild(script);setTimeout(() => loadPyodide({packages: ['requests', 'lxml', 'html5lib', 'beautifulsoup4', 'pandas']}).then((pyodide) => {window.pyodide = pyodide; console.log("window.pyodide injected !");}), 1000);})()
   ```
   - The code basically:
   ```js
   javascript: // execute js code in the current page
   (function(){ // execute all of the following
     var script = document.createElement('script'); // create a <script> element 
     script.src = "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js"; // set the source to the lib's CDN url
     document.getElementsByTagName('head')[0].appendChild(script); // append the script to the HEAD element => run the script
     
     // The above could take some time, let's wait a second before loading the lib
     setTimeout(() => 
       loadPyodide({ // load the python env
         packages: ['requests', 'lxml', 'html5lib', 'beautifulsoup4', 'pandas'] // preinstall the following packages. Note: pandas depends on lxml and bs4
       })
       .then( // promise: executed the above when loaded
         (pyodide) => {
           window.pyodide = pyodide; // save the env as a window property
           console.log("window.pyodide injected !"); // notify the console python is ready !
         }
       ), 1000); // wait 1 second
     })()
   ```
   - You can change the list of packages to install, or install them later with `pyodide.loadPackage('<package name>')`
- Now you can just run python code in the console :)
```js
pyodide.runPython(`# note: js uses backticks for multiline strings
import sys
print(f"Hello world ! {sys.version}")
`)
// Hello world ! 3.11.3 (main, Jan 18 2024, 19:07:12) [Clang 18.0.0 (https://github.com/llvm/llvm-project 75501f53624de92aafce2f1da698
```
- You can import any package that you install from the bookmar, or using `pyodid.loadPackage('<pkg>')` (from the js console)
  - Pandas
```js
pyodide.runPython(`# note: js uses backticks for multiline strings
import pandas as pd
print(f"Pandas version: {pd.__version__}")
`)
// Pandas version: 1.5.3
```

## Scraping with pyodide
```diff
+ Self contained: no need to install anything outside the browser
+ No need to setup auth for APIs / go crazy interpreting JS: What you see, you can get
+ Ideal for single page apps
- Cross page scraping requires to reload the lib
```

### Python <=> JS
- `pyodide` exposes a `js` module in python. 
```python
import js
```
- This is a proxy for the `window` object in the js console.
```python
# alert a popup
js.alert('Hellow world!')
```
- You can get the code, and reuse existing parsing scripts (`lxml`, `beautifulsoup4`, ...)
```python
# get the page HTML code
html_code = js.document.body.innerHTML
```
- Or just use the poweful CSS selector of HTML
```python
def links(selector='a'):
	'''
    Get all links (<a> tag) in a page
    '''
    return [
        a.href # link url
        for a in js.document.querySelectorAll(selector)
    ]
```
- Note: you can use `Right click (on an element) > Inspect > Copy > Selector` to get the selector for that element
  - Tip: that selector will be very specific, you can remove strict specifiers (e.g: `:nth-child(X)`) and leave just some relationshipt to parent element ids (`#id`) or classes (`.class`)
### Example: books.toscrape.com
- Note: this website allows (and encourage) scraping, make sure this is the case for other use cases
#### Setup
1. Open http://books.toscrape.com/
2. Click the `Inject Python` bookmark from the bookmark bar (see above section)
3. Open the `Dev tools > Console` tab, wait for the message `window.pyodide injected !` message to appear
3. All the below python code snippet will be run with 
```js
pyodide.runPython(`
# <some code here>
`)
```
#### Get all books links from the index page
1. Inspect the link of a book, and get the selector
```
#default > div > div > div > div > section > div:nth-child(2) > ol > li:nth-child(1) > article > h3 > a
```
2. Relax the selector to match all links, and not just that specific one
  - We just care about being inside an article's header 3
```python
book_urls = links(selector='article > h3 > a')
print(book_urls[:3]) # prints just the first 3 links
```
>['http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', 'http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html', 'http://books.toscrape.com/catalogue/soumission_998/index.html']
#### Open book detail page
1. You can iterate over the `book_urls`, and open each of them in a new tab
```python
def open_new_tab(url):
    js.open(url, "_blank") # "_blank" is the target for a new tab

for book in book_urls:
    open_new_tab(book)
```
- Note: ensure to disable the popup blocker (address bar, on the right), or the browser would block the pages after the first one to open
#### Navigate the pagination
The site splits the results in pages of 20 books each. You can move to the next page by clicking on the `next` button
1. Inspect and get the selector for the next button
```
#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a
```
2. Relax the selector, we just care about the links inside a `.next` class
3. Emulate the click on the element
```python
def go_next():
    next_button = js.document.querySelector('.next > a')
    next_button.click()

go_next()
```
- Note: this will refresh the page, and unload the `pyodide` object, that needs to be reloaded with the bookmark
  - Tip: You could automate this using a chrome extension
#### Parse tables to a pandas df
The book detail pages, contain a table http://books.toscrape.com/catalogue/foundation-foundation-publication-order-1_375/index.html

```python
def load_table(html):
	'''
    load a html table from a html code
    
    outputs a pandas dataframe
    '''
    tables = pd.read_html(html) # parses all tables
    return tables[0] # get the first one

df = load_table(js.document.body.innerHTML)

# now we can use all our pandas kung-fu to preprocess the data
df = df.transpose() # swap rows and columns
df.columns = df.iloc[0] # the first row is now the columns list
df = df[1:] # ignore the header

'''
   0  1
0 C1 V1    =>    C1 C2 C3
1 C2 V2        0 V1 V2 V3   
2 C3 V3
'''

print(df)
```
Outputs:
```
 0               UPC Product Type  ...            Availability Number of reviews
 1  3fc124f59f3068e4        Books  ...  In stock (5 available)                 0
 
[1 rows x 7 columns]
```

## To dive deep
- You can run js from python, and python from js, via a FFI (Foreign Function Interface) https://pyodide.org/en/stable/usage/type-conversions.html
- You can package a whole python code as a module, and just run it from the browser. This is good for larger projects https://pyodide.org/en/stable/usage/loading-custom-python-code.html
- You can write / read files from disk https://pyodide.org/en/stable/usage/file-system.html
  - pyodide has a internal File System, that can be synced with the computer's one, using the browser's FS APIs

## Links
- https://pyodide.org/en/stable/ the main project
- https://pyodide.org/en/stable/console.html repl with all the main packages available in seconds
- http://books.toscrape.com/ scraping playground site
- https://pyodide.org/en/stable/project/related-projects.html Cool projects based on pyodide
   - Notable mention: https://github.com/jupyterlite/jupyterlite Jupyter notebooks without any dependency outside the browser
   - Demo https://jupyterlite.readthedocs.io/en/stable/_static/lab/index.html
