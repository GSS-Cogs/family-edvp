#!/usr/bin/env python
# coding: utf-8

# In[277]:


import json

import pandas as pd

from gssutils import *


# In[278]:


infoFileName = 'info.json'

info    = json.load(open(infoFileName))
scraper = Scraper(seed=infoFileName)
distro  = scraper.distribution(latest=True, title=lambda t: 'Renewable electricity capacity and generation (ET 6.1 - quarterly)' in t)


# In[279]:


# Enumerate the tabs
tabs = distro.as_databaker()

# *Method explaination*
#
# `[tab.name for tab in tabs]`
#
# gives us
#
# `['Contents', 'Highlights', 'Main Table', 'Annual', 'Quarter', 'England - Annual', 'England - Qtr', 'Northern Ireland - Annual', 'Northern Ireland - Qtr', 'Scotland- Annual', 'Scotland - Qtr', 'Wales- Annual', 'Wales - Qtr', 'Calculation', 'checks']`
#
# so the tabs we want end are the only ones which end with r or l

# Generate a dictionary of the tab name with the databaker contents as the value
tabs = {x.name: x for x in tabs if x.name.endswith('r') | x.name.endswith('l')}

nations = {
    'England': 'E92000001',
    'Northern Ireland': 'N92000002',
    'Scotland': 'S92000003',
    'Wales': 'W92000004'
}


def et61_all(name, tab) -> pd.DataFrame():

    print(name)

    cell = tab.excel_ref('A1')

    geog = 'K02000001'

    years = cell.shift(1, 6).expand(RIGHT).is_not_blank()
    cats = cell.shift(0, 6).fill(DOWN).is_not_blank()
    obvs = cats.fill(RIGHT).is_not_blank() - tab.filter(contains_string('ELECTRICITY GENERATED')).fill(RIGHT).is_not_blank() - tab.filter(contains_string('LOAD FACTORS (%)')).fill(RIGHT).is_not_blank()
    cats = cats & obvs.expand(LEFT)
    heads = cell.shift(0, 6).expand(DOWN).is_not_blank() - cats | tab.filter(contains_string('ELECTRICITY GENERATED'))

    dims = [
            HDim(years, 'Year', DIRECTLY, ABOVE),
            HDim(heads, 'Head', CLOSEST, ABOVE),
            HDim(cats, 'Category', CLOSEST, ABOVE),
            HDimConst('Geography', geog)
            ]

    savepreviewhtml(ConversionSegment(tab, dims, obvs),fname=tab.name + "Preview.html")

    return ConversionSegment(tab, dims, obvs).topandas()


def et61_nat(name, tab) -> pd.DataFrame():

    cell = tab.excel_ref('A1')

    geog = nations[tab.name.split('-')[0].strip()]

    years = cell.shift(1, 6).expand(RIGHT).is_not_blank()
    cats = cell.shift(0, 6).fill(DOWN).is_not_blank()
    obvs = cats.fill(RIGHT).is_not_blank() - tab.filter(contains_string('ELECTRICITY GENERATED')).fill(RIGHT).is_not_blank() - tab.filter(contains_string('LOAD FACTORS (%)')).fill(RIGHT).is_not_blank() - tab.filter(contains_string('CUMULATIVE INSTALLED CAPACITY (MW)')).fill(RIGHT).is_not_blank()
    cats = cats & obvs.fill(LEFT)
    heads = cell.shift(0, 6).expand(DOWN).is_not_blank() - cats - tab.filter('Offshore Wind')

    dims = [
        HDim(years, 'Year', DIRECTLY, ABOVE),
        HDim(heads, 'Head', CLOSEST, ABOVE),
        HDim(cats, 'Category', DIRECTLY, LEFT),
        HDimConst('Geography', geog)
        ]

    savepreviewhtml(ConversionSegment(tab, dims, obvs),fname=tab.name + "Preview.html")

    return ConversionSegment(tab, dims, obvs).topandas()


df = pd.DataFrame()

for name, tab in tabs.items():
    if name == 'Quarter' or name == 'Annual':
        df = pd.concat([df, et61_all(name, tab)], axis=0)
    else:
        df = pd.concat([df, et61_nat(name, tab)], axis=0)


df = df[df['Category'] != 'Days in quarter']

df.reset_index(inplace=True, drop=True)


# In[280]:


# Next, strip these values from Head
df['Head'] = df['Head'].str.replace(r'\([^)]*\)', '').str.strip()

df['Quarter'] = df.apply(lambda x: x['Year'][-11:] if 'quarter' in x['Year'] else x['Year'], axis = 1)
df['Year'] = df.apply(lambda x: x['Year'][:4] if 'quarter' in x['Year'] else x['Year'], axis = 1)

df = df.replace({'Quarter' : {'1st quarter' : 'Q1',
                              '2nd quarter' : 'Q2',
                              '3rd quarter' : 'Q3',
                              '4th quarter' : 'Q4'}})

df['Period'] = df.apply(lambda x: 'quarter/' + x['Year'][:4] + '-' + x['Quarter'] if 'Q' in x['Quarter'] else 'year/' + x['Year'], axis = 1)

df.drop(['Year', 'Quarter'], axis=1, inplace=True)

df


# In[281]:


indexNames = df[ df['Head'].str.contains('SHARES OF ELECTRICITY GENERATED')].index
df.drop(indexNames, inplace = True)

df = df.replace({'Category' : {
            'Animal Biomass (non-AD) [note 2]' : 'Animal Biomass (non-AD)',
            'Animal Biomass (non-AD) [note 2] [note 6]' : 'Animal Biomass (non-AD)', 
            'Co-firing [note 4]' : 'Co-firing',
            'Energy from waste [note 8]' : 'Energy from waste', 
            'Hydro [note 6]' : 'Hydro', 
            'Landfill gas [note 6]' : 'Landfill gas', 
            'Non-biodegradable wastes [note 9]' : 'Non-biodegradable wastes', 
            'Offshore Wind [note 6] [note 7]' : 'Offshore Wind', 
            'Onshore Wind [note 6]' : 'Onshore Wind', 
            'Other biomass (inc. co-firing) [note 14]' : 'Other biomass',
            'Other biomass (inc. co-firing) [note 4]' : 'Other biomass',
            'Other biomass (inc. co-firing) [note 6] [note 14]' : 'Other biomass',
            'Other biomass [note 2]' : 'Other biomass', 
            'Plant Biomass [note 3]' : 'Plant Biomass',
            'Plant Biomass [note 3] [note 6]' : 'Plant Biomass', 
            'Sewage sludge digestion [note 6]' : 'Sewage sludge digestion', 
            'Shoreline wave / tidal [note 6]' : 'Shoreline Wave and Tidal', 
            'Solar PV [note 6]' : 'Solar PV', 
            'Solar photovoltaics [note 6]' : 'Solar photovoltaics',
            'Landfill gas ' : 'Landfill gas'},
                'DATAMARKER' : {'[x]' : 'not-available'},
                'Head' : {'CUMULATIVE INSTALLED CAPACITY  \n[note 1]' : 'cumulative-installed-capacity',
                          'CUMULATIVE INSTALLED CAPACITY  [note 1]' : 'cumulative-installed-capacity',
                          'ELECTRICITY GENERATED  \n[note 5]' : 'electricty-generated', 
                          'ELECTRICITY GENERATED  [note 5]' : 'electricty-generated',
                          'ELECTRICITY GENERATED  [note 6]' : 'electricty-generated', 
                          'LOAD FACTORS  \n[note 10]' : 'load-factors',
                          'LOAD FACTORS  [note 10]' : 'load-factors'}})

df['Unit'] = df['Head']

df = df.replace({'Unit' : {'Cumulative Installed Capacity' : 'mw',
                          'Electricty Generated' : 'gwh',
                          'Load Factors' : 'percent'}})

df['OBS'] = df.apply(lambda x: 0 if x['DATAMARKER'] == 'not-available' else x['OBS'], axis = 1)

df


# In[282]:


df = df.rename(columns={'Category' : 'Fuel', 'Head' : 'Measure Type', 'OBS' : 'Value', 'Geography' : 'Region', 'DATAMARKER' : 'Marker'}).fillna('')

df = df[['Period', 'Region', 'Fuel', 'Value', 'Marker', 'Measure Type', 'Unit']]

df


# In[283]:


scraper.dataset.title = info['title']
scraper.dataset.comment = info['description']

df.to_csv('observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')


# In[284]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)

