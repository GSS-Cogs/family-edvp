#!/usr/bin/env python
# coding: utf-8

# In[1]:


from gssutils import *
import json
import re
from datetime import date

scraper = Scraper(seed="info.json")
scraper.dataset.issued = '2020-12-08'
scraper.dataset.modified = date.today() #Dataset is updated daily

distro  = scraper.distribution(latest=True, mediaType='text/csv')
distro


# In[2]:


df = distro.as_pandas()#encoding='cp1252'

df = pd.melt(df, id_vars = ['Settlement_Date'], var_name = "Measure Type", value_name = "Value")

df['Unit'] = df['Measure Type']

df = df.replace({'Unit' : {
        'Actual_Eligible_Demand_MWh' : 'MWh',
        'Actual_EII_Excluded_Electricity_MWh' : 'MWh',
        'Actual_Gross_Demand_MWh' : 'MWh',
        'Actual_ILR_GBP_Per_MWh' : 'GBP Per MWh',
        'Actual_Income_GBP' : 'GBP'},
                'Measure Type' : {
        'Actual_Eligible_Demand_MWh' : 'Actual Eligible Demand',
        'Actual_EII_Excluded_Electricity_MWh' : 'Actual EII Excluded Electricity',
        'Actual_Gross_Demand_MWh' : 'Actual Gross Demand',
        'Actual_ILR_GBP_Per_MWh' : 'Actual ILR',
        'Actual_Income_GBP' : 'Actual Income'
}})

df = df.rename(columns={'Settlement_Date' : 'Period'})

df['Period'] = df.apply(lambda x: 'day/' + x['Period'], axis = 1)

df = df[['Period', 'Value', 'Measure Type', 'Unit']].fillna('NaN')

indexNames = df[ df['Value'] == 'NaN' ].index
df.drop(indexNames, inplace = True)

"""COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err"""

scraper.dataset.comment = """
Actual EII_Excluded Electricity (MWh) :	Supplier's Daily Energy Intensive Industries demand which is being exempted from paying CfD levy
Actual Eligible Demand (MWh) :  Gross Demand less both Energy Intensive Industries demand and Green Excluded Electricity demand
Actual Gross Demand (MWh) :	The volume of Active Import (i.e. electrical energy entering premises from the licensed distribution or transmission network), with no adjustment made for any Active Export (i.e. electrical energy generated on the premises and exported onto the licensed distribution or transmission network)
Actual ILR (£/MWh) : Under the Supplier Obligation Levy, electricity suppliers make pre-payments consisting of a unit cost fixed Interim Levy Rate, charged at a daily £/MWh rate to fund the cost of CfD generation payments. The Interim Levy Rate is set by LCCC every quarter, one quarter in advance, based on an estimate of the payments that will need to be made in respect of CfD generation in that quarter
Actual Income (£) :	Actual Income from electricity suppliers based on Actual Eligible Demand multiplied by Interim Levy Rate
Period : The date on which energy is deemed to be used and must be later settled through BSC initial settlement/reconciliation or Scottish Settlements. Also known as the Trading Day
"""
df.to_csv('observations.csv', index=False)

df


# In[3]:


catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

