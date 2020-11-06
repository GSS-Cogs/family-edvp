# -*- coding: utf-8 -*-
from gssutils import * 
import json

# # Helpers
#
# These are all the same two variations of table repeated, so we're just gonna have a function for each

# +
LITTLE_TABLE_ANCHOR = "Median equivalised fuel costs (£)"
BIG_TABLE_ANCHOR = "Proportion of households within group (%)" # note we dont want this cell but we're using it to differentiate the styles of table - 

def process_little_table(anchor, task, trace):
    """
    Given a single anchoring cell, process the smaller style of the tables
    """
    year = "year/"+tab.excel_ref('A1').value.split(",")[-1]
    
    # Get the obs, we don't want columns f + G
    # TODO - safety to make sure F & G actually are the columns we don't want for a given table 
    obs = anchor.shift(DOWN).expand(RIGHT).expand(DOWN).is_not_blank()
    obs = obs - tab.excel_ref('F:G')
    obs = clean_lower_tables(obs)

    horizontal_dimension = anchor.expand(RIGHT).is_not_blank()

    left_column = anchor.shift(LEFT).fill(DOWN).is_not_blank()
    left_column = clean_lower_tables(left_column)

    measure_type = anchor.fill(RIGHT)

    dimensions = [
        HDimConst("Period", year),
        HDim(horizontal_dimension, "Category", DIRECTLY, ABOVE),
        HDim(left_column, task["tables"][tab.name]["differentiating_dimension"], DIRECTLY, LEFT)
    ]

    cs = ConversionSegment(obs, dimensions)
    df = cs.topandas()
    
    # Pathify the differentiating dimension, switch all-hosueholds to all
    df[task["tables"][tab.name]["differentiating_dimension"]] = df[task["tables"][tab.name]["differentiating_dimension"]].apply(pathify)
    df[task["tables"][tab.name]["differentiating_dimension"]] = df[task["tables"][tab.name]["differentiating_dimension"]] \
            .map(lambda x: x.replace("all-households", "all"))

    # Measure and Unit
    df["Unit"] = df["Category"].apply(LookupFromDict("unit", task["units_map"]))
    df["Measure Type"] = df["Category"].apply(LookupFromDict("measure", task["measures_map"]))

    # Add the constant column
    if "constant_columns" in task["tables"][tab.name].keys():
        for k,v in task["tables"][tab.name]["constant_columns"].items():
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
    
    
def clean_lower_tables(bag):
    """
    Cut everything below the relevant "All households" line
    """
    return bag -bag.expand(DOWN).expand(LEFT).filter("All households").by_index(1).fill(DOWN).expand(RIGHT)

# TODO - there's gotta be a baked in pandas method for this im not remembering, look it up, kiss etc
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



# -

scraper = Scraper(seed="info.json")   
scraper


distro = scraper.distribution(latest=True)
tabs = distro.as_databaker()
tabs = [x for x in tabs if "Table" in x.name] # TODO = typos? Tables change? Numnbering of tables by concept changes?

# # Energy Efficiency and Dwelling Characteristics
#
# Tables 1 through 11 (the parameters, the processing will happen later on)

# +

# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
energy_efficiency_task = {
    "name": "Energy Efficiency",
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
# -


# # Household characteristics
#
# Tables 12 through 16 (the parameters, the processing will happen later on)

# +

# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
household_characteristics_task = {
    "name": "Household characteristics",
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
# -

# # Household income
#
# Tables 17 through 18 (the parameters, the processing will happen later on)

# +

# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
household_income_task = {
    "name": "Household income",
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
# -

# # Fuel payment type
#
# Tables 19 through 20 (the parameters, the processing will happen later on)

# +

# We're just gonna loop and use slightly different variables each time.
# If you need yo tweak anything you should be able to do it here.
fuel_payment_type_task = {
    "name": "Fuel payment type",
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

# +

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
            
            trace.start(tab.name, tab.name, [], distro.downloadURL)

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
                
                
                table_dict[tab.name] = df

    except Exception as err:
        raise Exception('Error encountered while processing task "{}" from "{}".'.format(json.dumps(dataset_task["tables"][tab.name]), 
                                                                                         dataset_task["name"])) from err
# -
# # Joins

# +
# dictionary of what needs joining to what
#
# <output name> : {
#    "category": <what ever measure we're joining on",    # column name from where the data came from, we'll drop this after the joins
#    "tables": "whichever tables we're gettign the measure from"
# }

table_joins = {
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": ["Table 1", "Table 2", "Table 3", "Table 4", "Table 5", "Table 6",
                  "Table 7", "Table 8", "Table 9", "Table 10", "Table 11"]
    },
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": ["Table 1", "Table 2", "Table 3", "Table 4", "Table 5", "Table 6",
                  "Table 7", "Table 8", "Table 9", "Table 10", "Table 11"]
    },
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": ["Table 1", "Table 2", "Table 3", "Table 4", "Table 5", "Table 6",
                  "Table 7", "Table 8", "Table 9", "Table 10", "Table 11"]
    },
    "Fuel poverty supplementary tables - Energy Efficiency and Dwelling Characteristics - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": ["Table 1", "Table 2", "Table 3", "Table 4", "Table 5", "Table 6",
                  "Table 7", "Table 8", "Table 9", "Table 10", "Table 11"]
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": ["Table 12", "Table 13", "Table 14", "Table 15", "Table 16"]
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": ["Table 12", "Table 13", "Table 14", "Table 15", "Table 16"]
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": ["Table 12", "Table 13", "Table 14", "Table 15", "Table 16"]
    },
    "Fuel poverty supplementary tables - Housing Characteristics - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": ["Table 12", "Table 13", "Table 14", "Table 15", "Table 16"]
    },
    "Fuel poverty supplementary tables - Housing Income - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": ["Table 17", "Table 18"]
    },
    "Fuel poverty supplementary tables - Housing Income - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": ["Table 17", "Table 18"]
    },
    "Fuel poverty supplementary tables - Housing Income - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": ["Table 17", "Table 18"]
    },
    "Fuel poverty supplementary tables - Housing Income - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": ["Table 17", "Table 18"]
    },
    "Fuel poverty supplementary tables - Fuel Payment Type - Median equivalised fuel costs": {
        "category": "Median equivalised fuel costs (£)",
        "tables": ["Table 19", "Table 20"]
    },
    "Fuel poverty supplementary tables - Fuel Payment Type - Median after housing costs (AHC), equivalised income": {
        "category": "Median after housing costs (AHC), equivalised income (£)",
        "tables": ["Table 19", "Table 20"]
    },
    "Fuel poverty supplementary tables - Fuel Payment Type - Median Fuel Poverty Energy Efficiency Rating (FPEER)": {
        "category": "Median Fuel Poverty Energy Efficiency Rating (FPEER)1",
        "tables": ["Table 19", "Table 20"]
    },
    "Fuel poverty supplementary tables - HFuel Payment Type - Median floor area": {
        "category": "Median floor area (m2)",
        "tables": ["Table 19", "Table 20"]
    } 
} 

for title, info in table_joins.items():
    
    dfs_to_join = []
    for table_wanted in info["tables"]:
        df = table_dict[table_wanted]
        df.to_csv("temp.csv", index=False)
        df = df[df["Category"] == info["category"]]
        
        # Drop the no longer needed category column
        df = df.drop("Category", axis=1)
        dfs_to_join.append(df)
    
    df = pd.concat(dfs_to_join)
    
    # Fill up the sparsity with alls
    df = df.fillna("all")
    for col in df.columns.values:
        df[df[col] == ""] = "all"
        
    df.drop_duplicates().to_csv('./out/{}.csv'.format(title), index=False)

# -
trace.render("spec_v1.html")

