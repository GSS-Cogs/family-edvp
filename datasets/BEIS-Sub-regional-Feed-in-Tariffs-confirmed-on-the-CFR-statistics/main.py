#!/usr/bin/env python
# coding: utf-8

# In[15]:


from gssutils import *
import pandas as pd
import json

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

scraper = Scraper(seed="info.json")
scraper.dataset.title = 'Sub-regional Feed-in Tariffs confirmed on the CFR statistics'
scraper


# In[16]:


for i in scraper.distributions:
    display(i)


# In[17]:


distribution = scraper.distribution(title=lambda t: 'Feed-in Tariffs' in t)
datasetTitle = distribution.title
print(distribution.downloadURL)
print(datasetTitle)


# In[18]:


# Extract all the tabs from the spread sheet
tabs = {tab.name: tab for tab in distribution.as_databaker()}


# In[19]:


# List out all the tab name to cross verify with the spread sheet
for tab in tabs:
    print(tab)


# In[20]:


columns = ["Region", "Region Name", "Period", "Technology", "Installation", "Households", "Local Or Parliamentary Code",
           "Local Enterprise Partnerships", "Leps Authority", "Marker", "Unit"]


# In[21]:


tidy_tabs = {}

import numpy as np
# Filtering out the tabs which are not required and start the transform
for name, tab in tabs.items():
    if tab.name not in ['Latest Quarter - Region', 'Latest Quarter - Region (kW)']:
        continue

    print(tab.name)

    cell = tab.filter('Region')

    remove = tab.filter('Notes:').expand(RIGHT).expand(DOWN)

    region = cell.fill(DOWN).is_not_blank() - remove

    technology = cell.shift(1, -1).expand(RIGHT).is_not_blank() | tab.filter('Total Domestic').shift(-1, -1).expand(RIGHT)

    installation = cell.shift(2, -2).expand(RIGHT).is_not_blank()

    perTen = cell.shift(2, -2).expand(RIGHT) - cell.shift(2, -2)

    periodYear = cell.shift(2, -4)

    periodQuarter = cell.shift(2, -3)

    buildingType = cell.shift(2, 0).expand(RIGHT).is_not_blank()

    observations = region.shift(RIGHT).fill(RIGHT).is_not_blank()

    dimensions = [
        HDim(region, "Region", DIRECTLY, LEFT),
        HDim(technology, "Technology", CLOSEST, LEFT),
        HDim(installation, "Installation", CLOSEST, LEFT),
        HDim(perTen, 'per Ten', CLOSEST, RIGHT),
        HDim(periodYear, "Period Year", CLOSEST, LEFT),
        HDim(periodQuarter, "Period Quarter", CLOSEST, LEFT),
        HDim(buildingType, 'Building Type', DIRECTLY, ABOVE)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

    df = tidy_sheet.topandas()

    if 'kW' not in tab.name:
        df['Installation'] = df.apply(lambda x: 'installations per 10000 households' if 'Installations per 10,000 households' in x['per Ten'] else 'cumulative installations', axis = 1)

    df['Technology'] = df.apply(lambda x: 'all' if x['Technology'] == '' else x['Technology'], axis = 1)

    df = df.drop(['per Ten'], axis=1)

    tidy_tabs[tab.name] = df


# In[22]:


for name, tab in tabs.items():
    if tab.name not in ['Latest Quarter - LA', 'Latest Quarter - LA (kW)']:
        continue

    print(tab.name)

    cell = tab.filter('Local Authority Code5')

    remove = tab.filter('Notes:').expand(RIGHT).expand(DOWN)

    region = cell.fill(DOWN).is_not_blank() - remove

    technology = cell.shift(1, -1).expand(RIGHT).is_not_blank() | tab.filter('Total Domestic').shift(-1, -1).expand(RIGHT)

    installation = cell.shift(3, -2).expand(RIGHT).is_not_blank()

    periodYear = cell.shift(3, -4)

    periodQuarter = cell.shift(3, -3)

    buildingType = cell.shift(3, 0).expand(RIGHT).is_not_blank()

    observations = region.shift(2, 0).fill(RIGHT).is_not_blank()

    dimensions = [
        HDim(region, "Region", DIRECTLY, LEFT),
        HDim(technology, "Technology", CLOSEST, LEFT),
        HDim(installation, "Installation", CLOSEST, LEFT),
        HDim(periodYear, "Period Year", CLOSEST, LEFT),
        HDim(periodQuarter, "Period Quarter", CLOSEST, LEFT),
        HDim(buildingType, 'Building Type', DIRECTLY, ABOVE)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

    df = tidy_sheet.topandas()

    df['Technology'] = df.apply(lambda x: 'all' if x['Technology'] == '' else x['Technology'], axis = 1)

    tidy_tabs[tab.name] = df

df


# In[23]:


for name, tab in tabs.items():
    if tab.name not in ['Latest Quarter - PC', 'Latest Quarter - PC (kW)']:
        continue

    print(tab.name)

    cell = tab.filter('Parliamentary Constituency Code')

    remove = tab.filter('Notes:').expand(RIGHT).expand(DOWN)

    region = cell.fill(DOWN).is_not_blank() - remove

    technology = cell.shift(1, -1).expand(RIGHT).is_not_blank() | tab.filter('Total Domestic').shift(-1, -1).expand(RIGHT)

    installation = cell.shift(2, -2).expand(RIGHT).is_not_blank()

    periodYear = cell.shift(2, -4)

    periodQuarter = cell.shift(2, -3)

    buildingType = cell.shift(2, 0).expand(RIGHT).is_not_blank()

    observations = region.shift(1, 0).fill(RIGHT).is_not_blank()

    dimensions = [
        HDim(region, "Region", DIRECTLY, LEFT),
        HDim(technology, "Technology", CLOSEST, LEFT),
        HDim(installation, "Installation", CLOSEST, LEFT),
        HDim(periodYear, "Period Year", CLOSEST, LEFT),
        HDim(periodQuarter, "Period Quarter", CLOSEST, LEFT),
        HDim(buildingType, 'Building Type', DIRECTLY, ABOVE)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

    df = tidy_sheet.topandas()

    df['Technology'] = df.apply(lambda x: 'all' if x['Technology'] == '' else x['Technology'], axis = 1)

    tidy_tabs[tab.name] = df



# In[24]:




#All information in these tabs is covered by LA pages, these tabs just have the same data but with another column informing what LEP each LA is a part of

"""for name, tab in tabs.items():
    if tab.name not in ['Latest Quarter - LEPs', 'Latest Quarter - LEPs (kW)']:
        continue

    print(tab.name)

    cell = tab.filter('LEPs')

    remove = tab.filter('Notes:').expand(RIGHT).expand(DOWN)

    region = cell.fill(DOWN).is_not_blank() - remove

    technology = cell.shift(1, -1).expand(RIGHT).is_not_blank() | tab.filter('Total Domestic').shift(-1, -1).expand(RIGHT)

    installation = cell.shift(2, -2).expand(RIGHT).is_not_blank()

    periodYear = cell.shift(2, -4)

    periodQuarter = cell.shift(2, -3)

    buildingType = cell.shift(2, 0).expand(RIGHT).is_not_blank()

    observations = region.shift(1, 0).fill(RIGHT).is_not_blank()

    dimensions = [
        HDim(region, "Region", DIRECTLY, LEFT),
        HDim(technology, "Technology", CLOSEST, LEFT),
        HDim(installation, "Installation", CLOSEST, LEFT),
        HDim(periodYear, "Period Year", CLOSEST, LEFT),
        HDim(periodQuarter, "Period Quarter", CLOSEST, LEFT),
        HDim(buildingType, 'Building Type', DIRECTLY, ABOVE)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

    df = tidy_sheet.topandas()

    df['Technology'] = df.apply(lambda x: 'all' if x['Technology'] == '' else x['Technology'], axis = 1)

    tidy_tabs[tab.name] = df"""


# In[25]:


df = pd.concat(x for x in tidy_tabs.values())

df = df.rename(columns={'Technology' : 'Technology Type', 'Households' : 'Building Type', 'Installation' : 'Measure Type', 'OBS' : 'Value', 'DATAMARKER' : 'Marker'})

df['Period'] = df.apply(lambda x: 'quarter/' + left(x['Period Year'], 4) + '-Q' + mid(x['Period Quarter'], 8, 1), axis = 1)

df = df.replace({'Building Type' : {'Total Non-Domestic' : 'Non-Domestic', 'Total Domestic' : 'Domestic'},
                 'Measure Type' : {'Cumulative number of installations 2' : 'cumulative installations',
                                   'Cumulative installed capacity (kW) 2' : 'cumulative installed capacity',
                                   'Cumulative installed capacity 2' : 'cumulative installed capacity',
                                   'Installations per 10,000 households': 'installations per 10000 households'},
                 'Region' :        {'East of England' : 'E12000006',
                                    'East Midlands' : 'E12000004',
                                    'London' : 'E12000007',
                                    'North East' : 'E12000001',
                                    'North West' : 'E12000002',
                                    'South East' : 'E12000008',
                                    'South West' : 'E12000009',
                                    'West Midlands' : 'E12000005',
                                    'Yorkshire and The Humber' : 'E12000003',
                                    'Total for England' : 'E92000001',
                                    'Wales' : 'W92000004',
                                    'Scotland' : 'S92000003'}})

df['Unit'] = df.apply(lambda x: 'kilowatt' if 'capacity' in x['Measure Type'] else 'installation', axis = 1)

df = df[['Period', 'Region', 'Technology Type', 'Building Type', 'Value', 'Measure Type', 'Unit']]

indexNames = df[ df['Region'].isin(['Unallocated 4', 'Grand Total']) ].index
df.drop(indexNames, inplace = True)

COLUMNS_TO_NOT_PATHIFY = ['Period', 'Region', 'Technology Type', 'Building Type', 'Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df['Value'] = df['Value'].apply(lambda x: round(x, 2))
#having to round to 2 decimal places to fix some duplicate issues, should fix at later date but should be fine for proof of concept EDV stuff

df = df.drop_duplicates()

df


# In[26]:


scraper.dataset.comment = """Quarterly sub-regional statistics show the number of installations and total installed capacity by technology type in England, Scotland and Wales at the end the latest quarter that have been confirmed on the Central Feed-in Tariff Register."""

df.to_csv('observations.csv', index=False)

df


# In[27]:


catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')


# In[28]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)

