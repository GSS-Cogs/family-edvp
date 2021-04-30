# COGS Dataset Specification


## BEIS RHI monthly deployment data   Month Year   Annual edition 

[Landing Page](https://www.gov.uk/government/collections/renewable-heat-incentive-statistics)

[Transform Flowchart](https://gss-cogs.github.io/family-EDVP/datasets/specflowcharts.html?BEIS-RHI-monthly-deployment-data-Month-Year-Annual-edition/flowchart.ttl)

## The following tables will result in 2 datasets being output one for application numbers and one for capacity in MW
### Non-Domestic
### Sheet: 1.1 Number of applications and total capacity by technology type, Great Britain, November 2011 to February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns B, G, L, Q
		Capacity MW: Columns D, I, N, T

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Technology Type (A7:A18) {Codelist, might already be one for this as it follows Ofgem tariff bands}
		Row 5: Application Type (B5:T5) {Codelist}

	Add Dimensions
		Geography with code for Great Britain
		Application Status with value "all"
		SIC with value "total"
		Measure Type with values "applications" and "mw"

	Footnotes
		footnote 1 needs to be added to the codelist definition json file
		
### Sheet: 1.2 Application status, Great Britain, November 2011 to February 2021

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Application Type (A7:A12) {Codelist}
		Row 5: Application Type (B5:T5) {Codelist}

	Add Dimensions
		Technology Type with value "total""
		Geography with code for Great Britain
		SIC with value "total"
		Measure Type with values "applications"

### Sheet: 1.3 Number of applications and capacity by region, Great Britain, November 2011 to February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns C, F
		Capacity MW: Columns I, L

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Geography (A7:A18), ignore Region column {Geography codelist already in use}
		Row 5: Application Type (C5:L5) {Codelist}

	Add Dimensions
		Technology Type with value "total"
		Application Status with value "all"
		SIC with value "total"
		Measure Type with values "applications" and "mw"

### Sheet 1.4 Number of accredited applications and installed capacity by local authority, Great Britain, November 2011 to February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns E
		Capacity MW: Columns F

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Geography (A7:A420), ignore area name column {Geography codelist already in use}
		Row 5: Application Type (C5:L5) {Codelist}

	Add Dimensions
		Technology Type with value "total"
		Application Status with value "all"
		SIC with value "total"
		Measure Type with values "applications" and "mw"
	
### Sheet 1.6 Number of tariff guarantee applications by tariff band, Great Britain, at end-February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns B, H, N, T
		Capacity MW: Columns E, K, Q, W
		
	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Technology Type (Change from Tariff band) (A10:A16) {Codelist}
		Row 8: Application Type (B8:W8)

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Measure Type with values "applications" and "mw"

	GUIDANCE NOTES UNDER THE TITLE NEED TO BE ADDED TO DESCRIPTION

### Sheet M1.1 Number of full applications, number of accredited full applications, and installed capacity per month, Great Britain, November 2011 to February 2021

	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns D, H
		Capacity MW: Columns F, J
				
	Skip cumulative columns

	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Application Type (D5:J5) {codelist} has added (by date of first submission) keep for now

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Technology Type with value "total"
		Geography with code for Great Britain
		Measure Type with values "applications" and "mw"

### Sheet M1.2 - Number of full applications (by date of first submission), by technology, per month, Great Britain, November 2011 to February 2021
			
	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Technology Type (D5:O5) {codelist} 

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Application Type with value "Number of full applications (by date of first submission)"
		Geography with code for Great Britain
		Measure Type with values "applications"

### Sheet M1.3 - Capacity of full applications (MW) (by date of first submission), by technology, per month, Great Britain, November 2011 to February 2021

	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Technology Type (D5:O5) {codelist}

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Application Type with value " Capacity of full applications (MW) (by date of first submission)"
		Geography with code for Great Britain
		Measure Type with values "mw"

### Sheet M1.4 - Number of TG applications (by date of first submission), by technology, per month, Great Britain, November 2011 to February 2021

	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Technology Type (D5:J5) {codelist} has added (by date of first submission) keep for now

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Application Type with value "Number of Tariff Guarantee Applications"
		Geography with code for Great Britain
		Measure Type with values "applications"

### Sheet Q1.1 - Number of full applications, number of accreditations, and installed capacity per quarter Great Britain, November 2011 to December 2020
			
	2 dimensions in dataset to be split out into 2 datasets after joining with other tables: 
		Applications: Columns D, H
		Capacity MW: Columns F, J
				
	Skip cumulative columns

	Dimensions
		Column A & B: Period: convert year and quarter to suitable format (quarter/yyyy-Qq)
		Row 5: Application Type (D5:J5) {codelist} has added (by date of first submission) keep for now

	Add Dimensions
		Application Status with value "all"
		SIC with value "total"
		Technology Type with value "total"
		Geography with code for Great Britain
		Measure Type with values "applications" and "mw"


### Joined Dataset 1 & 2

	Join all tables detailed above, 1.1, 1.2, 1.3, 1.4, 1.6, M1.1, M1.2, M1.3, M1.4, Q1.1
		
	Then split into 2 datasets by Measure Type: applications & MW
	
	For the Application dataset add a Dimension so it can be joined to another one later on:
		Applicant with value "non-domestic" {codelist}

	For the MW dataset remove dimension Application Status as it should only have one value

	Application (1) dataset to be with dataset 3
	
	MW Dataset (2)
	Scraper
	Title:
		RHI deployment data - Capacity (MW)
	Comment:
		Capacity (MW) statistics for the Renewable Heat Incentive (RHI) programme
	Description:
		Capacity (MW) statistics for the Renewable Heat Incentive (RHI) programme on technology type, region, local authority  
		ALL FOOTNOTES TO BE ADDED TO DESCRIPTION but some wording will have to be altered


	Wordings in some dimensions will have to be changed but will figure that out when we can see the output
	Footnotes need to be altered to suit

----------------------------------------------------
## Domestic
### Sheet 2.1 - Number of applications and accreditations by technology type, Great Britain, April 2014 to February 2021

	3 Tables with 2 dimensions: 
		Applications: Columns B, E  
		Capacity of Accredited Applications MW: Column H

	Skip percentage and MW columns columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Columns A8:A12, A17:A21, A26:A30: Technology Type {codelist}
		Rows 5, 14, 23: Installation {Codelist: Total, New, Legacy}

	Add Dimension
		Application Status with value "all"
		Geography with code for Great Britain

### Sheet 2.2 - Application status by technology, Great Britain, April 2014 to February 2021

	Skip percentage columns/rows

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A7:!5: Technology Type - change Tariff Band {Codelist}
		Row C6:H6: Application Status {codelist}

	Add Dimension
		Application Type with value "all"
		Geography with code for Great Britain

### Sheet 2.3 - Number of applications and accredited applications by region, Great Britain, April 2014 to February 2021

	Skip percentages
	
	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A8:A20: Geography, Change Total to Great Britain code. Ignore column B (codelist already in use)
		Row C5:AA5: Technology Type
		Row F6:AD6: Application Type

	Add Dimension
		Technology Type with value "total"
		Application Status with value "all"

### Sheet 2.4 - Number of accreditations by local authority, Great Britain, April 2014 to February 2021
	
	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A8:A420: Geography. Ignore columns B & C (codelist already in use)
		Row E5: Application Type
		
	Add Dimensions
		Technology Type with value "total"
		Application Status with value "all"


### Sheet M2.1 - Number of applications and accreditations per month Great Britain, April 2014 to February 2021

	Ignore cumulative columns

	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Application Type

	Add Dimension
		Technology Type with value "all"
		Application Status with value "all"
		Geography with code for Great Britain


### Sheet M2.2 - Number of applications and accreditations per month by technology, Great Britain, April 2014 to February 2021

	Dimensions
		Column A & B: Period: convert year and month to suitable format (month/yyyy-mm)
		Row 5: Application Type {codelist}
		Row 6: Technology Type {codelist}

	Add Dimension
		Application Status with value "all"
		Geography with code for Great Britain


### Sheet Q2.1 - Number of applications and accreditations per quarter Great Britain, April 2014 to December 2020

	Ignore cumulative columns

	Dimensions
		Column A & B: Period: convert year and quarter to suitable format (month/yyyy-Qq)
		Row 5: Application Type

	Add Dimension
		Technology Type with value "all"
		Application Status with value "all"
		Geography with code for Great Britain


### Sheet Q2.2 - Number of applications and accreditations per quarter by technology, Great Britain, April 2014 to December 2020

	Dimensions
		Column A & B: Period: convert year and quarter to suitable format (month/yyyy-Qq)
		Row 5: Application Type {codelist}
		Row 6: Technology Type {codelist}

	Add Dimension
		Application Status with value "all"
		Geography with code for Great Britain

		
### Joined Dataset 3

	Join all tables detailed above, 2.1, 2.2, 2.3, 2.4, M2.1, M2.2, Q2.1, Q2.2

	Should only be application data in this dataset and will be added to dataset 1

	Add Dimension:
		Applicant with value "domestic" {codelist}


## Join datasets 1 and 3 together

	Scraper
	Title:
		RHI deployment data - Application Numbers, domestic and non-domestic
	Comment:
		Application statistics for the Renewable Heat Incentive (RHI) programme
	Description:
		Application statistics for the Renewable Heat Incentive (RHI) programme by technology type, region, local authority & domestic and non-domestic

	Wordings in some dimensions will have to be changed but will figure that out when we can see the output
	Footnotes need to be altered to suit and added to description




----------------------------------------------------



----------------------------------------------------
## Dataset 4
### Sheet 1.7 Number and capacity of accredited installations and heat generated by Standard Industrial Classification Code (SIC), Great Britain, November 2011 to February 2021

	3 dimensions in dataset : 
		Installations: Column C 
		Capacity MW: Column E
		Heat paid for GWh: Column G

	Marker
		Replace any # values with empty string and put suppressed in Marker column
		
	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: SIC Code (A7:A95) ignore description column {SIC Codelist} probably not a code for total so might have to leave out or create new codelist
		Row 5: Installation Type (C5:G5)

	Measure Type with value "count"
	Unit = "Installations" (this is a multi-unit dataset but will just go with this for now)
		
	SIC CODES WEB ADDRESS FOR SIC CODES IN FOOTNOTES

----------------------------------------------------

### Sheet 1.5 Heat generated and paid for by technology, Great Britain, November 2011 to February 2021

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A: Technology Type (A7:A18) {Codelist, might already be one for this as it follows Ofgem tariff bands}

	Footnotes
		All footnotes need to be added to scraper description

	Measure Type: generated-heat
	Unit: kWh

	Scraper:
		Title: 
			RHI deployment data - Heat generated and paid for by technology, Great Britain
		Comment:
			Statistics for the Renewable Heat Incentive (RHI) programme. Heat generated and paid for by technology, Great Britain
		Description
			Statistics for the Renewable Heat Incentive (RHI) programme. Heat generated and paid for by technology, Great Britain
			These statistics provide an update on the uptake of both the non-domestic and domestic Renewable Heat Incentive (RHI) schemes
			PLUS FOOTNOTES

### Sheet 2.5 - Heat generated and paid for by technology, Great Britain, April 2014 to February 2021

	Skip percentage columns

	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Column A7:A18: Technology Type, change from Tariff Band
	
----------------------------------------------------

### Sheet 2.6 - Average capacity and design SPF¹ values, Great Britain, April 2014 to February 2021

	Skip Median and SPF columns
	
	Dimensions
		Period: from title (November 2011 to February 2021), convert to suitable format
		Columns A8:A11, A16:A19, A24:A27: Technology Type, change form Tariff Band {codelist}

			

##### DM Notes

		notes

