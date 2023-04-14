from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/exchange-rate-history/usd-idr')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={'class':'history-rates-data'})
if table:
    print(table.prettify()[1:500])
else:
    print("Could not find element")
    
row = table.find_all('a', attrs={'class':'w'})
row_length = len(row)

temp = [] #init

for i in range(0, row_length):
    
    #get Period
    period = table.find_all('a', attrs={'class':'n'})[i].text
    
    #get inflation yoy
    price = table.find_all('span', attrs={'class':'w'})[i].text
    price = price.strip() #to remove excess white space
    
    temp.append((period, price)) 
    

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('period','price'))

#insert data wrangling here

df['price'] = df['price'].str.replace('$1 = Rp', '', regex = False).str.replace(',', '.').astype('float64')
df['period'] = df['period'].astype('datetime64')
df = df.set_index('period')
df.dtypes
df.head()

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["price"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)