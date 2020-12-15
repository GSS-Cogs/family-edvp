#!/usr/bin/env python
# coding: utf-8
# %%

# %%


import pandas as pd 
from gssutils import * 
import json
from dateutil.parser import parse

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


# %%





# %%


#The three csv urls as of writing are
#1. https://www.ofgem.gov.uk/node/112635/revisions/349355/csv
#2. https://www.ofgem.gov.uk/node/112638/revisions/349359/csv
#3. https://www.ofgem.gov.uk/node/112641/revisions/349537/csv


# %%


trace = TransformTrace()
cubes = Cubes("info.json", job_name='')

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


# %%


link = scraper.distributions[0].downloadURL
columns = ['Period', 'Scheme Year', 'Support Element', 'Value']
trace.start(publisher, 'percentageexpenditure', columns, link)

df = scraper.distributions[0].as_pandas()

dimensions = list(df.columns) #%%list of columns
dimensions = [col for col in dimensions if 'spending proportion' not in col.lower()] #%%list of the dimensions

df_new_shape = pd.melt(df, id_vars=["Spending proportion"])
df_new_shape = df_new_shape.rename(columns={"variable": "Support Element", "value": "Value"})

df = df_new_shape[['Spending proportion', 'Support Element', 'Value']]

df['Scheme Year'] = df.apply(lambda x: left(x['Spending proportion'].replace('Scheme ', ''), 6), axis = 1)
#df['Period'] = df['Spending proportion']

df = df.replace({'Spending proportion' : {'Scheme Year 1 2011/12' : '1 April 2011 to 31 March 2012',
                             'Scheme Year 2 2012/13': '1 April 2012 to 31 March 2013',
                             'Scheme Year 3 2013/14': '1 April 2013 to 31 March 2014',
                             'Scheme Year 4 2014/15': '1 April 2014 to 31 March 2015',
                             'Scheme Year 5 2015/16': '1 April 2015 to 31 March 2016',
                             'Scheme Year 6 2016/17': '1 July 2016 to 31 May 2017',
                             'Scheme Year 7 2017/18': '1 June 2017 to 31 March 2018',
                             'Scheme Year 8 2018/19': '15 August 2018 to 31 March 2019'}})

df['Period Lower'] = df.apply(lambda x: parse(x['Spending proportion'].split(' to ')[0]).date(), axis = 1)
df['Period Higher'] = df.apply(lambda x: parse(x['Spending proportion'].split(' to ')[1]).date(), axis = 1)
df['Period'] = df.apply(lambda x: 'gregorian-interval/'+ str(x['Period Lower']) + 'T00:00:00/P' + str((x['Period Higher'] - x['Period Lower']).days) + 'D', axis = 1)

df = df[['Period', 'Scheme Year', 'Support Element', 'Value']]

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Value']

for col in df.columns.values.tolist():
    if col in COLUMNS_TO_NOT_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

mapping = {}
with open("info.json") as f:
    info_json = json.load(f)

    # "Value" entry for this dataset
    #mapping["Value"] = {"unit": "http://gss-data.org.uk/def/concept/measurement-units/percentage",
    #                    "measure": "http://gss-data.org.uk/def/measure/expenditure",
    #                    "datatype": "double"}

    # Read the map back into the cubes class
    #info_json["transform"]["columns"]['Value'] = mapping
    #cubes.info = info_json
    
    info_json["transform"]["columns"]['Value']["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/percentage"
    info_json["transform"]["columns"]['Value']["measure"] = "http://gss-data.org.uk/def/measure/expenditure"
    info_json["transform"]["columns"]['Value']["datatype"] = "double"
    
#if SHOW_MAPPING:
print("Mapping for: ", 'percentageexpenditure')
print(json.dumps(mapping, indent=2))
print("\n")

trace.Period("Values taken from 'Spending proportion' column")
trace.Scheme_Year("Values taken from 'Spending proportion' column")
trace.Support_Element("Values one of {}", dimensions)
trace.Value("Values taken from {} columns", dimensions)

scraper.dataset.title = 'Warm Home Discount Scheme: Distribution of expenditure by year'

scraper.dataset.comment = """
This data shows the distribution of expenditure for each year so far of the Warm Home Discount (WHD), a government energy scheme which aims to help people who are in fuel poverty or are at risk of it.
"""

scraper.dataset.description = """
Distribution of expenditure for each year so far of the Warm Home Discount (WHD), a government energy scheme which aims to help people who are in fuel poverty or are at risk of it.
The scheme focuses spending against three different support elements, categorised by a ‘core group’, ‘broader group’ and ‘industry initiatives’. ‘Legacy spending’ applied in scheme years 1 to 3.
Energy suppliers with over 250,000 domestic customers (referred to as ‘large suppliers’) are obligated to participate in each element of the scheme. Some suppliers with a smaller customer base also voluntarily participate. They only take part in the ‘core group’.
For more on the scheme elements and how they work, see our overview page at Warm Home Discount:
https://www.ofgem.gov.uk/environmental-programmes/social-programmes/warm-home-discount-whd
We update this chart on an annual basis.
"""

#cubes.add_cube(scraper, df, 'percentageexpenditure', info_json_dict=info_json)
#trace.store('percentageexpenditure', df)

df.head(10)


# %%
import os
from urllib.parse import urljoin

csvName = 'percentageexpenditure.csv'
out = Path('out')
out.mkdir(exist_ok=True)
df.drop_duplicates().to_csv(out / csvName, index = False)
df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')

scraper.dataset.family = 'edvp'
dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + "/percentageexpenditure"
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(dataset_path)

csvw_transform = CSVWMapping()
csvw_transform.set_csv(out / csvName)
csvw_transform.set_mapping(info_json)
csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
csvw_transform.write(out / f'{csvName}-metadata.json')

with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

# %%


with open('info.json') as f:
  info_file_data = json.load(f)
info_file_data["dataURL"] = "https://www.ofgem.gov.uk/node/112638/revisions/349359/csv?fake=.csv"
with open('info.json', 'w') as f:
    json.dump(info_file_data, f, indent=2)
scraper = Scraper(seed="info.json")
title = "warm-home-discount-total-expenditure-obligated-suppliers-scheme-year-8-2018-19".replace('-', ' ')
scraper.distributions[0].title = title
scraper


# %%


def sanitize_values(value):
     #%%removing comma and whitespace from values
     try:
         new_value = value.replace(' ', '').replace(',', '').strip()
         return new_value
     except:
         return ''

link = scraper.distributions[0].downloadURL
columns = ['Period', 'Scheme Year', 'Supplier', 'Support Element', 'Value']
trace.start(publisher, 'gbpexpenditure', columns, link)

df = scraper.distributions[0].as_pandas()

dimensions = list(df.columns) #%%list of columns
dimensions = [col for col in dimensions if 'supplier' not in col.lower()] #%%list of the dimensions

df_new_shape = pd.melt(df, id_vars=["Supplier"])
df_new_shape = df_new_shape.rename(columns={"variable": "Support Element", "value": "Value"})

df = df_new_shape.fillna('')
df['Period'] = df.apply(lambda x: 'gregorian-interval/'+ str(parse('15 August 2018').date()) + 'T00:00:00/P' + str((parse('31 March 2019') - parse('15 August 2018')).days) + 'D', axis = 1)
df['Scheme Year'] = 'year-8'
df['Marker'] = df.apply(lambda x: 'not-applicable' if x['Value'] == '' else '', axis = 1)
df['Value'] = df.apply(lambda x: sanitize_values(x['Value']), axis = 1)

df = df[['Period', 'Scheme Year', 'Support Element', 'Supplier', 'Marker', 'Value']]

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

mapping = {}
with open("info.json") as f:
    info_json = json.load(f)

    # "Value" entry for this dataset
    #mapping["Value"] = {"unit": "http://gss-data.org.uk/def/concept/measurement-units/gdp",
    #                    "measure": "http://gss-data.org.uk/def/measure/expenditure",
    #                    "datatype": "integer"}

    # Read the map back into the cubes class
    #info_json["transform"]["columns"]['Value'] = mapping
    #cubes.info = info_json

    info_json["transform"]["columns"]['Value']["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp"
    info_json["transform"]["columns"]['Value']["measure"] = "http://gss-data.org.uk/def/measure/expenditure"
    info_json["transform"]["columns"]['Value']["datatype"] = "integer"
    
    
#if SHOW_MAPPING:
print("Mapping for: ", 'gbpexpenditure')
print(json.dumps(mapping, indent=2))
print("\n")

trace.Supplier("Values taken from 'Supplier' column")
trace.Support_Element("Values one of {}", dimensions)
trace.Value("Values taken from {} columns", dimensions)
trace.Period("Value added as '15 August 2018 to 31 March 2019'")
trace.Scheme_Year("Value added as 'Year 8'")
trace.Value("Removed commas and whitespaces from Values")

scraper.dataset.title = 'Warm Home Discount Scheme: Total expenditure by obligated suppliers'

scraper.dataset.comment = """
Data details how much suppliers spent fulfilling their obligation of the Warm Home Discount (WHD), a government energy scheme which aims to help people who are in fuel poverty or are at risk of it.
"""

scraper.dataset.description = """
Data details how much suppliers spent fulfilling their obligation of the Warm Home Discount (WHD), a government energy scheme which aims to help people who are in fuel poverty or are at risk of it.
Energy suppliers with over 250,000 domestic customers (referred to as ‘large suppliers’) are obligated to participate in each support element of the scheme, categorised by a ‘core group’, ‘broader group’ and ‘industry initiatives’. They are also allocated targets based on their share of the domestic GB energy market.
For more on the scheme elements and how they work, see our overview page at Warm Home Discount:
https://www.ofgem.gov.uk/environmental-programmes/social-programmes/warm-home-discount-whd
We update this chart on an annual basis.
"""

#cubes.add_cube(scraper, df, 'gbpexpenditure', info_json_dict=info_json)
#trace.store('gbpexpenditure', df)

df.head(10)


# %%
import os
from urllib.parse import urljoin

csvName = 'gbpexpenditure.csv'
out = Path('out')
out.mkdir(exist_ok=True)
df.drop_duplicates().to_csv(out / csvName, index = False)
df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')

scraper.dataset.family = 'edvp'
dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + "/gbpexpenditure"
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(dataset_path)

csvw_transform = CSVWMapping()
csvw_transform.set_csv(out / csvName)
csvw_transform.set_mapping(info_json)
csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
csvw_transform.write(out / f'{csvName}-metadata.json')

with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

# %%


with open('info.json') as f:
  info_file_data = json.load(f)
info_file_data["dataURL"] = "https://www.ofgem.gov.uk/node/112641/revisions/349537/csv?fake=.csv"
with open('info.json', 'w') as f:
    json.dump(info_file_data, f, indent=2)
scraper = Scraper(seed="info.json")
title = "warm-home-discount-percentage-spend-nation-scheme-year-8-2018-19".replace('-', ' ')
scraper.distributions[0].title = title
scraper


# %%


link = scraper.distributions[0].downloadURL
columns = ['Nation', 'Value']
trace.start(publisher, 'nationexpenditure', columns, link)

df = scraper.distributions[0].as_pandas()

df = df.rename(columns={'Total spend' : 'Value'})
df['Period'] = df.apply(lambda x: 'gregorian-interval/'+ str(parse('15 August 2018').date()) + 'T00:00:00/P' + str((parse('31 March 2019') - parse('15 August 2018')).days) + 'D', axis = 1)
df['Scheme Year'] = 'year-8'
df['Value'] = df.apply(lambda x: sanitize_values(x['Value']), axis = 1)

df = df.replace({'Nation' : {'England' : 'E92000001',
                             'Scotland' : 'S92000003',
                             'Wales' : 'W92000004'}})

df = df[['Period', 'Scheme Year', 'Nation', 'Value']]

mapping = {}
with open("info.json") as f:
    info_json = json.load(f)

    # "Value" entry for this dataset
    #mapping["Value"] = {"unit": "http://gss-data.org.uk/def/concept/measurement-units/percentage",
    #                    "measure": "http://gss-data.org.uk/def/measure/expenditure",
    #                    "datatype": "double"}

    # Read the map back into the cubes class
    #info_json["transform"]["columns"]['Value'] = mapping
    #cubes.info = info_json
    
    info_json["transform"]["columns"]['Value']["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/percentage"
    info_json["transform"]["columns"]['Value']["measure"] = "http://gss-data.org.uk/def/measure/expenditure"
    info_json["transform"]["columns"]['Value']["datatype"] = "double"

#if SHOW_MAPPING:
print("Mapping for: ", 'nationexpenditure')
print(json.dumps(mapping, indent=2))
print("\n")

trace.Nation("Values taken from 'Nation' column")
trace.Nation("Replace Values with Geography Codes")

trace.Value("Values taken from Total spend column")

scraper.dataset.title = 'Warm Home Discount Scheme: Percentage spend by nation'

scraper.dataset.comment = """
This graph shows a by nation view of the direct support provided to fuel poor customers through energy bill rebates for the ‘core group’ and ‘broader group’ elements of the Warm Home Discount (WHD).
"""
scraper.dataset.description = """
Data shows a by nation view of the direct support provided to fuel poor customers through energy bill rebates for the ‘core group’ and ‘broader group’ elements of the Warm Home Discount (WHD). It comprises all participating suppliers in year 8 (2018/19) of the scheme.
The WHD is a government energy scheme which aims to help people who are in fuel poverty or are at risk of it. It focuses spending against three different support elements, categorised as ‘core group’, ‘broader group’ and ‘industry initiative’ spending.
For more on the scheme elements and how they work, see our overview page at Warm Home Discount:
https://www.ofgem.gov.uk/environmental-programmes/social-programmes/warm-home-discount-whd
We have gathered this information from obligated suppliers for information purposes, and as such it should be considered as advisory only. Scheme year 5 (2015/6) was the first year we have collected this data.
We update this chart on an annual basis.
"""

#cubes.add_cube(scraper, df, 'nationexpenditure', info_json_dict=info_json)
#trace.store('nationexpenditure', df)

df.head(10)


# %%
import os
from urllib.parse import urljoin

csvName = 'nationexpenditure.csv'
out = Path('out')
out.mkdir(exist_ok=True)
df.drop_duplicates().to_csv(out / csvName, index = False)
df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')

scraper.dataset.family = 'edvp'
dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + "/nationexpenditure"
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(dataset_path)

csvw_transform = CSVWMapping()
csvw_transform.set_csv(out / csvName)
csvw_transform.set_mapping(info_json)
csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
csvw_transform.write(out / f'{csvName}-metadata.json')

with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

# %%


#trace.render("spec_v1.html")
#cubes.output_all()


# %%
