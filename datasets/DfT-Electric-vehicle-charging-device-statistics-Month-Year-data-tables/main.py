#!/usr/bin/env python
# coding: utf-8

# In[122]:



from gssutils import *
import json

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

cubes = Cubes("info.json")
info = json.load(open('info.json'))


# In[123]:


scraper = Scraper("https://www.gov.uk/government/statistics/electric-vehicle-charging-device-statistics-october-2020")
scraper


# In[124]:


for i in scraper.distributions:
    display(i)


# In[125]:


tabs = [x for x in scraper.distributions[1].as_databaker() if "Info" not in x.name] #
tabs


# In[126]:


tidied_sheets = {}

for tab in tabs:

    if '01' in tab.name:

        print(tab.name)

        pivot = tab.filter('Department for Transport statistics')

        remove = tab.filter("Notes").expand(RIGHT).expand(DOWN)

        LA = pivot.shift(0, 6).fill(DOWN).is_not_blank() - remove

        measure = pivot.shift(2, 6).expand(RIGHT).is_not_blank()

        observations = LA.shift(2, 0).expand(RIGHT).is_not_blank() - remove

        dimensions = [
                HDimConst("Period", "2020.0"),
                HDim(LA, 'Area', DIRECTLY, LEFT),
                HDim(measure, 'Measure Type', DIRECTLY, ABOVE)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets[tab.name] = tidy_sheet.topandas()

    if '02' in tab.name:

        print(tab.name)

        pivot = tab.filter('Department for Transport statistics')

        remove = tab.filter("Notes").expand(RIGHT).expand(DOWN)

        year = pivot.shift(0, 6).fill(DOWN).is_not_blank() - remove

        quarter = year.shift(RIGHT)

        measure = pivot.shift(2, 6).expand(RIGHT).is_not_blank()

        observations = year.shift(2, 0).expand(RIGHT).is_not_blank() - remove

        dimensions = [
                HDim(year, 'Period', DIRECTLY, LEFT),
                HDim(quarter, 'Quarter', DIRECTLY, LEFT),
                HDimConst('Area', 'K02000001'),
                HDim(measure, 'Measure Type', DIRECTLY, ABOVE)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets[tab.name] = tidy_sheet.topandas()


# In[127]:


df = pd.concat(tidied_sheets.values()).fillna('NaN')

df['Period'] = df.apply(lambda x: 'year/' + left(x['Period'], 4) if 'NaN' in x['Quarter'] else 'quarter/'+left(x['Period'], 4)+'-'+x['Quarter'], axis = 1)

df['Measure Type'] = df.apply(lambda x: x['Measure Type'].replace("\n", " "), axis = 1)
df['Unit'] = 'Electric Vehicle Charging Platform'
#df['Charge Type'] = df.apply(lambda x: 'Rapid' if 'rapid' in x['Measure Type'].lower() else 'all', axis = 1)
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


# In[128]:


scraper.dataset.family = 'edvp'
scraper.dataset.comment = """
Charging device location data is sourced from the electric vehicle charging platform Zap-map and represents devices reported as operational at midnight, 1 October 2020.
‘Total devices’ represent publicly available charging devices at all speeds. ‘Rapid devices’ are those whose fastest connector is rated at 43kW or above. A device can have a number of connectors of varying speeds.
"""
scraper.dataset.contactPoint = "environment.stats@dft.gov.uk"

csvName = 'observations'
cubes.add_cube(scraper, df.drop_duplicates(), csvName)


# In[129]:


cubes.output_all()


# In[130]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[131]:


import pandas as pd
df = pd.read_csv("out/observations.csv")
df["all_dimensions_concatenated"] = ""
for col in df.columns.values:
    if col != "Value":
        df["all_dimensions_concatenated"] = df["all_dimensions_concatenated"]+df[col].astype(str)
found = []
bad_combos = []
for item in df["all_dimensions_concatenated"]:
    if item not in found:
        found.append(item)
    else:
        bad_combos.append(item)
df = df[df["all_dimensions_concatenated"].map(lambda x: x in bad_combos)]
drop_these_cols = []
for col in df.columns.values:
    if col != "all_dimensions_concatenated" and col != "Value":
        drop_these_cols.append(col)
for dtc in drop_these_cols:
    df = df.drop(dtc, axis=1)
df = df[["all_dimensions_concatenated", "Value"]]
df = df.sort_values(by=['all_dimensions_concatenated'])
df.to_csv("duplicates_with_values.csv", index=False)
# Find duplicates

