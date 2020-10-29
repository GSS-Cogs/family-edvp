# COGS Dataset Specification

[Family Home](https://gss-cogs.github.io/family-EDVP/datasets/specmenu.html)

[Family Transform Status](https://gss-cogs.github.io/family-EDVP/datasets/index.html)

## BEIS Fuel poverty detailed tables 2020 

[Landing Page](https://www.gov.uk/government/statistics/fuel-poverty-detailed-tables-2020)

[Transform Flowchart](https://gss-cogs.github.io/family-EDVP/datasets/specflowcharts.html?BEIS-Fuel-poverty-detailed-tables-2020/flowchart.ttl)

#### Datasets

#### Low Income High costs Matrix

	Tables: 2

	Dimensions:
		Year: 2018
		Low Income High costs Matrix (codelist/pathify):
			Low Income High Costs
			Low Income Low Costs
			High Income High Costs
			High Income Low Costs
			All households = All
	Attributes:
		Number of Households
	Measures:
		Measure Type:  
			Median Income after housing costs (AHC), equivalised income
			Median Equivalised fuel costs
		Unit: gbp & rating
		
	Table Structure
		Year, Low Income High costs Matrix, Number of Households, Measure Type, Unit, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-detailed-tables-2020/matrixincome
		Dataset-title 2: beis-fuel-poverty-detailed-tables-2020/matrixcosts
		Title1: Fuel poverty detailed tables - Low Income High costs Matrix - Median Equivalised Income
		Title1: Fuel poverty detailed tables - Low Income High costs Matrix - Median Equivalised fuel costs
		Comment: Fuel poverty statistics report for the Low Income high Costs Matrix (LIHC) Indicator
		Description:
			Fuel poverty statistics report for the Low Income high Costs Matrix (LIHC) Indicator 
			Households are considered to be fuel poor if:
			• they have required fuel costs that are above average (the national median level); and
			• were they to spend that amount, they would be left with a residual income below the official poverty line.
			The depth of fuel poverty is defined as the amount by which the assessed energy requirements of fuel poor households exceed the threshold for reasonable costs. This is referred to as the fuel poverty gap.
			
			Fuel Poverty methodology handbook:
			https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/882233/fuel-poverty-methodology-handbook-2020.pdf
			
			The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv
			

#### Energy Efficiency and Dwelling Characteristics

	Tables: 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17

	ONLY INTERESTED IN THE MAIN MEASURE COLUMN AND THE COLUMNS:
		Number of households: Not fuel poor, fuel poor
		Aggregate fuel poverty gap (£m)
		Average fuel poverty gap (£)
	OTHER COLUMNS CAN BE DERIVED
	
	TABLE WILL BE SPARSE IN PLACES
		
	Dimensions:
		Year: 2018
		FPEER (codelist): A/B/C, D, E, F, G, All
		SAP BAND (codelist): A/B/C, D, E, F, G, All
		Rurality (codelist/pathify): Urban, Semi-rural, Rural, All
		Region (codelist): replace regions with ONS geography codes (All households will be code for England)
		Dwelling Type (codelist/pathify): Converted Flat, etc. (All Households = all) (remove superscripts)
		Dwelling Age (codelist/pathify): Pre 1919, etc. (All Households = all)
		Floor Area (codelist/pathify): Less than 50 sqm, etc. (All Households = all)
		Gas Grid Connection (codelist): Yes, No, Total (Y|N|T) (could maybe represent this through an already defined ontology)
		Central Heating {Table 11 & 13} (codelist/pathify): Central heating, etc. (All Households = all)
		Main Fuel Type {Table 12 & 13} (codelist/pathify): Gas, etc. (All Households = all)
		Boiler Type (codelist/pathify): Standard boiler (floor or wall), etc. (All Households = all)
		Wall Insulation (codelist/pathify): Cavity uninsulated, etc. (All Households = all)
		Wall Type (codelist/pathify): Cavity wall predominant, etc. (All Households = all)
		Loft Insulation (codelist/pathify): Not applicable, etc. All Households = all)
	Attributes:
		Households in Fuel Poverty
		Households not in Fuel Poverty
	Measures:
		Measure Type:  
			Aggregate fuel poverty Gap
			Average fuel poverty Gap
		Unit: million-gbp, gbp
	Marker:
		^ number based on low sample count (between 10 and less than 30), inferences should not be made based on this figure. = low-sample-count
		* numbers hidden due to very low sample count (less than 10) within this category. = low-sample-count		
		
	Table Structure
		Year, FPEER, SAP Band, Rurality, Region, Dwelling Type, Dwelling Age, Floor Area, Gas Grid Connection, Central Heating, Main Fuel Type, Boiler Type, Wall Insulation, Wall Type, Loft Insulation, Households in Fuel Poverty, Households not in Fuel Poverty, Measure Type, Unit, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-detailed-tables-2020/energyagg
		Dataset-title 2: beis-fuel-poverty-detailed-tables-2020/energyavg
		Title 1: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Aggregate Gap
		Title 2: Fuel poverty detailed tables - Energy Efficiency and Dwelling Characteristics - Average Gap
		Comment: Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics		
		Description: 
		Fuel poverty statistics report detailing Energy Efficiency and Dwelling Characteristics
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv

#### Household characteristics

	Tables: 1, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28

	ONLY INTERESTED IN THE MAIN MEASURE COLUMN AND THE COLUMNS:
		Number of households: Not fuel poor, fuel poor
		Aggregate fuel poverty gap (£m)
		Average fuel poverty gap (£)
	OTHER COLUMNS CAN BE DERIVED
	
	TABLE WILL BE SPARSE IN PLACES
		
	Dimensions:
		Year: 2018
		FPEER (codelist): A/B/C, D, E, F, G, All
		Tenure (codelist/pathify): Owner occupied, etc. (All Households = all)
		Housing Sector (codelist/pathify): Private Sector, Social Sector, All
		Household Composition (codelist/pathify): Couple with dependent child(ren), etc. (All Households = all)
		Age of Youngest Person (codelist, combine with oldest): 0-4 etc. (All Households = all) (reformat age ranges: Y0T4). Add a not-applicable category for 'Age of Oldest' values.
		Age of Oldest Person (codelist, combine with youngest): 16-24 etc. (All Households = all) (reformat age ranges: Y16T24). Add a not-applicable category for 'Age of Youngest values.
		People in Household (codelist/pathify): 1, 2, 3, 4, 5 or more (All Households = all)
		Ethnicity (codelist/pathify): Ethnic minority, White  (All Households = all)
		Illness or Disability (codelsit/pathify): Yes, No (Y|N) (All Households = T)
		Under-Occupancy: (codelist/pathify): Not under-occupying, etc. (All Households = all)
		Vulnerability (codelist/pathify): Not Vulnerable, Vulnerable (N|Y) (All Households = T, Vulnerable households only = Y)	
	Attributes:
		Households in Fuel Poverty
		Households not in Fuel Poverty
	Measures:
		Measure Type:  
			Aggregate fuel poverty Gap
			Average fuel poverty Gap
		Unit: million-gbp, gbp
	Marker:
		^ number based on low sample count (between 10 and less than 30), inferences should not be made based on this figure. = low-sample-count
		* numbers hidden due to very low sample count (less than 10) within this category. = low-sample-count		
		
	Table Structure
		Year, FPEER, Tenure, Housing Composition, Age of Youngest Person, Age of Oldest Person, People in Household, Ethnicity, Illness or Disability, Under-Occupancy, Vulnerability, Households in Fuel Poverty, Households not in Fuel Poverty, Measure Type, Unit, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-detailed-tables-2020/characteristicsagg
		Dataset-title 2: beis-fuel-poverty-detailed-tables-2020/characteristicsavg
		Title 1: Fuel poverty detailed tables - Household Characteristics - Aggregate Gap
		Title 2: Fuel poverty detailed tables - Household Characteristics - Average Gap
		Comment: Fuel poverty statistics report detailing Household characteristic
		Description:
		Fuel poverty statistics report detailing Household characteristic
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv

#### Household Income

	Tables: 29, 30

	ONLY INTERESTED IN THE MAIN MEASURE COLUMN AND THE COLUMNS:
		Number of households: Not fuel poor, fuel poor
		Aggregate fuel poverty gap (£m)
		Average fuel poverty gap (£)
	OTHER COLUMNS CAN BE DERIVED
	
	Dimensions:
		Year: 2018
		FPEER (codelist): A/B/C, D, E, F/G, All
		Employment Status (codelist/pathify): Full-time work, etc. (All Households = all)	
		Income Decile Group (codelist/pathify): 1st decile - lowest income, etc. (All Households = all)
	Attributes:
		Households in Fuel Poverty
		Households not in Fuel Poverty
	Measures:
		Measure Type:  
			Aggregate fuel poverty Gap
			Average fuel poverty Gap
		Unit: million-gbp, gbp
	Marker:
		^ number based on low sample count (between 10 and less than 30), inferences should not be made based on this figure. = low-sample-count
		* numbers hidden due to very low sample count (less than 10) within this category. = low-sample-count		
		
	Table Structure
		Year, FPEER, Employment Status, Income Decile Group, Households in Fuel Poverty, Households not in Fuel Poverty, Measure Type, Unit, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-detailed-tables-2020/incomeagg
		Dataset-title 2: beis-fuel-poverty-detailed-tables-2020/incomeavg
		Title 1: Fuel poverty detailed tables - Household Income - Aggregate Gap
		Title 2: Fuel poverty detailed tables - Household Income - Average Gap
		Comment: Fuel poverty statistics report detailing Household Income
		Description:
		Fuel poverty statistics report detailing Household Income
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv

#### Fuel Payment Type

	Tables: 31, 32

	ONLY INTERESTED IN THE MAIN MEASURE COLUMN AND THE COLUMNS:
		Number of households: Not fuel poor, fuel poor
		Aggregate fuel poverty gap (£m)
		Average fuel poverty gap (£)
	OTHER COLUMNS CAN BE DERIVED

	Dimensions:
		Year: 2018
		Fuel Type (codelist/pathify): Gas, Electric
		Payment Method (codelist/pathify): Direct debit, etc. (All Households = all) from both table (31, 32).
	Attributes:
		Households in Fuel Poverty
		Households not in Fuel Poverty
	Measures:
		Measure Type:  
			Aggregate fuel poverty Gap
			Average fuel poverty Gap
		Unit: million-gbp, gbp
	Marker:
		^ number based on low sample count (between 10 and less than 30), inferences should not be made based on this figure. = low-sample-count
		* numbers hidden due to very low sample count (less than 10) within this category. = low-sample-count		
		
	Table Structure
		Year, Fuel Type, Payment Method, Households in Fuel Poverty, Households not in Fuel Poverty, Measure Type, Unit, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-detailed-tables-2020/paymentagg
		Dataset-title 2: beis-fuel-poverty-detailed-tables-2020/paymentavg
		Title 1: Fuel poverty detailed tables - Fuel Payment Type - Aggregate Gap
		Title 2: Fuel poverty detailed tables - Fuel Payment Type - Average Gap
		Comment: Fuel poverty statistics report detailing Fuel Payment Type
		Description:
		Fuel poverty statistics report detailing Fuel Payment Type
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv

#### Eligibility

	Tables: 33, 34, 35, 36

	ONLY INTERESTED IN THE MAIN MEASURE COLUMN AND THE COLUMNS:
		Number of households: Not fuel poor, fuel poor
		Aggregate fuel poverty gap (£m)
		Average fuel poverty gap (£)
	OTHER COLUMNS CAN BE DERIVED

	Dimensions:
		Year: 2018
		Eligibility Type (codelist/pathify): ECO affordable warmth, ECO 3 Help to Heat Group, WHD broader group, In receipt of benefits (All Households = all)
		Eligible (codelist): Yes, No (Y|N) (All Households = T) 
	Attributes:
		Households in Fuel Poverty
		Households not in Fuel Poverty
	Measures:
		Measure Type:  
			Aggregate fuel poverty Gap
			Average fuel poverty Gap
		Unit: million-gbp, gbp
	Marker:
		^ number based on low sample count (between 10 and less than 30), inferences should not be made based on this figure. = low-sample-count
		* numbers hidden due to very low sample count (less than 10) within this category. = low-sample-count		
		
	Table Structure
		Year, Eligibility Type, Eligible, Households in Fuel Poverty, Households not in Fuel Poverty, Measure Type, Unit, Marker, Value

	Scraper
		Dataset-title 1: beis-fuel-poverty-detailed-tables-2020/eligibilityagg
		Dataset-title 2: beis-fuel-poverty-detailed-tables-2020/eligibilityavg
		Title 1: Fuel poverty detailed tables - Eligibility - Aggregate Gap
		Title 2: Fuel poverty detailed tables - Eligibility = Average Gap
		Comment: Fuel poverty statistics report detailing Eligibility
		Description:
		Fuel poverty statistics report detailing Eligibility		
		The Government is interested in the amount of energy households need to consume to have a warm, well-lit home, with hot water for everyday use, and the running of appliances. Therefore fuel poverty is measured based on required energy bills rather than actual spending. This ensures that those households who have low energy bills simply because they actively limit their use of energy at home, for example, by not heating their home are not overlooked. A methodology handbook has been published alongside this publication. This sets out the method for calculating the headline statistics using the LIHC indicator and the detailed methodology for calculating the income, energy efficiency and fuel prices for each household. It is available at:
		https://www.gov.uk/government/publications/fuel-poverty-statistics-methodology-handbook
		Family: edv

##### Footnotes

		All footnotes from every sheet should be included in its respective scraper description apart from the information that informs the Marker column

##### DM Notes

		All datasets need to be split into 2 as we can't currently manage multiple measure cubes. 
		Split into:
			Aggregate fuel poverty Gap
			Average fuel poverty Gap
		You using the CSVMapping class you need to pull in the info.json file into a dict change the Measure Type and unit and pass the dict to the Mapping class.


