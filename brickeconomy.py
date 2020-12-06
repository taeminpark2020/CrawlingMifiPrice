import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import requests
from bs4 import BeautifulSoup
from currency_converter import CurrencyConverter
import math
import random


###CAUTION###
# 1. you need firebase api-json file
# 2. you need your firebase database url
# 3. This Code doesn't work ==> it is only for reference how to crawl. Please reform code to your style
#############

#Firebase database Autification & Initialize
cred = credentials.Certificate('your firebase json file')
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'your firebase database URL'

})

class Currency_Converter():
    def __init__(self,url):
        self.data= requests.get(url).json()
        self.currencies = self.data['rates']
    def convert(self, from_currency, to_currency, amount):
        initial_amount = amount
        # first convert it into USD if it is not in USD.
        # because our base currency is USD
        if from_currency != 'USD':
            amount = amount / self.currencies[from_currency]
            # limiting the precision to 4 decimal places
        amount = round(amount * self.currencies[to_currency], 4)
        return amount


currency_url = 'https://api.exchangerate-api.com/v4/latest/USD'
converter = Currency_Converter(currency_url)
first_dir = db.reference('/mifi_serial')
for i in first_dir.get():
    second_dir = db.reference('/mifi_serial'+'/'+i)
    for j in second_dir.get():
        mifi_serial_num = db.reference('/mifi_serial' + '/' + i).child(j).get()
        save_dir = db.reference('/mifi_value/' + mifi_serial_num)
        if(str(save_dir.child("USD").get())!="None"):
            print(mifi_serial_num+" Already Done!")
        else:

            URL = 'crawling minifigure site url/'+mifi_serial_num#It may be different
            response = requests.get(URL)
            soup = BeautifulSoup(response.text, 'html.parser')
            tmptext=str(soup.select('.mt-20.text-muted'))
            try:
                refine_value=tmptext.split('around')
                refine_value=refine_value[1].split('.')
                refine_value=refine_value[0].split('₩')
                final_refine_value=int(refine_value[1].replace(',',''))
                #print(final_refine_value)
                convert_to_usd=round(converter.convert('KRW','USD',final_refine_value),2)
                save_dir = db.reference('/mifi_value/'+mifi_serial_num)
                save_dir.update({"KRW": final_refine_value})
                save_dir.update({"USD": convert_to_usd})
                print(mifi_serial_num, convert_to_usd, " done!")
                time.sleep(random.randrange(1, 10))
            except:
                print("error")

