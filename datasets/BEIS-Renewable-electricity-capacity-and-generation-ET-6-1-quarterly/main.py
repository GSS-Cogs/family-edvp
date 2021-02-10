# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
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
# so the tabs we want end are the only ones which end with r

# Generate a dictionary of the tab name with the databaker contents as the value
tabs = {x.name: x for x in tabs if x.name.endswith("r")}

nations = {
    'England': 'E92000001',
    'Northern Ireland': 'N92000002',
    'Scotland': 'S92000003',
    'Wales': 'W92000004'
}


def et61_all(tab) -> pd.DataFrame():
    geog = 'K02000001'
    
    years = tab.excel_ref('B5').expand(RIGHT)
    qrtrs = tab.excel_ref('B6').expand(RIGHT)
    heads = tab.excel_ref('A7') | tab.excel_ref('A23') | tab.excel_ref('A39') | tab.excel_ref('A52')
    cats = tab.excel_ref('A7').expand(DOWN) - heads
    data = tab.excel_ref('E8').expand(DOWN).expand(RIGHT)

    dims = [
    HDim(years, 'Year', DIRECTLY, ABOVE),
    HDim(qrtrs, 'Quarter', DIRECTLY, ABOVE),
    HDim(heads, 'Head', CLOSEST, ABOVE),
    HDim(cats, 'Category', DIRECTLY, LEFT),
    HDimConst('Geography', geog)
    ]

    obvs = qrtrs.waffle(cats).is_not_blank()

    return ConversionSegment(tab, dims, obvs).topandas()


def et61_nat(tab) -> pd.DataFrame():
    geog = nations[tab.name.split(' - ')[0]]

    years = tab.excel_ref('B5').expand(RIGHT)
    qrtrs = tab.excel_ref('B6').expand(RIGHT)
    heads = tab.excel_ref('A7') | tab.excel_ref('A22') | tab.excel_ref('A33')
    cats = tab.excel_ref('A7').expand(DOWN) - heads
    data = tab.excel_ref('E8').expand(DOWN).expand(RIGHT)

    dims = [
        HDim(years, 'Year', DIRECTLY, ABOVE),
        HDim(qrtrs, 'Quarter', DIRECTLY, ABOVE),
        HDim(heads, 'Head', CLOSEST, ABOVE),
        HDim(cats, 'Category', DIRECTLY, LEFT),
        HDimConst('Geography', geog)
    ]

    obvs = qrtrs.waffle(cats).is_not_blank()

    return ConversionSegment(tab, dims, obvs).topandas()


df = pd.DataFrame()

for name, tab in tabs.items():
    if name == 'Quarter':
        df = pd.concat([df, et61_all(tab)], axis=0)
    else:
        df = pd.concat([df, et61_nat(tab)], axis=0)


df = df[df['Category'] != 'Days in quarter']

df['Period'] = df[['Year', 'Quarter']].apply(lambda x : f"/id/quarter/{x[0][:4]}-{x[1][:1]}", axis =1)
df.drop(['Year', 'Quarter'], axis=1, inplace=True)

cubes.add_cube(scraper, df, scraper.title)

cubes.output_all()


