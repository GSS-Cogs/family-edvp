#!/usr/bin/env python
# coding: utf-8

# In[626]:





# In[627]:



from gssutils import *
import json
import re

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

cubes = Cubes("info.json")
info = json.load(open('info.json'))


# In[628]:


scraper = Scraper(info['landingPage'])
scraper.dataset.family = 'energy'
scraper


# In[629]:


dist = [x for x in scraper.distributions if "Liquid biofuels" in x.title][0]

display(dist)


# In[630]:


tabs = [x for x in dist.as_databaker() if x.name not in ['Contents', 'Highlights']] #
tabs


# In[631]:


tidied_sheets = {}

for tab in tabs:

    if tab.name in ['Annual', 'Quarter']:

        print(tab.name)

        pivot = tab.filter('6 RENEWABLES')

        if tab.name == 'Annual':
            remove = tab.filter(contains_string("Source:")).expand(RIGHT).expand(DOWN)
        elif tab.name == 'Quarter':
            remove = tab.filter(contains_string("Source:")).expand(RIGHT).expand(DOWN) | tab.filter(contains_string('%')).expand(DOWN)

        fuel = tab.filter('VOLUME (million litres)').fill(DOWN) - tab.filter('ENERGY (thousand toe)') - remove

        if tab.name == 'Annual':
            period = tab.filter('VOLUME (million litres)').shift(1, -1).expand(RIGHT).is_not_blank()
        elif tab.name == 'Quarter':
            year = tab.filter('VOLUME (million litres)').shift(1, -2).expand(RIGHT).is_not_blank()
            quarter = year.shift(DOWN)

        measure = tab.filter('VOLUME (million litres)') | tab.filter('ENERGY (thousand toe)')

        observations = fuel.fill(RIGHT).is_not_blank()

        if tab.name == 'Annual':
            dimensions = [
                    HDim(period, "Period", DIRECTLY, ABOVE),
                    HDim(fuel, 'Fuel', DIRECTLY, LEFT),
                    HDim(measure, 'Measure Type', CLOSEST, ABOVE),
                    HDim(measure, 'Unit', CLOSEST, ABOVE)
            ]
        elif tab.name == 'Quarter':
            dimensions = [
                    HDim(year, "Year", DIRECTLY, ABOVE),
                    HDim(quarter, "Quarter", DIRECTLY, ABOVE),
                    HDim(fuel, 'Fuel', DIRECTLY, LEFT),
                    HDim(measure, 'Measure Type', CLOSEST, ABOVE),
                    HDim(measure, 'Unit', CLOSEST, ABOVE)
            ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets[tab.name] = tidy_sheet.topandas()

    elif tab.name in ['Main table']:

        print(tab.name)

        pivot = tab.filter('6 RENEWABLES')

        remove = tab.filter(contains_string("1.")).expand(RIGHT).expand(DOWN) | tab.filter(contains_string('Total biofuels for transport')).expand(UP) | tab.filter(contains_string('per cent change')).expand(DOWN)

        fuel = tab.filter('Shares of road fuels').fill(DOWN) - remove

        year = tab.filter('VOLUME (million litres)').shift(1, -2).expand(RIGHT).is_not_blank()
        quarter = year.shift(DOWN)
        yearAdd = tab.filter('VOLUME (million litres)').shift(1, -1).expand(RIGHT).is_not_blank() - quarter
        year = (yearAdd | year) - remove
        quarter = quarter | yearAdd.shift(UP)

        measure = tab.filter('Shares of road fuels') | tab.filter('Percentage change in shares of road fuels (2)')

        unit = 'Percent'

        observations = fuel.fill(RIGHT).is_not_blank() - remove - measure.expand(RIGHT)

        dimensions = [
                HDim(year, "Year", DIRECTLY, ABOVE),
                HDim(quarter, "Quarter", DIRECTLY, ABOVE),
                HDim(fuel, 'Fuel', DIRECTLY, LEFT),
                HDim(measure, 'Measure Type', CLOSEST, ABOVE),
                HDimConst('Unit', unit)
        ]


        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets[tab.name] = tidy_sheet.topandas()



# In[632]:


df = pd.concat([tidied_sheets['Annual'], tidied_sheets['Quarter']]).fillna('NaN')

df['Period'] = df.apply(lambda x: 'Quarter/' + left(x['Year'], 4) +'-Q'+ left(x['Quarter'], 1) if x['Period'] == 'NaN' else 'Year/' + left(x['Period'], 4), axis = 1)

df = df.drop(['Quarter', 'Year'], axis=1)

df['Measure Type'] = df.apply(lambda x: x['Measure Type'].split('(')[0].strip(), axis = 1)
df['Unit'] = df.apply(lambda x: left(x['Unit'].split('(')[1], len(x['Unit'].split('(')[1]) - 1).strip(), axis = 1)

df = df.replace({'Fuel' : {'Total biofuels for transport' : 'Total Biofuels'}})

df = df.rename(columns={'OBS' : 'Value'})

df = df[['Period', 'Fuel', 'Value', 'Measure Type', 'Unit']]

df


# In[633]:


dfShares = pd.concat([tidied_sheets['Main table']]).fillna('NaN')

dfShares['Period'] = dfShares.apply(lambda x: 'Quarter/' + left(x['Year'], 4) +'-Q'+ left(x['Quarter'], 1) if x['Quarter'] != '' else 'Year/' + left(x['Year'], 4), axis = 1)

dfShares = dfShares.drop(['Quarter', 'Year'], axis=1)

dfShares['Measure Type'] = dfShares.apply(lambda x: x['Measure Type'] + 'Motor Spirit' if 'Motor Spirit' in x['Fuel'] else (x['Measure Type'] + 'DERV' if 'DERV' in x['Fuel'] else x['Measure Type']), axis = 1)

dfShares['Fuel'] = dfShares.apply(lambda x: x['Fuel'].split('as')[0].strip(), axis = 1)

dfShares = dfShares.replace({'Measure Type' : {
    'Percentage change in shares of road fuels (2)Motor Spirit' : 'Percentage change in shares of Motor Spirit road fuels',
    'Percentage change in shares of road fuels (2)DERV' : 'Percentage change in shares of DERV road fuels',
    'Shares of road fuelsDERV' : 'Shares of DERV road fuels',
    'Shares of road fuelsMotor Spirit' : 'Shares of Motor Spirit road fuels',
    'Percentage change in shares of road fuels (2)' : 'Percentage change in shares of road fuels'
}})

dfShares = dfShares.rename(columns={'OBS' : 'Value'})

dfShares = dfShares[['Period', 'Fuel', 'Value', 'Measure Type', 'Unit']]

dfShares


# In[634]:


df = pd.concat([df, dfShares])

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df


# In[635]:


scraper.dataset.family = 'edvp'
scraper.dataset.comment = """
Data on UK liquid biofuels for transport consumption. Quarterly data published a quarter in arrears with detailed commentary available in the BEIS statistical publication Energy Trends.
https://www.uktradeinfo.com/Statistics/Pages/TaxAndDutybulletins.aspx
Percentage change on Quarter observations is % change on quarter in previous year (-ve value is decrease)
"""
scraper.dataset.contactPoint = "renewablesstatistics@beis.gov.uk"

csvName = 'observations'
cubes.add_cube(scraper, df.drop_duplicates(), csvName)


# In[636]:


cubes.output_all()

