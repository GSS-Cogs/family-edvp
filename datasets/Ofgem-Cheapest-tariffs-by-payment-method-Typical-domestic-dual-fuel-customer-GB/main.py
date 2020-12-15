#!/usr/bin/env python
# coding: utf-8
# %%

# %%


import json

import pandas as pd
import requests
from gssutils import *

from urllib.parse import urljoin

scraper = Scraper(seed="info.json")
# cubes = Cubes("info.json", base_url="http://gss-data.org.uk/data/gss_data/edvp/cheapest-tariffs-by-payment-method-typical-domestic-dual-fuel-customer-gb/")
cubes = Cubes()
title = "Cheapest tariffs by payment method: Typical domestic dual fuel customer (GB)"
scraper.distributions[0].title = title
scraper


# %%


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
         return ''


# %%


trace = TransformTrace()
link = scraper.distributions[0].downloadURL
link = link.split('?')[0] # Remove ?fake=.csv which is added dataURL since scraper only supports links ending with a proper file extension
columns = ['Period', 'Payment Method', 'Value']
publisher = "The Office of Gas and Electricity Markets"
trace.start(publisher, title, columns, link)

df = scraper.distributions[0].as_pandas()
dimensions = list(df.columns) # list of columns
dimensions = [col for col in dimensions if 'date' not in col.lower()] # list of the dimensions
trace.Period("Values taken from 'Date' column")
# Not sure what to call this column, Dimension_1
trace.Payment_Method("Values one of {}", dimensions)
trace.Value("Values taken from {} columns", dimensions)

df_new_shape = pd.melt(df, id_vars=["Date"])
df_final = df_new_shape.rename(columns={"Date": "Period", "variable": "Payment Method", "value": "Value"})
df_final["Period"] = df_final["Period"].apply(gregorian_day)
trace.Period("Formatted time to 'gregorian-day/dd/mm/yyyy'")
df_final["Value"] = df_final["Value"].apply(sanitize_values)
trace.Value("Removed commas and whitespaces from Values")

#trace.store(title, df_final)
#cubes.add_cube(scraper, df, title)
#trace.render("spec_v1.html")

df_final['Payment Method'] = df_final['Payment Method'].apply(pathify)

csvName = "{}.csv".format(pathify(title))
df_final.to_csv("./out/{}".format(csvName), index=False)

out = Path('out')
out.mkdir(exist_ok=True)

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

scraper.dataset.family = 'edvp'
dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower()
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(dataset_path)

csvw_transform = CSVWMapping()
csvw_transform.set_csv(out / csvName)
csvw_transform.set_mapping(json.load(open('info.json')))
csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
csvw_transform.write(out / f'{csvName}-metadata.json')

with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

df_final


# %%





# %%

# %%
