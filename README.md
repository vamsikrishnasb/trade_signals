# trade_signals

1. Vega Ratio (OTM Vega / ATM Vega)
2. Delta for the chosen moneyness

Both these metrics could be used to check if the OTM options are "cheap" or "expensive" compared to the historical OTM option prices.


# Characteristic of these greeks which makes them eligible for such comparisons

When implied volatility is high:
1. OTM vega for both call and put decreases
2. OTM call delta increases (e.g. call delta goes from 0.1 to 0.15)
3. OTM call delta decreases (e.g. put delta goes from -0.1 to -0.15)
