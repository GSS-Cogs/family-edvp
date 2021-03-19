#!/usr/bin/env python
# coding: utf-8

# In[24]:


# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.0
#   kernelspec:
#     display_name: Python 3.8.7 64-bit
#     metadata:
#       interpreter:
#         hash: 4cd7ab41f5fca4b9b44701077e38c5ffd31fe66a6cab21e0214b68d958d0e462
#     name: python3
# ---


# In[25]:


import json

import pandas as pd

from gssutils import *


# In[26]:


infoFileName = 'info.json'

info    = json.load(open(infoFileName))
scraper = Scraper(seed=infoFileName)
cubes   = Cubes(infoFileName)
distro  = scraper.distribution(latest=True, title=lambda t: 'Renewable electricity capacity and generation (ET 6.1 - quarterly)' in t)


# In[27]:


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

    cell = tab.filter('6 RENEWABLES')

    remove = tab.filter(contains_string('TOTAL ELECTRICITY GENERATED')).expand(RIGHT).expand(DOWN)

    geog = 'K02000001'

    if 'Annual' in [x.strip() for x in name.split('-')]:
        years = cell.shift(1, 5).expand(RIGHT).is_not_blank()
    else:
        years = cell.shift(1, 4).expand(RIGHT).is_not_blank()
        qrtrs = cell.shift(1, 5).expand(RIGHT).is_not_blank()
    cats = cell.shift(0, 6).expand(DOWN).is_not_blank() - remove
    obvs = cats.fill(RIGHT).is_not_blank() | tab.filter(contains_string('TOTAL ELECTRICITY GENERATED')).fill(RIGHT).is_not_blank()
    cats = cats & obvs.expand(LEFT)
    heads = cell.shift(0, 6).expand(DOWN).is_not_blank() - remove - cats | tab.filter(contains_string('TOTAL ELECTRICITY GENERATED'))

    if 'Annual' in [x.strip() for x in name.split('-')]:
        dims = [
            HDim(years, 'Year', DIRECTLY, ABOVE),
            HDim(heads, 'Head', CLOSEST, ABOVE),
            HDim(cats, 'Category', CLOSEST, ABOVE),
            HDimConst('Geography', geog)
            ]
    else:
        dims = [
            HDim(years, 'Year', DIRECTLY, ABOVE),
            HDim(qrtrs, 'Quarter', DIRECTLY, ABOVE),
            HDim(heads, 'Head', CLOSEST, ABOVE),
            HDim(cats, 'Category', CLOSEST, ABOVE),
            HDimConst('Geography', geog)
            ]

    savepreviewhtml(ConversionSegment(tab, dims, obvs),fname=tab.name + "Preview.html")

    return ConversionSegment(tab, dims, obvs).topandas()


def et61_nat(name, tab) -> pd.DataFrame():

    cell = tab.filter('6 RENEWABLES')

    geog = nations[tab.name.split('-')[0].strip()]

    if 'Annual' in [x.strip() for x in name.split('-')]:
        years = cell.shift(1, 5).expand(RIGHT).is_not_blank()
        remove = tab.filter('Days in year').expand(RIGHT).expand(DOWN)
    else:
        years = cell.shift(1, 4).expand(RIGHT).is_not_blank()
        qrtrs = cell.shift(1, 5).expand(RIGHT).is_not_blank()
        remove = tab.filter('Days in quarter').expand(RIGHT).expand(DOWN)
    cats = cell.shift(0, 6).expand(DOWN).is_not_blank() - remove
    obvs = cats.fill(RIGHT).is_not_blank() - tab.filter(contains_string('W'))
    cats = cats & obvs.fill(LEFT)
    heads = cell.shift(0, 6).expand(DOWN).is_not_blank() - remove - cats

    if 'Annual' in [x.strip() for x in name.split('-')]:
        dims = [
            HDim(years, 'Year', DIRECTLY, ABOVE),
            HDim(heads, 'Head', CLOSEST, ABOVE),
            HDim(cats, 'Category', DIRECTLY, LEFT),
            HDimConst('Geography', geog)
            ]
    else:
        dims = [
            HDim(years, 'Year', DIRECTLY, ABOVE),
            HDim(qrtrs, 'Quarter', DIRECTLY, ABOVE),
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

# Get the datamarkers from the Head column, as well as the units
extract = df['Head'].str.extract('\((.*?)\) \((.*?)\)')
# Uncomment to verify that the extract works as described
# df['Head'].value_counts(), extract[0].value_counts(), extract[1].value_counts()


# In[28]:


# So we're going to assign as described and verified above
df['Unit'] = extract[1]


# In[29]:


# Next, strip these values from Head
df['Head'] = df['Head'].str.replace(r'\([^)]*\)', '').str.strip()


# In[30]:


# Date formatting
df.loc[df['Quarter'].isna(),'Period'] = df['Year'].apply(lambda x : f"year/{x[:4]}")
df.loc[~df['Quarter'].isna(), 'Period'] = df.loc[~df['Quarter'].isna(), ['Year', 'Quarter']].apply(lambda x : f"quarter/{x[0][:4]}-Q{x[1][:1]}", axis=1)
df.drop(['Year', 'Quarter'], axis=1, inplace=True)

indexNames = df[ df['Head'].str.contains('SHARES OF ELECTRICITY GENERATED')].index
df.drop(indexNames, inplace = True)

df = df.replace({'Category' : {
            'Animal Biomass (non-AD) (2)' : 'Animal Biomass (non-AD)',
            'Animal Biomass (non-AD) (2,6)' : 'Animal Biomass (non-AD)',
            'Co-firing (4)'  : 'Co-firing',
            'Energy from waste (8)'  : 'Energy from waste',
            'Hydro (5)'  : 'Hydro',
            'Hydro (6)'  : 'Hydro',
            'Landfill gas '  : 'Landfill gas',
            'Landfill gas (5)'  : 'Landfill gas',
            'Landfill gas (6)'  : 'Landfill gas',
            'Non-biodegradable wastes (9)'  : 'Non-biodegradable wastes',
            'Offshore Wind (6,7)'  : 'Offshore Wind',
            'Onshore Wind (6)'  : 'Onshore Wind',
            'Other biomass (2)'  : 'Other biomass',
            'Other biomass (inc. co-firing) (4)'  : 'Other biomass (inc. co-firing)',
            'Other biomass (inc. co-firing) (5,6)'  : 'Other biomass (inc. co-firing)',
            'Plant Biomass (3)'  : 'Plant Biomass',
            'Plant Biomass (3,6)'  : 'Plant Biomass',
            'Sewage sludge digestion (5)'  : 'Sewage sludge digestion',
            'Sewage sludge digestion (6)'  : 'Sewage sludge digestion',
            'Shoreline wave / tidal' : 'Shoreline Wave and Tidal',
            'Shoreline wave / tidal (5)'  : 'Shoreline Wave and Tidal',
            'Shoreline wave / tidal (6)'  : 'Shoreline Wave and Tidal',
            'Solar PV (5)'  : 'Solar Photovoltaics',
            'Solar PV'  : 'Solar Photovoltaics',
            'Solar photovoltaics (6)' : 'Solar photovoltaics',
            'TOTAL'  : 'all',
            'TOTAL (excluding co-firing and non-biodegradable wastes)'  : 'all (excluding co-firing and non-biodegradable wastes)',
            'Total' : 'all'},
                'DATAMARKER' : {'-' : 'not-available'},
                'Unit' : {'12' : 'GWh'}})

df


# In[31]:


COLUMNS_TO_NOT_PATHIFY = ['DATAMARKER', 'Geography', 'OBS', 'Period']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err


# In[32]:


df = df.rename(columns={'Category' : 'Fuel', 'Head' : 'Measure Type', 'OBS' : 'Value', 'Geography' : 'Region', 'DATAMARKER' : 'Marker'}).fillna('')

df = df[['Period', 'Region', 'Fuel', 'Value', 'Marker', 'Measure Type', 'Unit']]

df['Unit'] = df.apply(lambda x: 'percent' if 'load-factors' in x['Measure Type'] else x['Unit'], axis = 1)

df


# In[33]:


cubes.add_cube(scraper, df, scraper.title)

cubes.output_all()


# In[34]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


