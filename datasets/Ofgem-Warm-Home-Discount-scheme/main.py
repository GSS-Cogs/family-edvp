#!/usr/bin/env python
# coding: utf-8

# In[52]:


from gssutils import *
from dateutil.parser import parse
import json

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


# In[53]:


publisher = "The Office of Gas and Electricity Markets"

with open('distribution-expenditure-info.json') as f:
  info_file_data = json.load(f)
info_file_data["dataURL"] = "https://www.ofgem.gov.uk/node/112635/revisions/374173/csv?fake=.csv"
with open('distribution-expenditure-info.json', 'w') as f:
    json.dump(info_file_data, f, indent=2)

scraper = Scraper(seed="distribution-expenditure-info.json")
scraper


# In[54]:



df = pd.read_csv('distribution-expenditure.csv')

dimensions = list(df.columns) #%%list of columns
dimensions = [col for col in dimensions if 'category' not in col.lower()] #%%list of the dimensions

df_new_shape = pd.melt(df, id_vars=["Category"])
df_new_shape = df_new_shape.rename(columns={"variable": "Support Element", "value": "Value"})

df = df_new_shape[['Category', 'Support Element', 'Value']]

df['Scheme Year'] = df.apply(lambda x: left(x['Category'].replace('Scheme ', ''), 6), axis = 1)

df = df.replace({'Category' : {'Scheme Year 1 2011/12' : '1 April 2011 to 31 March 2012',
                             'Scheme Year 2 2012/13': '1 April 2012 to 31 March 2013',
                             'Scheme Year 3 2013/14': '1 April 2013 to 31 March 2014',
                             'Scheme Year 4 2014/15': '1 April 2014 to 31 March 2015',
                             'Scheme Year 5 2015/16': '1 April 2015 to 31 March 2016',
                             'Scheme Year 6 2016/17': '1 July 2016 to 31 May 2017',
                             'Scheme Year 7 2017/18': '1 June 2017 to 31 March 2018',
                             'Scheme Year 8 2018/19': '15 August 2018 to 31 March 2019',
                             'Scheme Year 9 2019/20': '1 April 2019 to 31 March 2020'}})

df['Period Lower'] = df.apply(lambda x: parse(x['Category'].split(' to ')[0]).date(), axis = 1)
df['Period Higher'] = df.apply(lambda x: parse(x['Category'].split(' to ')[1]).date(), axis = 1)
df['Period'] = df.apply(lambda x: 'gregorian-interval/'+ str(x['Period Lower']) + 'T00:00:00/P' + str((x['Period Higher'] - x['Period Lower']).days) + 'D', axis = 1)

df['Value'] = df.apply(lambda x: str(x['Value']).replace('%', ''), axis = 1)

df['Measure Type'] = 'expenditure'
df['Unit'] = 'percent'

df = df[['Period', 'Scheme Year', 'Support Element', 'Value', 'Measure Type', 'Unit']]

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Value']

for col in df.columns.values.tolist():
    if col in COLUMNS_TO_NOT_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

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

df.head(10)


# In[55]:



df.to_csv('distribution-expenditure-observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('distribution-expenditure-catalog-metadata.json')


# In[56]:





with open('total-expenditure-info.json') as f:
  info_file_data = json.load(f)
info_file_data["dataURL"] = "https://www.ofgem.gov.uk/node/112638/revisions/374171/csv?fake=.csv"
with open('total-expenditure-info.json', 'w') as f:
    json.dump(info_file_data, f, indent=2)
    
scraper = Scraper(seed="total-expenditure-info.json")
scraper



# In[57]:





df = pd.read_csv('total-expenditure.csv')

dimensions = list(df.columns) #%%list of columns
dimensions = [col for col in dimensions if 'category' not in col.lower()] #%%list of the dimensions

df_new_shape = pd.melt(df, id_vars=["Category"])
df_new_shape = df_new_shape.rename(columns={"variable": "Support Element", "value": "Value", 'Category' : 'Supplier'})

df = df_new_shape.fillna('')
df['Period'] = df.apply(lambda x: 'gregorian-interval/'+ str(parse('01 April 2019').date()) + 'T00:00:00/P' + str((parse('31 March 2020') - parse('01 April 2019')).days) + 'D', axis = 1)
df['Scheme Year'] = 'year-9'
#These two things need updating to be automatically updated
df['Marker'] = df.apply(lambda x: 'not-applicable' if x['Value'] == '' else '', axis = 1)

df['Measure Type'] = 'expenditure'
df['Unit'] = 'gbp'

df = df[['Period', 'Scheme Year', 'Support Element', 'Supplier', 'Marker', 'Value', 'Measure Type', 'Unit']]

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err


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

df.head(10)



# In[58]:



df.to_csv('total-expenditure-observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('total-expenditure-catalog-metadata.json')


# In[59]:





with open('percentage-spend-info.json') as f:
  info_file_data = json.load(f)
info_file_data["dataURL"] = "https://www.ofgem.gov.uk/node/112641/revisions/374169/csv?fake=.csv"
with open('percentage-spend-info.json', 'w') as f:
    json.dump(info_file_data, f, indent=2)
    
scraper = Scraper(seed="percentage-spend-info.json")
scraper



# In[60]:





df = pd.read_csv('percentage-spend.csv')

df = df.rename(columns={'Total Spend' : 'Value', 'Category' : 'Nation'})
df['Period'] = df.apply(lambda x: 'gregorian-interval/'+ str(parse('01 April 2019').date()) + 'T00:00:00/P' + str((parse('31 March 2020') - parse('01 April 2019')).days) + 'D', axis = 1)
df['Scheme Year'] = 'year-9'
#These two things need updating to be automatically updated

df = df.replace({'Nation' : {'England' : 'E92000001',
                             'Scotland' : 'S92000003',
                             'Wales' : 'W92000004'}})

df['Measure Type'] = 'expenditure'
df['Unit'] = 'percent'

df = df[['Period', 'Scheme Year', 'Nation', 'Value', 'Measure Type', 'Unit']]

scraper.dataset.title = 'Warm Home Discount Scheme: Percentage spend by nation'

scraper.dataset.comment = """
This data shows a by nation view of the direct support provided to fuel poor customers through energy bill rebates for the ‘core group’ and ‘broader group’ elements of the Warm Home Discount (WHD).
"""
scraper.dataset.description = """
Data shows a by nation view of the direct support provided to fuel poor customers through energy bill rebates for the ‘core group’ and ‘broader group’ elements of the Warm Home Discount (WHD). It comprises all participating suppliers in year 8 (2018/19) of the scheme.
The WHD is a government energy scheme which aims to help people who are in fuel poverty or are at risk of it. It focuses spending against three different support elements, categorised as ‘core group’, ‘broader group’ and ‘industry initiative’ spending.
For more on the scheme elements and how they work, see our overview page at Warm Home Discount:
https://www.ofgem.gov.uk/environmental-programmes/social-programmes/warm-home-discount-whd
We have gathered this information from obligated suppliers for information purposes, and as such it should be considered as advisory only. Scheme year 5 (2015/6) was the first year we have collected this data.
We update this chart on an annual basis.
"""

df.head(10)


# In[61]:



df.to_csv('percentage-spend-observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('percentage-spend-catalog-metadata.json')

