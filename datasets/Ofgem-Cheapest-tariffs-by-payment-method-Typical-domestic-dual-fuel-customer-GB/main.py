# +
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


# +
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


# +
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

trace.store(title, df_final)
trace.render("spec_v1.html")

out = Path('out')
out.mkdir(exist_ok=True)

coldef = json.load(open('info.json'))
csvName = "{}.csv".format(pathify(title))
csvw_transform = CSVWMapping()
csvw_transform.set_csv(out / csvName)
csvw_transform.set_mapping(coldef)
csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
csvw_transform.write(out / f'{csvName}-metadata.json')

with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

df_final
# -


