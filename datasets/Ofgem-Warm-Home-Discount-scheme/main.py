# +
import pandas as pd 
from gssutils import * 
import json

# Since scraper cannot pickup datasets from charts, dataURL is used in info.json file as an alternative for loading datasets.
# There are three charts from which data has to be extracted and thus after processing of each chart data, dataURL in info.json is modified.

# The three csv urls as of writing are 
# 1. https://www.ofgem.gov.uk/node/112635/revisions/349355/csv
# 2. https://www.ofgem.gov.uk/node/112638/revisions/349359/csv
# 3. https://www.ofgem.gov.uk/node/112641/revisions/349537/csv


# +
publisher = "The Office of Gas and Electricity Markets"
title = "warm-home-discount-distribution-expenditure-year".replace('-', ' ')

with open('info.json') as f:
  info_file_data = json.load(f)
info_file_data["dataURL"] = "https://www.ofgem.gov.uk/node/112635/revisions/349355/csv?fake=.csv"
with open('info.json', 'w') as f:
    json.dump(info_file_data, f, indent=2)
scraper = Scraper(seed="info.json")
title = "ofgem-112635-WarmHomeDiscount_Distributionofexpenditurebyyear".replace('-', ' ')
scraper.distributions[0].title = title
scraper

# +
cubes = Cubes("info.json")
trace = TransformTrace()
link = scraper.distributions[0].downloadURL
columns = ['Spending proportion', 'Dimension 1', 'Value']
trace.start(publisher, title, columns, link)

df = scraper.distributions[0].as_pandas()

dimensions = list(df.columns) # list of columns
dimensions = [col for col in dimensions if 'spending proportion' not in col.lower()] # list of the dimensions

df_new_shape = pd.melt(df, id_vars=["Spending proportion"])
df_new_shape = df_new_shape.rename(columns={"variable": "Dimension_1", "value": "Value"})

trace.Spending_proportion("Values taken from 'Spending proportion' column")
trace.Dimension_1("Values one of {}", dimensions)
trace.Value("Values taken from {} columns", dimensions)

cubes.add_cube(scraper, df_new_shape, title)
cubes.output_all()

trace.store(title, df_new_shape)
trace.render("spec_v1.html")

df_new_shape
# -

with open('info.json') as f:
  info_file_data = json.load(f)
info_file_data["dataURL"] = "https://www.ofgem.gov.uk/node/112638/revisions/349359/csv?fake=.csv"
with open('info.json', 'w') as f:
    json.dump(info_file_data, f, indent=2)
scraper = Scraper(seed="info.json")
title = "warm-home-discount-total-expenditure-obligated-suppliers-scheme-year-8-2018-19".replace('-', ' ')
scraper.distributions[0].title = title
scraper


# +
def sanitize_values(value):
     # removing comma and whitespace from values
     try:
         new_value = value.replace(' ', '').replace(',', '').strip()
         return new_value
     except:
         return ''

cubes = Cubes("info.json")
trace = TransformTrace()
link = scraper.distributions[0].downloadURL
columns = ['Supplier', 'Dimension 1', 'Value']
trace.start(publisher, title, columns, link)

df = scraper.distributions[0].as_pandas()

dimensions = list(df.columns) # list of columns
dimensions = [col for col in dimensions if 'supplier' not in col.lower()] # list of the dimensions

df_new_shape = pd.melt(df, id_vars=["Supplier"])
df_new_shape = df_new_shape.rename(columns={"variable": "Dimension_1", "value": "Value"})

trace.Supplier("Values taken from 'Supplier' column")
trace.Dimension_1("Values one of {}", dimensions)
trace.Value("Values taken from {} columns", dimensions)

df_new_shape["Value"] = df_new_shape["Value"].apply(sanitize_values)
trace.Value("Removed commas and whitespaces from Values")

cubes.add_cube(scraper, df_new_shape, title)
cubes.output_all()

trace.store(title, df_new_shape)
trace.render("spec_v1.html")

df_new_shape
# -

with open('info.json') as f:
  info_file_data = json.load(f)
info_file_data["dataURL"] = "https://www.ofgem.gov.uk/node/112641/revisions/349537/csv?fake=.csv"
with open('info.json', 'w') as f:
    json.dump(info_file_data, f, indent=2)
scraper = Scraper(seed="info.json")
title = "warm-home-discount-percentage-spend-nation-scheme-year-8-2018-19".replace('-', ' ')
scraper.distributions[0].title = title
scraper

# +
cubes = Cubes("info.json")
trace = TransformTrace()
link = scraper.distributions[0].downloadURL
columns = ['Nation', 'Total spend']
trace.start(publisher, title, columns, link)

df = scraper.distributions[0].as_pandas()

trace.Nation("Values taken from 'Nation' column")
trace.Total_spend("Values taken from Total spend column")

cubes.add_cube(scraper, df, title)
cubes.output_all()

trace.store(title, df)
trace.render("spec_v1.html")

df
# -


