#!/usr/bin/env python
# coding: utf-8

# In[143]:



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


# In[144]:


scraper = Scraper(info['landingPage'])
scraper.dataset.family = 'edvp'
scraper


# In[145]:


dist = [x for x in scraper.distributions if "Fuel used in generation (DUKES 5.3)" in x.title][0]

display(dist)


# In[146]:


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
                HDimConst('Measure Type', 'Fuel used in Generation'),
                HDim(unit, 'Unit', CLOSEST, ABOVE, cellvalueoverride={'    "' : 'M tonnes'})
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets[tab.name] = tidy_sheet.topandas()


# In[147]:


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

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err


df


# In[148]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[149]:


dfOil, dfActual = [x for _, x in df.groupby(df['Unit'] != 'millions-of-tonnes-of-oil-equivalent')]

scraper.comments = """
For Major Power Producers, 'other fuels' only includes non-biodegradable waste. This was included in 'other renewables'  prior
to 2013. For 'other generators', 'other fuels' includes mainly non-biodegradable waste, coke oven gas, blast furnace gas, and waste
products from chemical processes. Non-biodegradable waste was included in 'other renewables' prior to 2007."""

scraper.dataset.title = "Fuel used in generation (DUKES 5.3) - Oil Equivalent Values"
scraper.dataset.description = "Digest of UK Energy Statistics (DUKES): electricity. DUKES chapter 5: statistics on electricity from generation through to sales. Measure as an equivalent to Oil"
cubes.add_cube(scraper, dfOil.drop_duplicates(), scraper.title)

scraper.dataset.title = "Fuel used in generation (DUKES 5.3)"
cubes.add_cube(scraper, dfActual.drop_duplicates(), scraper.title)


# In[150]:


cubes.output_all()

