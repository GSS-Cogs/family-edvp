#!/usr/bin/env python
# coding: utf-8

# In[209]:



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


# In[210]:


scraper = Scraper(info['landingPage'])
scraper.dataset.family = 'energy'
scraper


# In[211]:


dist = [x for x in scraper.distributions if "Fuel used in generation (DUKES 5.3)" in x.title][0]

display(dist)


# In[212]:


tabs = [x for x in dist.as_databaker() if x.name not in ['Contents']]

tidied_sheets = {}

for tab in tabs:

    if tab.name in ['5.3']:

        print(tab.name)

        remove = tab.filter('Total all generating companies').shift(DOWN).expand(RIGHT).expand(DOWN)

        pivot = tab.filter(contains_string('5.3')) - remove

        fuel = pivot.fill(DOWN).is_not_blank() - remove

        period = tab.filter('Unit').fill(RIGHT).is_not_blank()

        observations = fuel.fill(RIGHT).is_not_blank() - tab.filter(contains_string('oil')) - tab.filter('Unit').expand(DOWN)

        generators = pivot.fill(DOWN).is_not_blank() - remove - observations.expand(LEFT)

        unit = tab.filter('Unit').expand(DOWN).is_not_blank() | tab.filter('Original units of measurement').expand(DOWN).is_not_blank() - observations

        dimensions = [
                HDim(period, 'Period', DIRECTLY, ABOVE),
                HDim(fuel, 'Fuel', DIRECTLY, LEFT),
                HDim(generators, 'Generating Companies', CLOSEST, ABOVE),
                HDim(unit, 'Unit', CLOSEST, ABOVE, cellvalueoverride={'    "' : 'M tonnes'})
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets[tab.name] = tidy_sheet.topandas()


# In[213]:


df = pd.concat([tidied_sheets['5.3']]).fillna('NaN')

df['Period'] = df.apply(lambda x: 'year/' + left(x['Period'], 4), axis = 1)

df = df.replace({'Fuel' : {
        '                 combined cycle gas turbine stations' : 'combined cycle gas turbine stations',
        'Coal (5)' : 'Coal including coke oven coke', #(5) Includes coke oven coke.
        'Gas (4)' : 'Gas including refinery gas', #(4) Includes refinery gas.
        'Gas (6)' : 'Gas including colliery methane', #(6) Includes colliery methane.
        'Hydro (natural flow) (7)' : 'Hydro (natural flow)',
        'Of which: conventional thermal and other stations (9)' : 'conventional thermal and other stations', #(9) Includes gas turbines, oil engines, coal and plants producing electricity from renewable sources other than hydro. Excludes nuclear.
        'Oil (3)' : 'Oil including orimulsion', #(3) Includes orimulsion, oil used in gas turbine and diesel plant, and oil used for lighting up coal fired boilers.
        'Oil (3)(4)' : 'Oil including orimulsion and refinery gas',
        'Oil (4)' : 'Oil including refinery gas',
        'Other fuels (8)' : 'Other fuels',
        'Other renewables (7)' : 'Other renewables',
        'Total all generating companies' : 'All',
        'Total major power producers (2)' : 'All',
        'Total other generators (2)' : 'All'},
                'Generating Companies' : {
        'Major power producers (2)' : 'Major power producers',
        'Transport undertakings:' : 'Other generators - Transport Undertakings',
        'Undertakings in industrial and commercial sectors:' : 'Other generators - Undertakings in industrial and commercial sectors'},
                'Unit' : {
        'M tonnes' : 'Millions of Tonnes'}})

df = df.rename(columns={'OBS' : 'Value'})

df['Measure Type'] = df.apply(lambda x: 'fuel used in generation - representative' if 'equivalent' in x['Unit'] else 'fuel used in generation', axis = 1)

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df[['Period', 'Generating Companies', 'Fuel', 'Value', 'Measure Type', 'Unit']]

df


# In[214]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[215]:


scraper.dataset.title = info['title']

scraper.dataset.comment = """
Data on the UK\u2019s renewables sector. These tables focus on  liquid biofuels consumption.\nPublished quarterly on the last Thursday of each calendar quarter (March, June, September and December). The data is a quarter in arrears.
For Major Power Producers, 'other fuels' only includes non-biodegradable waste. This was included in 'other renewables'  prior
to 2013. For 'other generators', 'other fuels' includes mainly non-biodegradable waste, coke oven gas, blast furnace gas, and waste
products from chemical processes. Non-biodegradable waste was included in 'other renewables' prior to 2007."""

cubes.add_cube(scraper, df.drop_duplicates(), scraper.title)


# In[216]:


cubes.output_all()

