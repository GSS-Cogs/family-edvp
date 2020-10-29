# +
import pandas as pd 
import requests
from gssutils import * 

scraper = Scraper(seed="info.json")
cubes = Cubes("info.json")
title = "Cheapest tariffs by payment method: Typical domestic dual fuel customer (GB)"
scraper.distributions[0].title = title
scraper


# -

def gregorian_day(date):
    time_string = str(date).replace(".0", "").strip()
    time_len = len(time_string)
    if time_len == 10:
        return 'gregorian-day/' + time_string[:10]


df = scraper.distributions[0].as_pandas()#(sheet_name=title)
cols = list(df.columns)
df.columns = cols
df_new_shape = pd.melt(df, id_vars=["Date"])
df_final = df_new_shape.rename(columns={"Date": "Period", "variable": "DimentionName"})
df_final["Period"] = df_final["Period"].apply(gregorian_day)
cubes.add_cube(scraper, df_final, title)
cubes.output_all()


