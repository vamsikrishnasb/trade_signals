# OTM Vega / ATM Vega is plotted for the following 2 inputs:
# 1. Moneyness of the strike
# 2. Days to expiry

from __future__ import print_function
import pandas as pd
import pandasql as ps
from pandasql import *
import plotly
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import glob
from nsepython import *

# For the widget


from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets

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

def vega_ratio(put_strike, call_strike, from_expiry, days_to_expiry):
    
    #NIFTY and moneyness
    
    nifty = nse_quote_ltp("NIFTY","latest","Fut")
    moneyness_put = np.log(nifty / put_strike)
    moneyness_call = np.log(nifty / call_strike)
    
    
    # Put

    put_atm = close_options[
        (close_options['option_type'] == 'PE')
        & (close_options['days_to_expiry'] == days_to_expiry)
        & (close_options['moneyness_close'] >= 0.0)
        & (close_options['expiry'] >= from_expiry)][[
        'date', 'expiry', 'strike', 'close_option', 'close_ul', 'days_to_expiry', 'implied_volatility', 
        'delta', 'gamma', 'theta', 'vega', 'vanna', 'charm', 'volga']]

    put_atm = put_atm.rename(columns={
        'date': 'date_start_atm', 'expiry': 'expiry_start_atm', 'strike': 'strike_start_atm', 
        'close_option': 'close_option_start_atm', 'close_ul': 'close_ul_start_atm', 
        'days_to_expiry': 'days_to_expiry_start_atm', 'implied_volatility': 'iv_atm', 'delta': 'delta_atm', 'gamma': 'gamma_atm', 
        'theta': 'theta_atm', 'vega': 'vega_atm', 'vanna': 'vanna_atm', 'charm': 'charm_atm', 
        'volga': 'volga_atm'})

    temp = put_atm.groupby(['expiry_start_atm'], sort=False)['days_to_expiry_start_atm'].min()
    temp = pd.DataFrame(temp)

    put_atm = temp.merge(put_atm, on=['expiry_start_atm', 'days_to_expiry_start_atm'], how='inner')

    temp = put_atm.groupby(['expiry_start_atm'], sort=False)['strike_start_atm'].max()
    temp = pd.DataFrame(temp)

    put_atm = temp.merge(put_atm, on=['expiry_start_atm', 'strike_start_atm'], how='inner')

    put_otm = close_options[
        (close_options['option_type'] == 'PE')
        & (close_options['days_to_expiry'] == days_to_expiry)
        & (close_options['moneyness_close'] >= (0.9 * moneyness_put))
        & (close_options['expiry'] >= from_expiry)][['date', 'expiry', 'strike', 'close_option', 'close_ul', 
                                                 'days_to_expiry', 'implied_volatility', 'delta', 'gamma',
                                                 'theta', 'vega', 'vanna', 'charm', 'volga']]

    put_atm_to_merge = put_atm[['expiry_start_atm', 
                                  'strike_start_atm', 
                                  'close_option_start_atm', 
                                  'iv_atm', 
                                  'vega_atm']]

    put_otm = put_otm.rename(columns={
        'date': 'date_start_otm', 'expiry': 'expiry_start_otm', 'strike': 'strike_start_otm', 
        'close_option': 'close_option_start_otm', 'close_ul': 'close_ul_start_otm', 
        'days_to_expiry': 'days_to_expiry_start_otm', 'implied_volatility': 'iv_otm', 'delta': 'delta_otm',
        'gamma': 'gamma_otm', 'theta': 'theta_otm', 'vega': 'vega_otm', 'vanna': 'vanna_otm',
        'charm': 'charm_otm', 'volga': 'volga_otm'})

    put_atm_to_merge = put_atm_to_merge.rename(columns={
        'expiry_start_atm': 'expiry_start_otm'})

    temp = put_otm.groupby(['expiry_start_otm'], sort=False)['days_to_expiry_start_otm'].min()
    temp = pd.DataFrame(temp)
    temp

    put_otm = temp.merge(put_otm, on=['expiry_start_otm', 'days_to_expiry_start_otm'], how='inner')

    temp = put_otm.groupby(['expiry_start_otm'], sort=False)['strike_start_otm'].max()
    temp = pd.DataFrame(temp)

    put_otm = temp.merge(put_otm, on=['expiry_start_otm', 'strike_start_otm'], how='inner')

    # put_otm['date_start_otm'] = pd.to_datetime(put_otm['date_start_otm'])
    put_otm['expiry_start_otm'] = pd.to_datetime(put_otm['expiry_start_otm'])
    put_atm_to_merge['expiry_start_otm'] = pd.to_datetime(put_atm_to_merge['expiry_start_otm'])

    put_otm = put_otm.merge(put_atm_to_merge, on=['expiry_start_otm'], how='inner')

    put_otm['vega_ratio_otm_atm'] = 1.00 * (put_otm['vega_otm'] / put_otm['vega_atm'])
    
    
    # Call
    
    call_atm = close_options[
        (close_options['option_type'] == 'CE')
        & (close_options['days_to_expiry'] == days_to_expiry)
        & (close_options['moneyness_close'] <= -0.0)
        & (close_options['expiry'] >= from_expiry)][[
        'date', 'expiry', 'strike', 'close_option', 'close_ul', 'days_to_expiry', 'implied_volatility', 
        'delta', 'gamma', 'theta', 'vega', 'vanna', 'charm', 'volga']]

    call_atm = call_atm.rename(columns={
        'date': 'date_start_atm', 'expiry': 'expiry_start_atm', 'strike': 'strike_start_atm', 
        'close_option': 'close_option_start_atm', 'close_ul': 'close_ul_start_atm', 
        'days_to_expiry': 'days_to_expiry_start_atm', 'implied_volatility': 'iv_atm', 'delta': 'delta_atm', 'gamma': 'gamma_atm', 
        'theta': 'theta_atm', 'vega': 'vega_atm', 'vanna': 'vanna_atm', 'charm': 'charm_atm', 
        'volga': 'volga_atm'})

    temp = call_atm.groupby(['expiry_start_atm'], sort=False)['days_to_expiry_start_atm'].min()
    temp = pd.DataFrame(temp)

    call_atm = temp.merge(call_atm, on=['expiry_start_atm', 'days_to_expiry_start_atm'], how='inner')

    temp = call_atm.groupby(['expiry_start_atm'], sort=False)['strike_start_atm'].min()
    temp = pd.DataFrame(temp)

    call_atm = temp.merge(call_atm, on=['expiry_start_atm', 'strike_start_atm'], how='inner')


    call_otm = close_options[
        (close_options['option_type'] == 'CE')
        & (close_options['days_to_expiry'] == days_to_expiry)
        & (close_options['moneyness_close'] <= (0.9 * moneyness_call))
        & (close_options['expiry'] >= from_expiry)][['date', 'expiry', 'strike', 'close_option', 'close_ul', 
                                                 'days_to_expiry', 'implied_volatility', 'delta', 'gamma',
                                                 'theta', 'vega', 'vanna', 'charm', 'volga']]

    call_atm_to_merge = call_atm[['expiry_start_atm', 
                                  'strike_start_atm', 
                                  'close_option_start_atm', 
                                  'iv_atm', 
                                  'vega_atm']]

    call_otm = call_otm.rename(columns={
        'date': 'date_start_otm', 'expiry': 'expiry_start_otm', 'strike': 'strike_start_otm', 
        'close_option': 'close_option_start_otm', 'close_ul': 'close_ul_start_otm', 
        'days_to_expiry': 'days_to_expiry_start_otm', 'implied_volatility': 'iv_otm', 'delta': 'delta_otm',
        'gamma': 'gamma_otm', 'theta': 'theta_otm', 'vega': 'vega_otm', 'vanna': 'vanna_otm',
        'charm': 'charm_otm', 'volga': 'volga_otm'})

    call_atm_to_merge = call_atm_to_merge.rename(columns={
        'expiry_start_atm': 'expiry_start_otm'})

    temp = call_otm.groupby(['expiry_start_otm'], sort=False)['days_to_expiry_start_otm'].min()
    temp = pd.DataFrame(temp)
    temp

    call_otm = temp.merge(call_otm, on=['expiry_start_otm', 'days_to_expiry_start_otm'], how='inner')

    temp = call_otm.groupby(['expiry_start_otm'], sort=False)['strike_start_otm'].min()
    temp = pd.DataFrame(temp)

    call_otm = temp.merge(call_otm, on=['expiry_start_otm', 'strike_start_otm'], how='inner')

    call_otm['expiry_start_otm'] = pd.to_datetime(call_otm['expiry_start_otm'])
    call_atm_to_merge['expiry_start_otm'] = pd.to_datetime(call_atm_to_merge['expiry_start_otm'])

    call_otm = call_otm.merge(call_atm_to_merge, on=['expiry_start_otm'], how='inner')

    call_otm['vega_ratio_otm_atm'] = 1.00 * (call_otm['vega_otm'] / call_otm['vega_atm'])
    
    # Plot
    
    fig = px.line(put_otm, x="expiry_start_otm", y='vega_ratio_otm_atm', title='Chart')
    fig.show()
    
    fig = px.line(call_otm, x="expiry_start_otm", y='vega_ratio_otm_atm', title='Chart')
    fig.show()
    
vega_ratio(put_strike, call_strike, from_expiry, days_to_expiry)