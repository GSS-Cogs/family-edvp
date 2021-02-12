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

# +
import json

import pandas as pd

from gssutils import *

# +
infoFileName = 'info.json'
 
info    = json.load(open(infoFileName))
scraper = Scraper(seed=infoFileName)
cubes   = Cubes(infoFileName)
distro  = scraper.distribution(latest=True, title=lambda t: 'Renewable electricity capacity and generation (ET 6.1 - quarterly)' in t)
# -

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
    geog = 'K02000001'
    
    if 'Annual' in [x.strip() for x in name.split('-')]:
        years = tab.excel_ref('B6').expand(RIGHT)
    else:
        years = tab.excel_ref('B5').expand(RIGHT)
        qrtrs = tab.excel_ref('B6').expand(RIGHT)
    heads = tab.excel_ref('A7') | tab.excel_ref('A23') | tab.excel_ref('A39') | tab.excel_ref('A52')
    cats = tab.excel_ref('A7').expand(DOWN) - heads
    data = tab.excel_ref('E8').expand(DOWN).expand(RIGHT)

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

    obvs = years.waffle(cats).is_not_blank()

    return ConversionSegment(tab, dims, obvs).topandas()


def et61_nat(name, tab) -> pd.DataFrame():
    geog = nations[tab.name.split('-')[0].strip()]

    if 'Annual' in [x.strip() for x in name.split('-')]:
        years = tab.excel_ref('B6').expand(RIGHT)
    else:
        years = tab.excel_ref('B5').expand(RIGHT)
        qrtrs = tab.excel_ref('B6').expand(RIGHT)
    heads = tab.excel_ref('A7') | tab.excel_ref('A22') | tab.excel_ref('A33')
    cats = tab.excel_ref('A7').expand(DOWN) - heads
    data = tab.excel_ref('E8').expand(DOWN).expand(RIGHT)

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

    obvs = years.waffle(cats).is_not_blank()

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

# So we're going to assign as described and verified above
df['DATAMARKER'], df['Unit'] = extract[0], extract[1]

# Next, strip these values from Head
df['Head'] = df['Head'].str.replace(r'\([^)]*\)', '').str.strip()

# Date formatting
df.loc[df['Quarter'].isna(),'Period'] = df['Year'].apply(lambda x : f"/id/year/{x[:4]}")
df.loc[~df['Quarter'].isna(), 'Period'] = df.loc[~df['Quarter'].isna(), ['Year', 'Quarter']].apply(lambda x : f"/id/quarter/{x[0][:4]}-{x[1][:1]}", axis=1)
df.drop(['Year', 'Quarter'], axis=1, inplace=True)

cubes.add_cube(scraper, df, scraper.title)

cubes.output_all()


