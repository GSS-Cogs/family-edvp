#!/usr/bin/env python
# coding: utf-8

# In[612]:


from gssutils import *
import json
import re

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

info = json.load(open('info.json'))


# In[613]:


scraper = Scraper(info['landingPage'])
scraper.dataset.family = 'energy'
scraper


# In[614]:


dist = [x for x in scraper.distributions if "Liquid biofuels" in x.title][0]

display(dist)


# In[615]:


tabs = [x for x in dist.as_databaker() if x.name not in ['Contents', 'Highlights']] #
#tabs


# In[616]:


tidied_sheets = {}

for tab in tabs:

    if tab.name in ['Annual', 'Quarter']:#, 'Main table']: Main table is just data from annual and quarter

        print(tab.name)

        pivot = tab.filter('VOLUME (million litres)')

        year = pivot.fill(RIGHT).is_not_blank() - tab.filter(contains_string('per cent change'))
        quarter = year #they joined the cells rather than having year above quarter smh

        measure = pivot.expand(DOWN).filter(contains_string('VOLUME')) | pivot.expand(DOWN).filter(contains_string('ENERGY')) | pivot.expand(DOWN).filter(contains_string('volume')) 

        fuel = pivot.fill(DOWN).is_not_blank() - measure

        observations = (fuel.fill(RIGHT).is_not_blank() - measure.expand(RIGHT) - tab.filter(contains_string('per cent change')).fill(DOWN)) - (tab.filter('VOLUME - Per cent changes from same quarter last year (%)').expand(RIGHT).expand(DOWN) - tab.filter('VOLUME - per cent of total biofuels (%)').expand(RIGHT).expand(DOWN)) #this is a terrible way of doing this but finding a better way really isnt worth the time

        dimensions = [
                HDim(year, "Year", DIRECTLY, ABOVE),
                HDim(quarter, "Quarter", DIRECTLY, ABOVE),
                HDim(fuel, 'Fuel', DIRECTLY, LEFT),
                HDim(measure, 'Measure Type', CLOSEST, ABOVE)
        ]


        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname=tab.name + " Preview.html")

        tidied_sheets[tab.name] = tidy_sheet.topandas()


# In[617]:


df = pd.concat(tidied_sheets.values()).fillna('NaN')

df['Year'] = df['Year'].str.lower()

df['Quarter'] = df.apply(lambda x: x['Year'][-11:] if 'quarter' in x['Year'] else x['Year'], axis = 1)
df['Year'] = df.apply(lambda x: x['Year'][:4] if 'quarter' in x['Year'] else x['Year'], axis = 1)

df['Unit'] = df['Measure Type']

df['Unit'] = df.apply(lambda x: 'percent' if '%' in x['Unit'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'million-litres' if 'million litres' in x['Unit'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'thousand-toe' if 'ktoe' in x['Unit'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'percent' if 'Shares' in x['Unit'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'thousand-toe' if 'thousand toe' in x['Unit'] else x['Unit'], axis = 1)

df['Measure Type'] = df['Measure Type'].str.lower()

df = df.replace({'Quarter' : {'1st quarter' : 'Q1',
                              '2nd quarter' : 'Q2',
                              '3rd quarter' : 'Q3',
                              '4th quarter' : 'Q4'}})

                 

df['Period'] = df.apply(lambda x: 'quarter/' + x['Year'][:4] + '-' + x['Quarter'] if 'Q' in x['Quarter'] else 'year/' + x['Year'], axis = 1)

df.drop(['Year', 'Quarter'], axis=1, inplace=True)

df['Measure Type'] = df.apply(lambda x: x['Measure Type'].split('(')[0].strip(), axis = 1)

df = df.replace({'Measure Type' : {'volume - all transport fuels consumption' : 'volume',
                                   'volume - per cent of total biofuels' : 'volume of total biofuels'}})

df = df.rename(columns={'OBS' : 'Value'})

df = df[['Period', 'Fuel', 'Value', 'Measure Type', 'Unit']]

df['Measure Type'] = df['Measure Type'].apply(pathify)

df


# In[618]:


scraper.dataset.title = info['title']

scraper.dataset.comment = """
Data on UK liquid biofuels for transport consumption. Quarterly data published a quarter in arrears with detailed commentary available in the BEIS statistical publication Energy Trends.
https://www.uktradeinfo.com/Statistics/Pages/TaxAndDutybulletins.aspx
Percentage change on Quarter observations is % change on quarter in previous year (-ve value is decrease)
"""
scraper.dataset.contactPoint = "renewablesstatistics@beis.gov.uk"


# In[619]:


df.to_csv('observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')


# In[620]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)

