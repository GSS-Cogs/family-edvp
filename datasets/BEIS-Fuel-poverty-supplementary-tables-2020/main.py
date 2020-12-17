#!/usr/bin/env python
# coding: utf-8

# In[91]:


# -*- coding: utf-8 -*-
# + {}
from gssutils import *
import json

from template import generate_codelist_from_template

cubes = Cubes("info.json")

coldef = json.load(open('info.json'))


# In[92]:


# # Helpers
#
# These are all the same two variations of table repeated, so we're just gonna have a function for each


# In[93]:


LITTLE_TABLE_ANCHOR = "Median equivalised fuel costs (£)"
BIG_TABLE_ANCHOR = "Proportion of households within group (%)" # note we dont want this cell but we're using it to differentiate the styles of table -

def process_little_table(anchor, task, trace):
    """
    Given a single anchoring cell, process the smaller style of the tables
    """

    year = "year/"+tab.excel_ref('A1').value.split(",")[-1].strip()
    trace.Year('Get year from cell A1 and add "/year" prefix, gets us:"{}"'.format(year))

    # Get the obs, we don't want columns f + G
    # TODO - safety to make sure F & G actually are the columns we don't want for a given table
    obs = anchor.shift(DOWN).expand(RIGHT).expand(DOWN).is_not_blank()
    obs = obs - tab.excel_ref('F:G')
    obs = clean_lower_tables(obs)

    trace.add_column("Category")
    trace.Category('Extract colum headers as a temporary "Category" column.')
    horizontal_dimension = anchor.expand(RIGHT).is_not_blank()

    # Use an alias to trace the differentiating dimension, as the name may or may not
    # support being set as an attribute
    trace.add_column({task["tables"][tab.name]["differentiating_dimension"]:"Diffdim"})
    trace.Diffdim('Take the left hand column as: "{}".'.format(task["tables"][tab.name]["differentiating_dimension"]))

    left_column = anchor.shift(LEFT).fill(DOWN).is_not_blank()
    left_column = clean_lower_tables(left_column)

    measure_type = anchor.fill(RIGHT)

    dimensions = [
        HDimConst("Year", year),
        HDim(horizontal_dimension, "Category", DIRECTLY, ABOVE),
        HDim(left_column, task["tables"][tab.name]["differentiating_dimension"], DIRECTLY, LEFT)
    ]

    cs = ConversionSegment(obs, dimensions)
    df = cs.topandas()

    # NOTE - moving pathify to after the joins, so we can generate accurate codelists
    # Pathify the differentiating dimension, switch all-households to all
    #df[task["tables"][tab.name]["differentiating_dimension"]] = df[task["tables"][tab.name]["differentiating_dimension"]].apply(pathify)

    df[task["tables"][tab.name]["differentiating_dimension"]] = df[task["tables"][tab.name]["differentiating_dimension"]]             .map(lambda x: x.replace("All Households", "all"))

    # Measure and Unit
    trace.Unit('Set unit from mapping: "{}".'.format(json.dumps(task["units_map"])))
    df["Unit"] = df["Category"].apply(LookupFromDict("unit", task["units_map"]))

    trace.Measure_Type('Set measure type from mapping: "{}".'.format(json.dumps(task["measures_map"])))
    df["Measure Type"] = df["Category"].apply(LookupFromDict("measure", task["measures_map"]))

    # Add the constant column
    if "constant_columns" in task["tables"][tab.name].keys():
        for k,v in task["tables"][tab.name]["constant_columns"].items():
            trace.add_column(k)
            trace.multi([k.replace(" ", "_")], 'Set as value: "{}".'.format(v))
            df[k] = v

    # Tidy up
    df = df.rename(columns={"OBS": "Value"})

    return df, trace

def process_big_table(anchor, task, trace):
    """
    Given a single anchoring cell, process the bigger style of the tables
    """
    year = "year/"+tab.excel_ref('A1').value.split(",")[-1]

    # Switch to the anchor point we actually want to use
    anchor = anchor.expand(RIGHT).filter(LITTLE_TABLE_ANCHOR).assert_one()

    fuel = anchor.expand(RIGHT).expand(DOWN).filter(contains_string("fuel"))
    fuel = clean_lower_tables(fuel)
    assert len(fuel) == 2, 'We should only be selecting two references to "fuel" per sub table'

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
            codelistDF = codelistDF.append({'Label' : val.replace('-', 'to') , 'Notation' : pathify(str(val)), 'Parent Notation' : '', 'Sort Priority' : ''} , ignore_index=True)

        codelistDF = codelistDF.drop_duplicates()
        codelistDF.to_csv(destination, index=False)

    else:
        codelist = {
            "Label": [],
            "Notation": [],
            "Parent Notation": [],
            "Sort Priority": []
            }

        for val in list(df[col].unique()):
            codelist["Label"].append(val.replace('-', 'to'))
            codelist["Notation"].append(pathify(str(val)))
            codelist["Parent Notation"].append("")
            codelist["Sort Priority"].append("")

        df = pd.DataFrame.from_dict(codelist)
        df.to_csv(destination, index=False)

    # Output the codelist csvw
    url = "{}-{}.csv".format(pathify(title), pathify(col))
    path_id = "http://gss-data.org.uk/data/gss_data/edvp/beis-fuel-poverty-supplementary-tables-2020"
    codelist_csvw = generate_codelist_from_template(url, title, col, path_id)

    codelist_csvw = codelist_csvw.strip()

    with open('./codelists/{}.csv-metadata.json'.format(pathify(col)), 'w') as f:
        f.write(codelist_csvw)


def clean_lower_tables(bag):
    """
    Cut everything below the relevant "All households" line
    """
    return bag -bag.expand(DOWN).expand(LEFT).filter("All households").by_index(1).fill(DOWN).expand(RIGHT)

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


# In[94]:


scraper = Scraper(seed="info.json")
scraper


distro = scraper.distribution(latest=True)
tabs = distro.as_databaker()
tabs = [x for x in tabs if "Table" in x.name] # TODO = typos? Tables change? Numnbering of tables by concept changes?

# # Energy Efficiency and Dwelling Characteristics
#
# Tables 1 through 11 (the parameters, the processing will happen later on)


# In[95]:


# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
energy_efficiency_task = {
    "name": "Energy Efficiency",
    "store_as": "1through17",
    "tables":{
        "Table 1": {
            "sub_table_count": 1,
            "differentiating_dimension": "Low Income High costs Matrix"
        },
        "Table 2": {
            "sub_table_count": 1,
            "differentiating_dimension": "FPEER"
        },
        "Table 3": {
            "sub_table_count": 1,
            "differentiating_dimension": "SAP BAND"
        },
        "Table 4": {
            "sub_table_count": 1,
            "differentiating_dimension": "Rurality"
        },
        "Table 5": {
            "sub_table_count": 1,
            "differentiating_dimension": "Region"
        },
        "Table 6": {
            "sub_table_count": 1,
            "differentiating_dimension": "Dwelling Type"
        },
       "Table 7": {
            "sub_table_count": 1,
            "differentiating_dimension": "Dwelling Age"
        },
       "Table 8": {
            "sub_table_count": 1,
            "differentiating_dimension": "Floor Area"
        },
       "Table 9": {
            "sub_table_count": 1,
            "differentiating_dimension": "Gas Grid Connection"
        },
       "Table 10": {
            "sub_table_count": 1,
            "differentiating_dimension": "Main Fuel Type"
        },
       "Table 11": {
            "sub_table_count": 1,
            "differentiating_dimension": "Wall Insulation"
        }
    },
    "measures_map": {
        "Median equivalised fuel costs (£)": "Median costs",
        "Median after housing costs (AHC), equivalised income (£)": "Median income",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "Median rating",
        "Median floor area (m2)": "Median floor area"
    },
    "units_map": {
        "Median equivalised fuel costs (£)": "gdp",
        "Median after housing costs (AHC), equivalised income (£)": "gdp",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "rating",
        "Median floor area (m2)": "m2"
    }
}


# In[96]:



# # Household characteristics
#
# Tables 12 through 16 (the parameters, the processing will happen later on)


# In[97]:


# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
household_characteristics_task = {
    "name": "Household characteristics",
    "store_as": "12through16",
    "tables":{
        "Table 12": {
            "sub_table_count": 1,
            "differentiating_dimension": "Tenure"
        },
        "Table 13": {
            "sub_table_count": 1,
            "differentiating_dimension": "Household Composition"
        },
       "Table 14": {
            "sub_table_count": 1,
            "differentiating_dimension": "Age of Youngest Person"
        },
       "Table 15": {
            "sub_table_count": 1,
            "differentiating_dimension": "Age of Oldest Person"
        },
       "Table 16": {
            "sub_table_count": 1,
            "differentiating_dimension": "Ethnicity"
        }
    },
    "measures_map": {
        "Median equivalised fuel costs (£)": "Median costs",
        "Median after housing costs (AHC), equivalised income (£)": "Median income",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "Median rating",
        "Median floor area (m2)": "Median floor area"
    },
    "units_map": {
        "Median equivalised fuel costs (£)": "gdp",
        "Median after housing costs (AHC), equivalised income (£)": "gdp",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "rating",
        "Median floor area (m2)": "m2"
    }
}


# In[98]:


# # Household income
#
# Tables 17 through 18 (the parameters, the processing will happen later on)


# In[99]:


# +

# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
household_income_task = {
    "name": "Household income",
    "store_as": "17through18",
    "tables": {
        "Table 17": {
            "sub_table_count": 1,
            "differentiating_dimension": "Employment Status"
        },
        "Table 18": {
            "sub_table_count": 1,
            "differentiating_dimension": "Income Decile Group"
        }
    },
    "measures_map": {
        "Median equivalised fuel costs (£)": "Median costs",
        "Median after housing costs (AHC), equivalised income (£)": "Median income",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "Median rating",
        "Median floor area (m2)": "Median floor area"
    },
    "units_map": {
        "Median equivalised fuel costs (£)": "gdp",
        "Median after housing costs (AHC), equivalised income (£)": "gdp",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "rating",
        "Median floor area (m2)": "m2"
    }
}


# In[100]:


# # Fuel payment type
#
# Tables 19 through 20 (the parameters, the processing will happen later on)


# In[101]:


# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
fuel_payment_type_task = {
    "name": "Fuel payment type",
    "store_as": "19through20",
    "tables":
        {
        "Table 19": {
            "sub_table_count": 1,
            "differentiating_dimension": "Payment Method",
            "constant_columns": {
              "Fuel Type": "Gas"
            }
        },
        "Table 20": {
            "sub_table_count": 1,
            "differentiating_dimension": "Payment Method",
            "constant_columns": {
              "Fuel Type": "Electricity"
            }
        }
    },
    "measures_map": {
        "Median equivalised fuel costs (£)": "Median costs",
        "Median after housing costs (AHC), equivalised income (£)": "Median income",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "Median rating",
        "Median floor area (m2)": "Median floor area"
    },
    "units_map": {
        "Median equivalised fuel costs (£)": "gdp",
        "Median after housing costs (AHC), equivalised income (£)": "gdp",
        "Median Fuel Poverty Energy Efficiency Rating (FPEER)": "rating",
        "Median floor area (m2)": "m2"
    }
}


# In[102]:


trace = TransformTrace()
table_dict = {}

# do everything
# for dataset_task in [energy_efficiency_tasks, household_characteristics_tasks, household_income_tasks,fuel_payment_type_tasks]:
for category, dataset_task in {
    "Fuel Payment":fuel_payment_type_task,
    "Household Income": household_income_task,
    "Household Characteristics": household_characteristics_task,
    "Energy Efficiency": energy_efficiency_task
    }.items():

    try:
        subset_of_tabs = [x for x in tabs if x.name.strip() in dataset_task["tables"].keys()]
        for tab in subset_of_tabs:

            # Just specifiy the common dimensions for now
            columns = ["Year", "Measure Type", "Unit"]
            trace.start(category, tab.name, columns, distro.downloadURL)

            # there can only be one style of anchor per sheet
            is_little_table = False
            anchors = tab.filter(BIG_TABLE_ANCHOR)
            if len(anchors) == 0:
                anchors = tab.filter(LITTLE_TABLE_ANCHOR)
                is_little_table = True

            if len(anchors) == 0:
                raise Exception("Cannot find any anchor cells")

            for i, anchor in enumerate(anchors):   # i.e for each sub table on this sheet
                if is_little_table:
                    df, trace = process_little_table(anchor, dataset_task, trace)
                else:
                    df, trace = process_big_table(anchor, dataset_task, trace)

            # Strip any subscript
            # TODO - better
            for col in df.columns.values.tolist():
                new_col = col
                for i in range(0, 10):
                    new_col = new_col.rstrip(str(i))
                df = df.rename(columns={col: new_col})

            # Store however many tabs we've extracted against the specified identifier
            trace.store(dataset_task["store_as"], df)

    except Exception as err:
        raise Exception('Error encountered while processing task "{}" from "{}".'.format(json.dumps(dataset_task["tables"][tab.name]),
                                                                                         dataset_task["name"])) from err
# -
# # CSVW Mapping
#
# We're gonna need quite a lof of mapping for all these datasets, so we'll do it here and pass it around dynamically.
#
# I've broken it down in the `"csvw_common_map"` (for columns that appear in every dataset) a `"csvw_value_map"` and dataset specific maps where necessary.

# +

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
    "Median costs": {
                "unit": "http://gss-data.org.uk/def/concept/measurement-units/gbp",
                "measure": "http://gss-data.org.uk/def/measure/median-costs",
                "datatype": "double"
            },
    "Median income": {
                "unit": "http://gss-data.org.uk/def/concept/measurement-units/gbp",
                "measure": "http://gss-data.org.uk/def/measure/median-income",
                "datatype": "double"
            },
    "Median rating": {
                "unit": "http://gss-data.org.uk/def/concept/measurement-units/rating",
                "measure": "http://gss-data.org.uk/def/measure/median-rating",
                "datatype": "double"
            },
    "Median floor area": {
                "unit": "http://gss-data.org.uk/def/concept/measurement-units/m2",
                "measure": "http://gss-data.org.uk/def/measure/median-floor-area",
                "datatype": "double"
            }
}


# In[103]:


df.head()
df['Category'].unique()

# # Metadata & Joins


# In[104]:


# description we'll add to most joined tables

comment = "Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics	 based on Median Fuel Costs, Income, FPEER Rating and Floor Area"
description = """Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics based on Median Fuel Costs, Income, FPEER Rating and Floor Area,
The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
"""


table_joins = {
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": "1through17",
        "comment": comment,
        "description": description,
        "datasetid": "eedc-fuelcosts"
    },
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": "1through17",
        "comment": comment,
        "description": description,
        "datasetid": "eedc-housingcosts"
    },
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": "1through17",
        "comment": comment,
        "description": description,
        "datasetid": "eedc-fpeer"
    },
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": "1through17",
        "comment": comment,
        "description": description,
        "datasetid": "eedc-floorarea"
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": "12through16",
        "comment": comment,
        "description": description,
        "datasetid": "hoch-fuelcosts"
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": "12through16",
        "comment": comment,
        "description": description,
        "datasetid": "hoch-housingcosts"
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": "12through16",
        "comment": comment,
        "description": description,
        "datasetid": "hoch-fpeer"
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": "12through16",
        "comment": comment,
        "description": description,
        "datasetid": "hoch-floorarea"
    },
    "Fuel poverty supplementary tables - Housing Income - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": "17through18",
        "comment": comment,
        "description": description,
        "datasetid": "hoin-fuelcosts"
    },
    "Fuel poverty supplementary tables - Housing Income - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": "17through18",
        "comment": comment,
        "description": description,
        "datasetid": "hoin-housingcosts"
    },
    "Fuel poverty supplementary tables - Housing Income - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": "17through18",
        "comment": comment,
        "description": description,
        "datasetid": "hoin-fpeer"
    },
    "Fuel poverty supplementary tables - Housing Income - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": "17through18",
        "comment": comment,
        "description": description,
        "datasetid": "hoin-floorarea"
    },
    "Fuel poverty supplementary tables - Fuel Payment Type - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": "19through20",
        "comment": comment,
        "description": description,
        "datasetid": "fupt-fuelcosts"
    },
    "Fuel poverty supplementary tables - Fuel Payment Type - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": "19through20",
        "comment": comment,
        "description": description,
        "datasetid": "fupt-housingcosts"
    },
    "Fuel poverty supplementary tables - Fuel Payment Type - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": "19through20",
        "comment": comment,
        "description": description,
        "datasetid": "fupt-fpeer"
    },
    "Fuel poverty supplementary tables - HFuel Payment Type - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": "19through20",
        "comment": comment,
        "description": description,
        "datasetid": "fupt-floorarea"
    }
}

# Given there are standard column to all datacubes it's easier
# to define the columns we're NOT going to pathify
COLUMNS_TO_NOT_PATHIFY = ["Value", "Period", "Unit", "Measure Type", "Region"]

# Switch for generating codelists (should usually be False)
GENERATE_CODELISTS = False

# Print the mapping where you need to debug stuff
SHOW_MAPPING = True

count = 0

test = {}

# https://staging.gss-data.org.uk/cube/explore?uri=http%3A%2F%2Fgss-data.org.uk%2Fdata%2Fgss_data%2Fedvp%2Fbeis-fuel-poverty-supplementary-tables-2020-catalog-entry
for title, info in table_joins.items():

    #if pathify(title) != "fuel-poverty-supplementary-tables-energy-efficiency-and-dwelling-characteristics-median-after-housing-costs-ahc-equivalised-income":
    #    continue

    df = trace.combine_and_trace(title, info["tables"])

    # slice just the bit we want using category, then drop the column
    df = df[df["Category"] == info["category"]]
    df = df.drop("Category", axis=1)
    trace.Measure_Type('Drop all rows not related to: "{}".'.format(info["category"]))

    # Fill up the sparsity with alls
    df = df.fillna("all")
    for col in df.columns.values:
        df[df[col] == ""] = "all"

    df = df.replace({'Region' : {'all' : 'E92000001',
                                 'East' : 'E12000006',
                                 'East Midlands' : 'E12000004',
                                 'London' : 'E12000007',
                                 'North East' : 'E12000001',
                                 'North West' : 'E12000002',
                                 'South East' : 'E12000008',
                                 'South West' : 'E12000009',
                                 'West Midlands' : 'E12000005',
                                 'Yorkshire and the Humber' : 'E12000003',
                                 'All households' : 'E92000001'},
                     'Dwelling Type' : {'Converted flat2' : 'Converted flat',
                                        'Purpose-built flat': 'Purpose built flat'},
                     'Wall Insulation' : {'Other2' : 'Other'}})

    df = df.rename(columns={'Year' : 'Period'})

    # Metadata etc
    scraper.dataset.title = title
    if "comment" in info.keys():
        scraper.dataset.comment = info["comment"]

    if "description" in info.keys():
        scraper.dataset.description = info["description"]

    from IPython.core.display import HTML
    for col in df:
        if col not in ['Value']:
            df[col] = df[col].astype('category')
            display(HTML(f"<h2>{col}</h2>"))
            display(df[col].cat.categories)

    # Pathify (sometimes generate codelists from) appropriate columns
    for col in df.columns.values.tolist():

        if col in COLUMNS_TO_NOT_PATHIFY:
            continue

        if GENERATE_CODELISTS:
            generate_codelist(title, df, col)

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
            url_title = "beis-fuel-poverty-supplementary-tables-2020"

            for col in df.columns.values.tolist():
                if col not in cols_we_have_a_map_for:
                    mapping[col] = {
                        "parent": "http://gss-data.org.uk/data/gss_data/edvp/{url_title}/concept-scheme/{col}".format(url_title=pathify(url_title), col=pathify(col)),
                        "value": "http://gss-data.org.uk/data/gss_data/edvp/{url_title}/concept/{col}/{{{col_underscored}}}".format(url_title=pathify(url_title), col=pathify(col), col_underscored=pathify(col).replace("-", "_")),
                        "description": ""
                    }

            # "Deprivation Indicator": {
            #            "parent": "http://gss-data.org.uk/data/gss_data/towns-high-streets/sg-scottish-index-of-multiple-deprivation-2020/concept-scheme/deprivation-indicator",
            #            "value": "http://gss-data.org.uk/data/gss_data/towns-high-streets/sg-scottish-index-of-multiple-deprivation-2020/concept/deprivation-indicator/{deprivation_indicator}",
            #            "description": "SIMD is the Scottish Government's standard approach to identify areas of multiple deprivation in Scotland. It can help improve understanding about the outcomes and circumstances of people living in the most deprived areas in Scotland. It can also allow effective targeting of policies and funding where the aim is to wholly or partly tackle or take account of area concentrations of multiple deprivation. SIMD ranks data zones from most deprived (ranked 1) to least deprived (ranked 6,976). People using SIMD will often focus on the data zones below a certain rank, for example, the 5%, 10%, 15% or 20% most deprived data zones in Scotland. SIMD is an area-based measure of relative deprivation: not every person in a highly deprived area will themselves be experiencing high levels of deprivation."
            # },

            # Read the map back into the cubes class
            # info_json["transform"]["columns"] = mapping
            # cubes.info = info_json

        #if SHOW_MAPPING:
        #    print("Mapping for: ", title)
        #    print(json.dumps(mapping, indent=2))
        #    print("\n")

    # FOR NOW - remove measure type
    df = df.drop("Measure Type", axis=1)
    df = df.drop("Unit", axis=1)

    df = df.drop_duplicates()

    #csvName = "{}.csv".format(pathify(title))
    csvName = "observations{}.csv".format(pathify(info['datasetid']))
    out = Path('out')
    out.mkdir(exist_ok=True)
    #joined_dat.drop_duplicates().to_csv(out / csvName, index = False)
    df.drop_duplicates().to_csv(out / (csvName), index = False)

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + '/' + info['datasetid']# differentiating name goes here + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    from urllib.parse import urljoin

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform._mapping = mapping
    #csvw_transform.set_mapping(coldef)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())


# In[105]:


#cubes.output_all()
# cubes.base_url = "http://gss-data.org.uk/data/gss_data/edvp/beis-fuel-poverty-supplementary-tables-2020"
#cubes.cubes[0].multi_trig = scraper.generate_trig()
#cubes.cubes[0].output(Path("./out"), False, cubes.info, False)
trace.render("spec_v1.html")
#

# http://gss-data.org.uk/data/data/gss_data/edvp/beis-fuel-poverty-supplementary-tables-2020/fuel-poverty-supplementary-tables-energy-efficiency-and-dwelling-characteristics-median-after-housing-costs-ahc-equivalised-income#dimension


"""
import os
path = os.getcwd() + '/codelists2'
files = os.listdir(path)


for index, file in enumerate(files):
    print(file)
    newNme = file.replace("fuel-poverty-supplementary-tables-housing-income-median-floor-area-","")
    os.rename(os.path.join(path, file), os.path.join(path, newNme))
"""


# In[105]:







