import js
import pandas as pd


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