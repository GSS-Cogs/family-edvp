#!/usr/bin/env python
# coding: utf-8

# In[583]:


# -*- coding: utf-8 -*-
# # Documentation
#
# There's a lof of tables here but they fall into one of two patterns.
#
# What I'm calling the "small" table:
#
# ![Small Table](./docs/small_table.png)
#
# And what I'm calling the "Big Table"
#
# ![Big Table](./docs/big_table.png)
#
# They always have a differentiating dimension down the left, each "table style" always has the same headers, the key difference is that **sub field of "Not Fuel Poor" / "Fuel Poor"** in the big style table.
#
# # What needs doing?
#
# * Fill out the argument definitions based on Leighs spec.md (you can use the supplementary tables pipeline to get the idea). I've titled the right bit of the notebook appropriately.
# * do the above incrementally, add a tab - see if it works. Havn't proerly finished the "process_big_table" code btw, it aint working at the moment, don't know why but I'd start with getting things working with the one "Argument definition" already in place and build from there.
# note -  as you add more argument dicts (and populate more than just the eneergy efficiency arguments), you'll need to turn them on via this bit (later on):
# ```python
# for category, dataset_task in {
#     "Energy Efficiency": energy_efficiency_task
#     }.items():
# ```
# * there is a section for CSVW Mapping, flagged off, I'd also leave Leigh to decide if he wants to use it.
# * there's a final bit at the end called "Metadata & Joins", at that point in the run we'll have all the dataframes (one for each measure of each table of each tab) in memory. The "table_joins" dict defines what get's joined to what and with which comments etc. You should be able to get the details from the spec.md for this pipeline and the gist of what we're after from the supplementary tables example: https://github.com/GSS-Cogs/family-edvp/blob/main/datasets/BEIS-Fuel-poverty-supplementary-tables-2020/main.py
#


# In[584]:


from gssutils import *
import json
import re
import csv
from template import generate_codelist_from_template
import copy

coldef = json.load(open('info.json'))
etl_title = coldef["title"]
etl_publisher = coldef["publisher"]
print("Publisher: " + etl_publisher)
print("Title: " + etl_title)

coldef['landingPage'] = "https://www.gov.uk/government/statistics/fuel-poverty-detailed-tables-2021"

with open('info.json', 'w') as outfile:
    json.dump(coldef, outfile, indent= 4 )

# Scraper needs updating as it currently doesn't look into each release of the publication, so it needs to be fed the release itself
# Needs to be updated to look in each and return distributions for each


# In[585]:


# # Helpers
#
# This is where most of the magic happens:
#
# * **process_big_table** - processes big style table(s) from a tab
# * **process_little_table** - processes little style table(s) from a tab
# * **clean_lower_tables** - remove everything below the "sub table" you happend to be looking at
# * **generate_codelist** - is there if Leigh needs it but is flagged off (leave it off).
# * **LookupFromDict** - needs replacing, as pandas should be able to just do that
#
# There is mess here, it will be a faffy task, but hopefully things will more or less work as intended.


# In[586]:


def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

def colnum_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def cellCont(cell):
    return re.findall(r"'([^']*)'", str(cell))[0]

def table_one_transform(anchor, task):

    """
    Table 1 has a different vertical dimension on each of the 2 tables on the Tab which made it a pain in the ass.
    Since I wasnt sure at this point if the little table process was going to be used for anything else I made a new function bespoke for table 1
    rather than cater that one. Its horribly hard coded but its only one tab so hey ho
    """

    #print("Anchor is:", anchor)

    year = "year/"+tab.excel_ref('A1').value.split(",")[-1].strip()

    # Get the obs, we don't want columns f + G
    # TODO - safety to make sure F & G actually are the columns we don't want for a given table
    obs = anchor.shift(DOWN).expand(RIGHT).expand(DOWN).is_not_blank()
    obs = obs - tab.excel_ref('F:G') - tab.excel_ref('B:C')
    obs = clean_lower_tables(obs)

    obs2 = tab.filter("Vulnerable households only").shift(RIGHT).fill(DOWN).fill(RIGHT).is_not_blank()
    obs2 = obs2 - tab.excel_ref('F:G') - tab.excel_ref('B:C')
    obs2 = clean_lower_tables(obs2)

    fuel_attributeA = tab.filter("In fuel poverty").shift(1, 0)
    fuel_attributeB = tab.filter("Not in fuel poverty").shift(1, 0)

    horizontal_dimension = anchor.expand(RIGHT).is_not_blank()

    horizontal_dimension2 = clean_lower_tables(tab.filter("Vulnerable households only").fill(RIGHT))

    dimensions = [
        HDimConst("Year", year),
        HDim(horizontal_dimension, "Category", DIRECTLY, ABOVE),
        HDimConst('Vulnerability', 'T'),
        HDim(fuel_attributeA, 'Households in Fuel Poverty', DIRECTLY, LEFT),
        HDim(fuel_attributeB, 'Households not in Fuel Poverty', CLOSEST, BELOW)
    ]

    dimensions2 = [
        HDimConst("Year", year),
        HDim(horizontal_dimension2, "Category", DIRECTLY, ABOVE),
        HDimConst('Vulnerability', 'Y'),
        HDim(fuel_attributeA, 'Households in Fuel Poverty', DIRECTLY, LEFT),
        HDim(fuel_attributeB, 'Households not in Fuel Poverty', CLOSEST, BELOW)
    ]

    cs = ConversionSegment(obs, dimensions)
    df1 = cs.topandas()

    cs = ConversionSegment(obs2, dimensions2)
    df2 = cs.topandas()

    df = pd.concat([df1, df2])

    # Measure and Unit
    df["Unit"] = df["Category"].apply(LookupFromDict("unit", task["units_map"]))

    df["Measure Type"] = df["Category"].apply(LookupFromDict("measure", task["measures_map"]))

    # Add the constant column
    if "constant_columns" in task["tables"][tab.name].keys():
        for k,v in task["tables"][tab.name]["constant_columns"].items():
            df[k] = v

    # Tidy up
    df = df.rename(columns={"OBS": "Value"})

    return df


def process_little_table(anchor, task):
    """
    Given a single anchoring cell, process the smaller style of the tables
    """

    #print("Anchor is:", anchor)

    year = "year/"+tab.excel_ref('A1').value.split(",")[-1].strip()

    # Get the obs, we don't want columns f + G
    # TODO - safety to make sure F & G actually are the columns we don't want for a given table
    obs = anchor.shift(DOWN).expand(RIGHT).expand(DOWN).is_not_blank()
    obs = obs - tab.excel_ref('F:G')
    obs = clean_lower_tables(obs)

    horizontal_dimension = anchor.expand(RIGHT).is_not_blank()

    # Use an alias to trace the differentiating dimension, as the name may or may not
    # support being set as an attribute

    left_column = anchor.shift(LEFT).fill(DOWN).is_not_blank()
    left_column = clean_lower_tables(left_column)

    measure_type = anchor.fill(RIGHT)

    dimensions = [
        HDimConst("Year", year),
        HDim(horizontal_dimension, "Category", DIRECTLY, ABOVE),
        HDim(left_column, task["tables"][tab.name]["differentiating_dimension"], DIRECTLY, LEFT)
    ]

    cs = ConversionSegment(obs, dimensions)
    #savepreviewhtml(cs, fname="Preview.html")
    df = cs.topandas()

    # Measure and Unit
    df["Unit"] = df["Category"].apply(LookupFromDict("unit", task["units_map"]))

    df["Measure Type"] = df["Category"].apply(LookupFromDict("measure", task["measures_map"]))

    # Add the constant column
    if "constant_columns" in task["tables"][tab.name].keys():
        for k,v in task["tables"][tab.name]["constant_columns"].items():
            df[k] = v

    # Tidy up
    df = df.rename(columns={"OBS": "Value"})

    return df

def process_big_table(anchor, task):

    """
    Given a single anchoring cell, process the bigger style of the tables
    """
    year = "year/"+tab.excel_ref('A1').value.split(",")[-1].strip()

    #print("Anchor is:", anchor)

    fuel_attributeA = clean_lower_tables(anchor.shift(2, 1).fill(DOWN).filter("Not fuel poor").fill(DOWN))
    fuel_attributeB = clean_lower_tables(anchor.shift(3, 1).fill(DOWN).filter("Fuel poor").fill(DOWN))

    obs = fuel_attributeA.shift(2, 0).expand(RIGHT).expand(DOWN)
    obs = clean_lower_tables(obs)

    horizontal_dimension = anchor.expand(RIGHT).is_not_blank()

    horizontal_dimension = anchor.expand(RIGHT).is_not_blank()

    #Majority of the tables have both a differentiating dimension as well as the FPEER band dimension, this adds this common dimension back in
    #and shifts the differentiating dimension look up one step to the left
    #could replace this if statement with an argument that could be passed into the task dictionary which would be faster but this works for now
    #will add that if theres a similar thing in other tables but isnt FPEER band
    if cellCont(anchor.shift(LEFT)) == task["tables"][tab.name]["secondary_dimension"]:
        secondary_dimension = anchor.shift(LEFT).fill(DOWN).is_not_blank()
        secondary_dimension = clean_lower_tables(secondary_dimension)
        left_column = anchor.shift(-2, 0).fill(DOWN).is_not_blank()
        left_column = clean_lower_tables(left_column)
    else:
        left_column = anchor.shift(LEFT).fill(DOWN).is_not_blank()
        left_column = clean_lower_tables(left_column)

    measure_type = anchor.fill(RIGHT)
    if cellCont(anchor.shift(LEFT)) == task["tables"][tab.name]["secondary_dimension"]:
        dimensions = [
            HDimConst("Year", year),
            HDim(horizontal_dimension, "Category", CLOSEST, LEFT),
            HDim(secondary_dimension, task["tables"][tab.name]["secondary_dimension"].replace('FPEER band', 'FPEER'), DIRECTLY, LEFT),
            HDim(left_column, task["tables"][tab.name]["differentiating_dimension"], CLOSEST, ABOVE),
            HDim(fuel_attributeA, "Households not in Fuel Poverty", DIRECTLY, LEFT),
            HDim(fuel_attributeB, "Households in Fuel Poverty", DIRECTLY, LEFT)
        ]
    elif tab.name in ['Table 31', 'Table 32']:
        dimensions = [
            HDimConst("Year", year),
            HDim(horizontal_dimension, "Category", CLOSEST, LEFT),
            HDim(left_column, task["tables"][tab.name]["differentiating_dimension"].split(' - ', 1)[0], DIRECTLY, LEFT),
            HDimConst("Fuel Type", task["tables"][tab.name]["differentiating_dimension"].split(' - ', 1)[1]),
            HDim(fuel_attributeA, "Households not in Fuel Poverty", DIRECTLY, LEFT),
            HDim(fuel_attributeB, "Households in Fuel Poverty", DIRECTLY, LEFT)
        ]
    elif tab.name in ['Table 33', 'Table 34', 'Table 35', 'Table 36']:
        dimensions = [
            HDimConst("Year", year),
            HDim(horizontal_dimension, "Category", CLOSEST, LEFT),
            HDimConst("Eligibility Type", task["tables"][tab.name]["differentiating_dimension"]),
            HDim(left_column, "Eligible", DIRECTLY, LEFT),
            HDim(fuel_attributeA, "Households not in Fuel Poverty", DIRECTLY, LEFT),
            HDim(fuel_attributeB, "Households in Fuel Poverty", DIRECTLY, LEFT)
        ]
    else:
        dimensions = [
            HDimConst("Year", year),
            HDim(horizontal_dimension, "Category", CLOSEST, LEFT),
            HDim(left_column, task["tables"][tab.name]["differentiating_dimension"], DIRECTLY, LEFT),
            HDim(fuel_attributeA, "Households not in Fuel Poverty", DIRECTLY, LEFT),
            HDim(fuel_attributeB, "Households in Fuel Poverty", DIRECTLY, LEFT)
        ]

    cs = ConversionSegment(obs, dimensions)
    #savepreviewhtml(cs, fname="Preview.html")
    df = cs.topandas()

    # NOTE - moving pathify to after the joins, so we can generate accurate codelists
    # Pathify the differentiating dimension, switch all-households to all
    #df[task["tables"][tab.name]["differentiating_dimension"]] = df[task["tables"][tab.name]["differentiating_dimension"]].apply(pathify)

    # Measure and Unit
    df["Unit"] = df["Category"].apply(LookupFromDict("unit", task["units_map"]))

    df["Measure Type"] = df["Category"].apply(LookupFromDict("measure", task["measures_map"]))

    # Add the constant column
    if "constant_columns" in task["tables"][tab.name].keys():
        for k,v in task["tables"][tab.name]["constant_columns"].items():
            df[k] = v

    # Tidy up
    df = df.rename(columns={"OBS": "Value"})

    return df


def generate_codelist(title, df, col):
    """
    Given a dataframe and a specific column, generate a codelist csv and csvw
    """

    # TODO - use makedir and path!
    destination = './codelists/{}.csv'.format(pathify(col))

    # TODO - does it already exist? Are there any unaccounted for
    # values in this version of that codelist?

    if Path(destination).is_file():
        codelistDF = pd.read_csv(destination).fillna('')
        for val in list(df[col].unique()):
            codelistDF = codelistDF.append({'Label' : val , 'Notation' : pathify(str(val)), 'Parent Notation' : '', 'Sort Priority' : ''} , ignore_index=True)

        codelistDF = codelistDF.drop_duplicates()
        codelistDF.to_csv(destination, index=False)

    else:
        codelist = {
            "Label": [],
            "Notation": [],
            "Parent Notation": [],
            "Sort Priority": []
            }

        if col in ['Households in Fuel Poverty', 'Households not in Fuel Poverty']:
            for val in list(df[col].unique()):
                codelist["Label"].append(val.replace('.0', ''))
                codelist["Notation"].append(val.replace('.0', ''))
                codelist["Parent Notation"].append("")
                codelist["Sort Priority"].append("")
        else:
            for val in list(df[col].unique()):
                codelist["Label"].append(val)
                codelist["Notation"].append(pathify(str(val)))
                codelist["Parent Notation"].append("")
                codelist["Sort Priority"].append("")

        df = pd.DataFrame.from_dict(codelist)
        df.to_csv(destination, index=False)

    # Output the codelist csvw
    url = "{}-{}.csv".format(pathify(title), pathify(col))
    path_id = "http://gss-data.org.uk/data/gss_data/energy/beis-fuel-poverty-detailed-tables-2020"
    codelist_csvw = generate_codelist_from_template(url, title, col, path_id)

    codelist_csvw = codelist_csvw.strip()

    #with open('./codelists/{}.csv-metadata.json'.format(pathify(col)), 'w') as f:
     #   f.write(codelist_csvw)



def clean_lower_tables(bag):
    """
    Cut everything below the relevant "All households" line
    """
    try:
        return bag -bag.expand(DOWN).expand(LEFT).filter("All households").by_index(1).fill(DOWN).expand(RIGHT)
    except:
        return bag -bag.expand(DOWN).expand(RIGHT).filter("England").expand(LEFT).expand(DOWN).expand(RIGHT)


# TODO - there's gotta be a baked in pandas method for this im not remembering, look it up, this feels dumb
class LookupFromDict:
    """
    Pandas apply function that takes a dictionary argument.
    Used to figure out the measures to use, uses the "measures_map"
    dictionary passed from the task
    """

    # store the dict in the class on instantiation
    def __init__(self, name, measures_map):
        self.map = measures_map
        self.name = name

    # do the lookup on each cell value passed in by df[whatever].apply()
    def __call__(self, cell_value):
        try:
            for k in self.map.keys():
                if k in cell_value: # use "in" not a direct lookup to avoid whitespace/footnote issues
                    return self.map[k]
        except Exception as err:
            raise ('Measure lookup, couldnt find {} lookup for value: "{}".'.format(self.name, cell_value)) from err


# In[587]:


scraper = Scraper(seed="info.json")
scraper


# In[588]:


scraper.distributions


# In[589]:


distro = scraper.distribution(latest=True)
tabs = distro.as_databaker()
tabs = [x for x in tabs if "Table" in x.name] # TODO = typos? Tables change? Numnbering of tables by concept changes?

scraper.dataset.family = 'energy'

energy_efficiency_task = {
    "name": "Energy Efficiency",
    "store_as": "energyEfficiency",
    "tables":{
        "Table 3": {
            "sub_table_count": 1,
            "differentiating_dimension": "FPEER",
            "secondary_dimension": None
        },
        "Table 4": {
            "sub_table_count": 1,
            "differentiating_dimension": "SAP12 band",
            "secondary_dimension": None
        },
        "Table 5": {
            "sub_table_count": 2,
            "differentiating_dimension": "Rurality",
            "secondary_dimension": "FPEER band"
        },
        "Table 6": {
            "sub_table_count": 1,
            "differentiating_dimension": "Region",
            "secondary_dimension": None
        },
        "Table 7": {
            "sub_table_count": 1,
            "differentiating_dimension": "Dwelling type",
            "secondary_dimension": None
        },
        "Table 8": {
            "sub_table_count": 1,
            "differentiating_dimension": "Dwelling age",
            "secondary_dimension": None
        },
        "Table 9": {
            "sub_table_count": 1,
            "differentiating_dimension": "Floor area",
            "secondary_dimension": None
        },
        "Table 10": {
            "sub_table_count": 2,
            "differentiating_dimension": "Gas grid connection",
            "secondary_dimension": "FPEER band"
        },
        "Table 11": {
            "sub_table_count": 2,
            "differentiating_dimension": "Central heating",
            "secondary_dimension": "FPEER band"
        },
        "Table 12": {
            "sub_table_count": 2,
            "differentiating_dimension": "Main fuel type",
            "secondary_dimension": "FPEER band"
        },
        "Table 13": {
            "sub_table_count": 1,
            "differentiating_dimension": "Central heating",
            "secondary_dimension": "Main fuel type"
        },
        "Table 14": {
            "sub_table_count": 1,
            "differentiating_dimension": "Boiler Type",
            "secondary_dimension": None
        },
        "Table 15": {
            "sub_table_count": 2,
            "differentiating_dimension": "Wall insulation",
            "secondary_dimension": "FPEER band"
        },
        "Table 16": {
            "sub_table_count": 1,
            "differentiating_dimension": "Wall type",
            "secondary_dimension": "Gas grid connection"
        },
        "Table 17": {
            "sub_table_count": 1,
            "differentiating_dimension": "Loft insulation",
            "secondary_dimension": None
        }
    },
    "measures_map": {
        "Aggregate fuel poverty gap (£m)": "Aggregate fuel poverty Gap",
        "Average fuel poverty gap (£)": "Average fuel poverty Gap"
    },
    "units_map": {
        "Aggregate fuel poverty gap (£m)": "gbp-million",
        "Average fuel poverty gap (£)": "gbp"
    }
}

household_characteristics_task = {
    "name": "Household Characteristics",
    "store_as": "householdCharacteristics",
    "tables":{
        #Not sure how to add in Table 1 as Households in Fuel Poverty is an attribute to observations in the rest of the table
        "Table 1": {
            "sub_table_count": 1,
            "differentiating_dimension": "All households",
            "secondary_dimension": None
        },
        "Table 18" :{
            "sub_table_count": 3,
            "differentiating_dimension": "Tenure",
            "secondary_dimension": "FPEER band"
        },
        "Table 19" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Housing Sector",
            "secondary_dimension": None
        },
        "Table 20" :{
            "sub_table_count": 2,
            "differentiating_dimension": "Household Composition",
            "secondary_dimension": "FPEER band"
        },
        "Table 21" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Age band of youngest person in household",
            "secondary_dimension": None
        },
        "Table 22" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Age band of oldest person in household",
            "secondary_dimension": None
        },
        "Table 23" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Number of people in household",
            "secondary_dimension": None
        },
        "Table 24" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Ethnicity",
            "secondary_dimension": None
        },
        "Table 25" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Long term illness or disability",
            "secondary_dimension": None
        },
        "Table 26" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Under-occupancy",
            "secondary_dimension": None
        },
        "Table 27" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Vulnerability",
            "secondary_dimension": None
        },
        "Table 28" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Vulnerability",
            "secondary_dimension": "Tenure"
        }
    },
    "measures_map": {
        "Aggregate fuel poverty gap (£m)": "Aggregate fuel poverty Gap",
        "Average fuel poverty gap (£)": "Average fuel poverty Gap"
    },
    "units_map": {
        "Aggregate fuel poverty gap (£m)": "gbp-million",
        "Average fuel poverty gap (£)": "gbp"
    }
}

household_income_task = {
    "name": "Household Income",
    "store_as": "householdIncome",
    "tables":{
        "Table 29" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Employment status",
            "secondary_dimension": None
        },
        "Table 30" :{
            "sub_table_count": 2,
            "differentiating_dimension": "After Housing Costs (AHC) equivalised income decile group",
            "secondary_dimension": "FPEER band"
        }
    },
    "measures_map": {
        "Aggregate fuel poverty gap (£m)": "Aggregate fuel poverty Gap",
        "Average fuel poverty gap (£)": "Average fuel poverty Gap"
    },
    "units_map": {
        "Aggregate fuel poverty gap (£m)": "gbp-million",
        "Average fuel poverty gap (£)": "gbp"
    }
}

fuel_payment_task = {
    "name": "Fuel Payment Type",
    "store_as": "fuelPaymentType",
    "tables":{
        "Table 31" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Method of payment - gas",
            "secondary_dimension": None
        },
        "Table 32" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Method of payment - electricity",
            "secondary_dimension": None
        }
    },
    "measures_map": {
        "Aggregate fuel poverty gap (£m)": "Aggregate fuel poverty Gap",
        "Average fuel poverty gap (£)": "Average fuel poverty Gap"
    },
    "units_map": {
        "Aggregate fuel poverty gap (£m)": "gbp-million",
        "Average fuel poverty gap (£)": "gbp"
    }
}

eligibility_task = {
    "name": "Eligibility",
    "store_as": "eligibility",
    "tables":{
        "Table 33" :{
            "sub_table_count": 1,
            "differentiating_dimension": "ECO affordable warmth eligibility",
            "secondary_dimension": None
        },
        "Table 34" :{
            "sub_table_count": 1,
            "differentiating_dimension": "ECO 3 Help to Heat Group eligibility",
            "secondary_dimension": None
        },
        "Table 35" :{
            "sub_table_count": 1,
            "differentiating_dimension": "Eligible for WHD broader group",
            "secondary_dimension": None
        },
        "Table 36" :{
            "sub_table_count": 1,
            "differentiating_dimension": "In receipt of benefits",
            "secondary_dimension": None
        }
    },
    "measures_map": {
        "Aggregate fuel poverty gap (£m)": "Aggregate fuel poverty Gap",
        "Average fuel poverty gap (£)": "Average fuel poverty Gap"
    },
    "units_map": {
        "Aggregate fuel poverty gap (£m)": "gbp-million",
        "Average fuel poverty gap (£)": "gbp"
    }
}


# In[590]:


LITTLE_TABLE_ANCHOR = "Proportion of households that are in this group (%)"
BIG_TABLE_ANCHOR = "Proportion of households within group (%)" # note we dont want this cell but we're using it to differentiate the styles of table -

table_dict = {}

# do everything
# for dataset_task in [energy_efficiency_tasks, household_characteristics_tasks, household_income_tasks,fuel_payment_type_tasks]:
for category, dataset_task in {
    "Energy Efficiency": energy_efficiency_task,
    "Household Characteristics" : household_characteristics_task,
    "Household Income" : household_income_task,
    "Fuel Payment Type" : fuel_payment_task,
    "Eligibility" : eligibility_task
    }.items():

    try:
        subset_of_tabs = [x for x in tabs if x.name.strip() in dataset_task["tables"].keys()]

        for tab in subset_of_tabs:

            # there can only be one style of anchor per sheet
            is_little_table = False
            anchors = tab.filter(BIG_TABLE_ANCHOR)

            if len(anchors) == 0:
                anchors = tab.filter(LITTLE_TABLE_ANCHOR)
                is_little_table = True

            if len(anchors) == 0:
                raise Exception("Cannot find any anchor cells")

            processed_tables = []

            for i, anchor in enumerate(anchors):# i.e for each sub table on this sheet
                if is_little_table:
                    if tab.name == 'Table 1':
                        if i == 1:
                            break
                        df = table_one_transform(anchor, dataset_task)
                        processed_tables.append(df)
                    else:
                        df = process_little_table(anchor, dataset_task)
                        processed_tables.append(df)
                else:
                    df = process_big_table(anchor, dataset_task)
                    processed_tables.append(df)

            df = pd.concat(processed_tables)

            # Store however many tabs we've extracted against the specified identifier

            if dataset_task["store_as"] in table_dict:
                table_dict[dataset_task["store_as"]] = pd.concat([table_dict[dataset_task["store_as"]], df])
            else:
                table_dict[dataset_task["store_as"]] = df

            #table_dict[dataset_task["store_as"]] = df
            #trace.store(dataset_task["store_as"], df)

    except Exception as err:
        raise Exception('Error encountered while processing task "{}" from "{}".'.format(json.dumps(dataset_task["tables"][tab.name]),
                                                                                         dataset_task["name"])) from err


# In[591]:


# # CSVW Mapping
#
# We're gonna need quite a lof of mapping for all these datasets, so we'll do it here and pass it around dynamically.
#
# I've broken it down in the `"csvw_common_map"` (for columns that appear in every dataset) a `"csvw_value_map"` and dataset specific maps where necessary.


# In[592]:


# csvw mapping for dimensions common to all datasets
csvw_common_map = {
    "Period": {
                "parent": "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod",
                "value": "http://reference.data.gov.uk/id/{+period}"
            },
    "Marker": {
                "attribute": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus",
                "value": "http://gss-data.org.uk/def/concept/cogs-markers/{marker}"
      },
    "Region": {
                "parent": "http://purl.org/linked-data/sdmx/2009/dimension#refArea",
                "value": "http://statistics.data.gov.uk/id/statistical-geography/{+region}",
                "description": ""
            }
}

# csvw mapping for representing the different measures and units in the dataset(s)
# depending on the measure type used.
csvw_value_map = {
     "Aggregate fuel poverty Gap": {
                 "unit": "http://gss-data.org.uk/def/concept/measurement-units/gbp-million",
                 "measure": "http://gss-data.org.uk/def/measure/aggregate-fuel-poverty-gap",
                 "datatype": "double"
             },
     "Average fuel poverty Gap": {
                 "unit": "http://gss-data.org.uk/def/concept/measurement-units/gbp",
                 "measure": "http://gss-data.org.uk/def/measure/average-fuel-poverty-gap",
                 "datatype": "double"
             }
}


# In[593]:


df.head()
df['Category'].unique()

# # Metadata & Joins


# In[594]:


table_joins = {
    "Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Aggregate Gap": {
        "category": "Aggregate fuel poverty gap (£m)",
        "tables": "energyEfficiency",
        "comment": "Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
        "datasetid": "edc-fuelcosts-energyagg",
        "structure" : ['Year', 'FPEER', 'SAP12 Band', 'Rurality', 'Region', 'Dwelling Type', 'Dwelling Age', 'Floor Area', 'Gas Grid Connection', 'Central Heating', 'Main Fuel Type', 'Boiler Type', 'Wall Insulation', 'Wall Type', 'Loft Insulation', 'Households in Fuel Poverty', 'Households not in Fuel Poverty', 'Measure Type', 'Unit', 'Value', 'Marker']
    },
    "Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Average Gap": {
        "category": "Average fuel poverty gap (£)",
        "tables": "energyEfficiency",
        "comment": "Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
       "datasetid": "edc-fuelcosts-energyavg",
        "structure" : ['Year', 'FPEER', 'SAP12 Band', 'Rurality', 'Region', 'Dwelling Type', 'Dwelling Age', 'Floor Area', 'Gas Grid Connection', 'Central Heating', 'Main Fuel Type', 'Boiler Type', 'Wall Insulation', 'Wall Type', 'Loft Insulation', 'Households in Fuel Poverty', 'Households not in Fuel Poverty', 'Measure Type', 'Unit', 'Value', 'Marker']
    },
    "Fuel poverty detailed tables - Household Characteristics - Aggregate Gap": {
        "category": "Aggregate fuel poverty gap (£m)",
        "tables": "householdCharacteristics",
        "comment": "Fuel poverty statistics report detailing Household characteristics by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Household characteristic by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
        "datasetid": "edc-fuelcosts-characteristicsagg",
        "structure" : ["Year", "FPEER", "Tenure", "Housing Composition", "Age of Youngest Person", "Age of Oldest Person", "People in Household", "Ethnicity", "Illness or Disability", "Under-Occupancy", "Vulnerability", "Households in Fuel Poverty", "Households not in Fuel Poverty", "Measure Type", "Unit", "Marker", "Value"]
    },
    "Fuel poverty detailed tables - Household Characteristics - Average Gap": {
        "category": "Average fuel poverty gap (£)",
        "tables": "householdCharacteristics",
        "comment": "Fuel poverty statistics report detailing Household characteristics by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Household characteristic by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
        "datasetid": "edc-fuelcosts-characteristicsavg",
        "structure" : ["Year", "FPEER", "Tenure", "Housing Composition", "Age of Youngest Person", "Age of Oldest Person", "People in Household", "Ethnicity", "Illness or Disability", "Under-Occupancy", "Vulnerability", "Households in Fuel Poverty", "Households not in Fuel Poverty", "Measure Type", "Unit", "Marker", "Value"]
    },
    "Fuel poverty detailed tables - Household Income - Aggregate Gap": {
        "category": "Aggregate fuel poverty gap (£m)",
        "tables": "householdIncome",
        "comment": "Fuel poverty statistics report detailing Household Income by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Household Income by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
        "datasetid": "edc-fuelcosts-incomeagg",
        "structure" : ["Year", "FPEER", "Employment Status", "Income Decile Group", "Households in Fuel Poverty", "Households not in Fuel Poverty", "Measure Type", "Unit", "Value"]
    },
    "Fuel poverty detailed tables - Household Income - Average Gap": {
        "category": "Average fuel poverty gap (£)",
        "tables": "householdIncome",
        "comment": "Fuel poverty statistics report detailing Household Income by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Household Income by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
        "datasetid": "edc-fuelcosts-incomeavg",
        "structure" : ["Year", "FPEER", "Employment Status", "Income Decile Group", "Households in Fuel Poverty", "Households not in Fuel Poverty", "Measure Type", "Unit", "Value"]
    },
    "Fuel poverty detailed tables - Fuel Payment Type - Aggregate Gap": {
        "category": "Aggregate fuel poverty gap (£m)",
        "tables": "fuelPaymentType",
        "comment": "Fuel poverty statistics report detailing Fuel Payment Type by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Fuel Payment Type by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
        "datasetid": "edc-fuelcosts-paymentagg",
        "structure" : ["Year", "Fuel Type", "Payment Method", "Households in Fuel Poverty", "Households not in Fuel Poverty", "Measure Type", "Unit", "Value"]
    },
    "Fuel poverty detailed tables - Fuel Payment Type - Average Gap": {
        "category": "Average fuel poverty gap (£)",
        "tables": "fuelPaymentType",
        "comment": "Fuel poverty statistics report detailing Fuel Payment Type by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Fuel Payment Type by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
        "datasetid": "edc-fuelcosts-paymentavg",
        "structure" : ["Year", "Fuel Type", "Payment Method", "Households in Fuel Poverty", "Households not in Fuel Poverty", "Measure Type", "Unit", "Value"]
    },
    "Fuel poverty detailed tables - Eligibility - Aggregate Gap": {
        "category": "Aggregate fuel poverty gap (£m)",
        "tables": "eligibility",
        "comment": "Fuel poverty statistics report detailing Eligibility by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Eligibility by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
        "datasetid": "edc-fuelcosts-eligibilityagg",
        "structure" : ["Year", "Eligibility Type", "Eligible", "Households in Fuel Poverty", "Households not in Fuel Poverty", "Measure Type", "Unit", "Value"]
    },
    "Fuel poverty detailed tables - Eligibility - Average Gap": {
        "category": "Average fuel poverty gap (£)",
        "tables": "eligibility",
        "comment": "Fuel poverty statistics report detailing Eligibility by Aggregate and Average Fuel Poverty Gap",
        "description": """Fuel poverty statistics report detailing Eligibility by Aggregate and Average Fuel Poverty Gap
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook""",
       "datasetid": "edc-fuelcosts-eligibilityavg",
        "structure" : ["Year", "Eligibility Type", "Eligible", "Households in Fuel Poverty", "Households not in Fuel Poverty", "Measure Type", "Unit", "Value"]
    }
}

# Given there are standard column to all datacubes it's easier
# to define the columns we're NOT going to pathify
COLUMNS_TO_NOT_PATHIFY = ["Region", "Households in Fuel Poverty", "Households not in Fuel Poverty", "Value", "Period", "Unit", "Measure Type"]

# Switch for generating codelists (should usually be False)
GENERATE_CODELISTS = False

# Print the mapping where you need to debug stuff
SHOW_MAPPING = False

count = 0

# https://staging.gss-data.org.uk/cube/explore?uri=http%3A%2F%2Fgss-data.org.uk%2Fdata%2Fgss_data%2Fedvp%2Fbeis-fuel-poverty-supplementary-tables-2020-catalog-entry
for title, info in table_joins.items():

    print(title)

    #df = trace.combine_and_trace(title, info["tables"])
    df = table_dict[info["tables"]]
    # slice just the bit we want using category, then drop the column
    df = df[df["Category"] == info["category"]]
    df = df.drop("Category", axis=1)

    # Fill up the sparsity with alls
    df = df.fillna("all")
    for col in df.columns.values:
        if col not in ['DATAMARKER', 'Value']:
            df[df[col] == ""] = "all"

    df = df.replace({"All households" : 'all'})

    #replace * datamarker with value before * is removed by pathify
    #also using this oppertunity to make column values match the spec
    df = df.replace({'DATAMARKER' : {'*' : 'low-sample-count',
                                     'all' : ''},
                     'Region' : {'all' : 'E92000001',
                                 'East' : 'E12000006',
                                 'East Midlands' : 'E12000004',
                                 'London' : 'E12000007',
                                 'North East' : 'E12000001',
                                 'North West' : 'E12000002',
                                 'South East' : 'E12000008',
                                 'South West' : 'E12000009',
                                 'West Midlands' : 'E12000005',
                                 'Yorkshire and the Humber' : 'E12000003',
                                 'all' : 'E92000001'},
                     'Dwelling type' : {'All households' : 'all',
                                        'Converted flat1' : 'Converted flat'},
                     'Dwelling age' : {'All households' : 'all'},
                     'Floor area' : {'All households' : 'all'},
                     'Gas grid connection' : {'All households' : 'T',
                                              'Yes' : 'Y',
                                              'No' : 'N',
                                              'all' : 'T'},
                     'Central heating' : {'All households' : 'all',
                                          'Other heating system' : 'other'},
                     'Main fuel type' : {'All households' : 'all',
                                         'Other2' : 'other',
                                         'Other1' : 'other'},
                     'Boiler Type' : {'All households' : 'all'},
                     'Wall insulation' : {'All households' : 'all',
                                          'Solid or Other4' : 'Solid or Other',
                                          'Other3' : 'Other'},
                     'Wall type' : {'All households' : 'all'},
                     'Loft insulation' : {'All households' : 'all',
                                          'Under 125mm ' : 'Under 125mm'},
                     'Households in Fuel Poverty' : {'*' : 'low-sample-count'},
                     'Households not in Fuel Poverty' : {'*' : 'low-sample-count'},
                     'Tenure' : {'Housing association2' : 'Housing association'},
                     'Household Composition' : {'Couple with dependent child(ren)' : 'Couple with dependent children',
                                                'Couple, no dependent child(ren) aged 60 or over' : 'Couple, no dependent children aged 60 or over',
                                                'Couple, no dependent child(ren) under 60' : 'Couple, no dependent children under 60',
                                                'Household with dependent child(ren)5' : 'Household with dependent children',
                                                'Household with one or more persons aged 60 or over5' : 'Household with one or more persons aged 60 or over',
                                                'Lone parent with dependent child(ren)' : 'Lone parent with dependent children',
                                                'Other multi-person households4' : 'Other multi-person households'},
                     'Long term illness or disability' : {'No2' : 'N',
                                                          'Yes' : 'Y',
                                                          'all' : 'T'},
                     'Vulnerability' : {'Not Vulnerable' : 'N',
                                        'Vulnerable' : 'Y',
                                        'all' : 'T'},
                     'Number of people in household' : {'1.0' : '1', '2.0' : '2', '3.0' : '3', '4.0' : '4'},
                     'Eligible' : {'all' : 'T', 'No' : 'N', 'Yes' : 'Y'}})

    df = df.rename(columns={'SAP12 band' : 'SAP12 Band',
                            'DATAMARKER' : 'Marker',
                            'Dwelling type' : 'Dwelling Type',
                            'Dwelling age' : 'Dwelling Age',
                            'Floor area' : 'Floor Area',
                            'Gas grid connection' : 'Gas Grid Connection',
                            'Central heating' : 'Central Heating',
                            'Main fuel type' : 'Main Fuel Type',
                            'Wall insulation' : 'Wall Insulation',
                            'Wall type' : 'Wall Type',
                            'Loft insulation' : 'Loft Insulation',
                            'Age band of youngest person in household' : 'Age of Youngest Person',
                            'Age band of oldest person in household' : 'Age of Oldest Person',
                            'Number of people in household' : 'People in Household',
                            'Long term illness or disability' : 'Illness or Disability',
                            'Under-occupancy' : 'Under-Occupancy',
                            'Household Composition' : 'Housing Composition',
                            'Employment status' : 'Employment Status',
                            'After Housing Costs (AHC) equivalised income decile group' : 'Income Decile Group',
                            'Method of payment' : 'Payment Method'})

    if 'Marker' in df.columns.values.tolist():
        df = df.drop(df[(df['Value'] == '') & (df['Marker'] == '')].index)
    else:
        df = df.drop(df[(df['Value'] == '')].index)

    #df = df[info['structure']]

    df['Households in Fuel Poverty'] = df.apply(lambda x: x['Households in Fuel Poverty'].replace('.0', ''), axis=1)
    df['Households not in Fuel Poverty'] = df.apply(lambda x: x['Households not in Fuel Poverty'].replace('.0', ''), axis=1)

    df = df.rename(columns={'Year' : 'Period'})

    # Metadata etc
    scraper.dataset.title = title
    if "comment" in info.keys():
        scraper.dataset.comment = info["comment"]

    if "description" in info.keys():
        scraper.dataset.description = info["description"]

    # Pathify (sometimes generate codelists from) appropriate columns
    for col in df.columns.values.tolist():

        #if GENERATE_CODELISTS:
            #generate_codelist(title, df, col)

        if col in COLUMNS_TO_NOT_PATHIFY:
            continue

        try:
            df[col] = df[col].apply(pathify)
        except Exception as err:
            raise Exception('Failed to pathify column "{}".'.format(col)) from err



    # CSVW Mapping
    # We're gonna change the column mapping on the fly to deal with the large number and
    # variation of datasets

    do_mapping = True

    if do_mapping:
        mapping = {}
        with open("info.json") as f:
            info_json = json.load(f)

            # "Common" column mappings for this dataset
            for k, v in csvw_common_map.items():
                mapping[k] = v

            # "Value" entry for this dataset
            measures_list = list(df["Measure Type"].unique())
            assert len(measures_list) == 1, "At this point in this transform we should only have one measure type"
            mapping["Value"] = csvw_value_map[measures_list[0]]

            # If it's neither common nor value, it's a locally declared dimension
            cols_we_have_a_map_for = list(csvw_common_map.keys())
            cols_we_have_a_map_for.append("Value")

            # TODO - somewhere else
            url_title = "beis-fuel-poverty-detailed-tables-2020"

            for col in df.columns.values.tolist():
                if col not in cols_we_have_a_map_for:
                    mapping[col] = {
                        "parent": "http://gss-data.org.uk/data/gss_data/energy/{url_title}/concept-scheme/{col}".format(url_title=pathify(url_title), col=pathify(col)),
                        "value": "http://gss-data.org.uk/data/gss_data/energy/{url_title}/concept/{col}/{{{col_underscored}}}".format(url_title=pathify(url_title), col=pathify(col), col_underscored=pathify(col).replace("-", "_")),
                        "description": ""
                    }

            # "Deprivation Indicator": {
            #            "parent": "http://gss-data.org.uk/data/gss_data/towns-high-streets/sg-scottish-index-of-multiple-deprivation-2020/concept-scheme/deprivation-indicator",
            #            "value": "http://gss-data.org.uk/data/gss_data/towns-high-streets/sg-scottish-index-of-multiple-deprivation-2020/concept/deprivation-indicator/{deprivation_indicator}",
            #            "description": "SIMD is the Scottish Government's standard approach to identify areas of multiple deprivation in Scotland. It can help improve understanding about the outcomes and circumstances of people living in the most deprived areas in Scotland. It can also allow effective targeting of policies and funding where the aim is to wholly or partly tackle or take account of area concentrations of multiple deprivation. SIMD ranks data zones from most deprived (ranked 1) to least deprived (ranked 6,976). People using SIMD will often focus on the data zones below a certain rank, for example, the 5%, 10%, 15% or 20% most deprived data zones in Scotland. SIMD is an area-based measure of relative deprivation: not every person in a highly deprived area will themselves be experiencing high levels of deprivation."
            # },

            # Read the map back into the cubes class
            #info_json["transform"]["columns"] = mapping
            # cubes.info = info_json

        if SHOW_MAPPING:
            print("Mapping for: ", title)
            print(json.dumps(mapping, indent=2))
            print("\n")

    # FOR NOW - remove measure type
    #df = df.drop("Measure Type", axis=1)
    #df = df.drop("Unit", axis=1)

    # FOR NOW - remove the Attributes
    if "Households not in Fuel Poverty" in df.columns:
        df = df.drop("Households not in Fuel Poverty", axis=1)
    if "Households in Fuel Poverty" in df.columns:
        df = df.drop("Households in Fuel Poverty", axis=1)

    df['Measure Type'] = df.apply(lambda x: pathify(x['Measure Type']), axis = 1)

    if 'Marker' in list(df.columns):
        df['Value'] = df.apply(lambda x: '0.0' if x['Marker'] != '' else x['Value'], axis = 1)
    
    df = df.drop_duplicates()

    df.to_csv(pathify(scraper.title) + '-observations.csv', index=False)

    catalog_metadata = scraper.as_csvqb_catalog_metadata()
    catalog_metadata.to_json_file(pathify(scraper.title) + '-catalog-metadata.json')

    #with open(pathify(scraper.title) + '-info.json', 'w') as f:
    #    json.dump(coldef, f, indent=2)

    """csvName = "observations-{}.csv".format(pathify(info['datasetid']))
    out = Path('out')
    out.mkdir(exist_ok=True)
    df.drop_duplicates().to_csv(out / (csvName), index = False)

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + '/' + info['datasetid']# differentiating name goes here + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    from urllib.parse import urljoin

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform._mapping = mapping
    csvw_transform.set_mapping(mapping)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())"""


# In[595]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[596]:


#cubes.output_all()
#cubes.base_url = "http://gss-data.org.uk/data/gss_data/energy/beis-fuel-poverty-detailed-tables-2020"
#ubes.output_all()

