#!/usr/bin/env python
# coding: utf-8

# In[65]:


import datetime
import json

import pandas as pd
import requests
from gssutils import *

from urllib.parse import urljoin

scraper = Scraper(seed="info.json")
# cubes = Cubes("info.json", base_url="http://gss-data.org.uk/data/gss_data/energy/cheapest-tariffs-by-payment-method-typical-domestic-dual-fuel-customer-gb/")
cubes = Cubes()
title = "Cheapest tariffs by payment method: Typical domestic dual fuel customer (GB)"
scraper.distributions[0].title = title
scraper


# In[66]:


def gregorian_day(date):
    time_string = str(date).replace(".0", "").strip()
    time_len = len(time_string)
    if time_len == 10:
        return 'gregorian-day/' + time_string[:10]

def sanitize_values(value):
     # removing comma and whitespace from values
     try:
         new_value = value.replace(' ', '').replace(',', '').strip()
         return new_value
     except:
         return value


# In[67]:


df = pd.read_csv('cheapest-tariffs-by-paym.csv')
scraper.distributions[0]
df


# In[68]:


dimensions = list(df.columns) # list of columns
dimensions = [col for col in dimensions if 'date' not in col.lower()] # list of the dimensions
print(dimensions)
# Not sure what to call this column, Dimension_1

df_new_shape = pd.melt(df, id_vars=["\n"])
df_final = df_new_shape.rename(columns={"\n": "Period", "variable": "Payment Method", "value": "Value"})


# In[69]:


df_final['Period'] = pd.to_datetime(pd.Series(df_final['Period']), format="%Y/%m/%d").astype(str)
#df_final["Period"] = df_final["Period"].apply(gregorian_day)
df_final['Period'] = 'day/' + df_final['Period'].astype(str)

df_final["Value"] = df_final["Value"].apply(sanitize_values)

df_final['Payment Method'] = df_final['Payment Method'].apply(pathify)


# In[70]:


scraper.dataset.comment = """
This data compares the cheapest available tariffs offered by the large legacy suppliers with the cheapest tariff
available in the market by payment method (direct debit, standard credit and prepayment). Figures are based on a
typical domestic dual fuel customer paying by direct debit.
"""

scraper.dataset.description = """
This data compares the cheapest available tariffs offered by the large legacy suppliers with the cheapest tariff
available in the market by payment method (direct debit, standard credit and prepayment). Figures are based on a
typical domestic dual fuel customer paying by direct debit.

Methodology
We calculate the bill values associated with the different tariff types using a ‘typical medium domestic consumer’.
As of April 2020, typical domestic consumption values (TDCV) for a medium consumer are 12,000kWh/year for gas and
2,900kWh/year for electricity (profile class 1). The previous typical domestic consumption values (TDCV), that came
into effect as of October 2017 were 12,000kWh/year for gas and 3,100kWh/year for electricity (profile class 1).
The chart includes collective switching tariffs from Q1 2016.

All tariffs shown in the chart are for a dual fuel customer. Dual fuel refers to a situation where a customer takes
gas and electricity from the same supplier.
Tariffs with limited availability depending on customer features (for example, tariffs which are only available to
new customers, also known as ‘acquisition’ tariffs, or tariffs restricted to certain regions) are excluded from the
calculation to make sure that all tariffs considered are generally available to all customers across GB.
Tariffs available with white label suppliers are included in the calculation of the cheapest tariff. White label
suppliers are organisations without supply licenses that partner with an active licensed supplier to offer gas and
electricity using their own brand.
"""


# In[71]:


scraper.dataset.family = 'energy'

cubes.add_cube(scraper, df_final, title)


# In[72]:


cubes.output_all()

