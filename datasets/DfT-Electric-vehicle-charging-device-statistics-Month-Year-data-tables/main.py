#!/usr/bin/env python
# coding: utf-8

# In[12]:


from IPython.display import display

from gssutils import *
import json

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

scraper = Scraper("https://www.gov.uk/government/statistics/electric-vehicle-charging-device-statistics-january-2021")
#Collections landing page doesnt pick up any distributions, will need to update the scraper to pick up new releases without manual input
scraper



# In[13]:




for i in scraper.distributions:
    display(i)



# In[14]:



tabs = [x for x in scraper.distributions[1].as_databaker() if "Info" not in x.name] #

tidied_sheets = {}

for tab in tabs:

    if '01' in tab.name:

        print(tab.name)

        pivot = tab.filter('Department for Transport statistics')

        remove = tab.filter("Notes").expand(RIGHT).expand(DOWN)

        LA = pivot.shift(0, 6).fill(DOWN).is_not_blank() - remove

        period = pivot.shift(2,6).expand(RIGHT).is_not_blank()

        measure = pivot.shift(2, 7).expand(RIGHT).is_not_blank()

        observations = LA.shift(2, 0).expand(RIGHT).is_not_blank() - remove

        if tab.name in ['EVCD_01a']:
            chargeType = 'all speeds'
        elif tab.name in ['EVCD_01b']:
            chargeType = 'rapid'

        dimensions = [
                HDim(period, "Period", CLOSEST, LEFT),
                HDim(LA, 'Area', DIRECTLY, LEFT),
                HDim(measure, 'Measure Type', DIRECTLY, ABOVE),
                HDimConst('Charge Type', chargeType)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname = tab.name + "-Preview.html")

        tidied_sheets[tab.name] = tidy_sheet.topandas()

    if '02Exclude' in tab.name:

        #data in this tab is either incorrect or has been a result in change in methodology, is being looked into

        print(tab.name)

        pivot = tab.filter('Department for Transport statistics')

        remove = tab.filter("Notes").expand(RIGHT).expand(DOWN)

        year = pivot.shift(0, 6).fill(DOWN).is_not_blank() - remove

        quarter = pivot.shift(1, 6).fill(DOWN).is_not_blank() - remove

        measure = pivot.shift(2, 6).expand(RIGHT).is_not_blank()

        observations = quarter.shift(RIGHT).expand(RIGHT).is_not_blank() - remove

        dimensions = [
                HDim(year, 'Period', CLOSEST, ABOVE),
                HDim(quarter, 'Quarter', DIRECTLY, LEFT),
                HDimConst('Area', 'K02000001'),
                HDim(measure, 'Measure Type', DIRECTLY, ABOVE)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname = tab.name + "-Preview.html")

        tidied_sheets[tab.name] = tidy_sheet.topandas()


# In[ ]:



df = pd.concat(tidied_sheets.values(), sort = True).fillna('NaN')

df['Quarter'] = df.apply(lambda x: mid(x['Period'], 5, 5) if '-' in x['Period'] else x['Quarter'], axis = 1)
df['Period'] = df.apply(lambda x: left(x['Period'], 4), axis = 1)
df = df.replace({'January': 'Q1',
                 'April': 'Q2',
                 'July': 'Q3',
                 'October': 'Q4',
                 '01-01' : 'Q1',
                 '04-01' : 'Q2',
                 '07-01' : 'Q3',
                 '10-01' : 'Q4'}, regex=True)

df['Period'] = df.apply(lambda x: 'quarter/' + x['Period'] + '-' + x['Quarter'], axis = 1)

df['Measure Type'] = df.apply(lambda x: x['Measure Type'].replace("\n", " "), axis = 1)

df['Measure Type'] = df.apply(lambda x: 'Rapid Devices ' + x['Measure Type'] if 'rapid' in x['Charge Type'] and '100' in x['Measure Type'] else ('Total Devices ' + x['Measure Type'] if 'all speeds' in x['Charge Type'] and '100' in x['Measure Type'] else x['Measure Type']), axis = 1)

df['Unit'] = 'Electric Vehicle Charging Platform'
df['OBS'] = df.apply(lambda x: "{:.2f}".format(x['OBS']), axis = 1)

df = df.rename(columns={'OBS' : 'Value', 'Area' : 'Region'})

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period', 'Region']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df.replace({'Measure Type' : {'total-public-charging-devices' : 'total-devices',
                                   'total-public-rapid-charging-devices' : 'rapid-devices',
                                   'charging-devices-per-100-000-population' : 'total-devices-per-100-000-population'}})

df = df[['Period', 'Region', 'Value', 'Measure Type', 'Unit']]

df


# In[15]:





scraper.dataset.family = 'edvp'
scraper.dataset.comment = """
Charging device location data is sourced from the electric vehicle charging platform Zap-map and represents devices reported as operational at midnight, 1 October 2020.
‘Total devices’ represent publicly available charging devices at all speeds. ‘Rapid devices’ are those whose fastest connector is rated at 43kW or above. A device can have a number of connectors of varying speeds.
"""
scraper.dataset.contactPoint = "environment.stats@dft.gov.uk"

df.to_csv('observations.csv', index=False)

df


# In[ ]:


catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

