# OTM Vega / ATM Vega is plotted for the following 2 inputs:
# 1. Moneyness of the strike
# 2. Days to expiry

import pandas as pd
import pandasql as ps
from pandasql import *
from nsepython import *
import plotly
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import glob

print("Steps to Download CSV File")
print("1. Copy & paste this link to your browser (https://drive.google.com/drive/folders/1AK93HiSWmFA_3vOfqRpVGcIsag28SW4F?usp=sharing)")
print("2. Download the CSV to your system.")
print("3. Enter the path to the downloaded CSV below.")
path = input("Enter path here: ")
close_options = pd.read_csv(path)

close_options = close_options.drop_duplicates()

days_to_expiry = list(range(1, 30))

from_expiry = '2019-02-14'
put_strike = int(input("Enter Put Strike: "))
call_strike = int(input("Enter Call Strike: "))
days_to_expiry = int(input("Enter Days To Expiry: "))

def delta_for_moneyness(put_strike, call_strike, from_expiry, days_to_expiry):
    
    nifty = nse_quote_ltp("NIFTY","latest","Fut")
    moneyness_put = np.log(nifty / put_strike)
    moneyness_call = np.log(nifty / call_strike)

    ################################################   
    
    # Put Delta | Historical
    
    put_close = close_options[
        (close_options['expiry'] >= from_expiry)
        & (close_options['moneyness_close'] >= (moneyness_put - 0.1 * moneyness_put))
        & (close_options['days_to_expiry'] == days_to_expiry)]

    temp = put_close.groupby(['expiry'], sort=False)['strike'].max()
    temp = pd.DataFrame(temp)

    put_close = put_close[['expiry', 'strike', 'implied_volatility', 'close_option', 'close_ul', 'delta']]

    put_close = temp.merge(put_close, on=['expiry', 'strike'], how='inner')
    
    # Close
    fig = px.line(put_close, x="expiry", y="delta", title='Put Delta | Close | Historical')
    fig.show()

    ################################################    

    # Call Delta | Historical
    
    call_close = close_options[
        (close_options['expiry'] >= from_expiry)
        & (close_options['moneyness_close'] < (moneyness_call + 0.1 * moneyness_call))
        & (close_options['days_to_expiry'] == days_to_expiry)]

    temp = call_close.groupby(['expiry'], sort=False)['strike'].min()
    temp = pd.DataFrame(temp)

    call_close = call_close[['expiry', 'strike', 'implied_volatility', 'close_option', 'close_ul', 'delta']]

    call_close = temp.merge(call_close, on=['expiry', 'strike'], how='inner')

    # Close
    fig = px.line(call_close, x="expiry", y="delta", title='Call Delta | Close | Historical')
    fig.show()   
    
delta_for_moneyness(put_strike, call_strike, from_expiry, days_to_expiry)