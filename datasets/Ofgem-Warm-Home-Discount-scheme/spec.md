# COGS Dataset Specification

[Family Transform Status](https://gss-cogs.github.io/family-EDVP/datasets/index.html)

## OFGEM Warm Home Discount scheme 

[Landing Page](https://www.ofgem.gov.uk/environmental-programmes/social-programmes/warm-home-discount/warm-home-discount-reports-and-statistics)


#### Warm Home Discount: Distribution of expenditure by year (%)

	Dimensions
		Dimension_1: rename as Support Element
		Spending Proportion: Split out into 2 columns:
			Scheme Year: alter values to just: year-1,year-2,year-3, etc.
			Period, format as Gregorian-interval with relevant amount of days or months: 
				1. 1 April 2011 to 31 March 2012
				2. 1 April 2012 to 31 March 2013
				3. 1 April 2013 to 31 March 2014
				4. 1 April 2014 to 31 March 2015
				5. 1 April 2015 to 31 March 2016
				6. 1 July 2016 to 31 May 2017 *
				7. 1 June 2017 to 31 March 2018
				8. 15 August 2018 to 31 March 2019 **
			
			* Due to delays in bringing the regulations into force for the sixth scheme period, a decision was taken to set the scheme period for SY6 from July 2016 to May 2017.
			** Delays in bringing amended WHD Regulations into force for the eighth scheme period delayed the start date of the eighth scheme period and as such, a decision was taken to set the scheme period for SY8 from August 2018 to March 2019. 
	Marker
		Add not-applicable to any empty values	
	Measures:
		Measure Type: expenditure
		Unit: percentage
	Scraper:
		dataset_path: gss_data/energy/ofgem-warm-home-discount-scheme/percentageexpenditure
		Title: Warm Home Discount: Distribution of expenditure by year
		Comment: 
		Distribution of expenditure for each year so far of the Warm Home Discount (WHD), a government energy scheme 	which aims to help people who are in fuel poverty or are at risk of it.
		Description:	
		Distribution of expenditure for each year so far of the Warm Home Discount (WHD), a government energy scheme which aims to help people who are in fuel poverty or are at risk of it.
		The scheme focuses spending against three different support elements, categorised by a ‘core group’, ‘broader group’ and ‘industry initiatives’. ‘Legacy spending’ applied in scheme years 1 to 3.
		Energy suppliers with over 250,000 domestic customers (referred to as ‘large suppliers’) are obligated to participate in each element of the scheme. Some suppliers with a smaller customer base also voluntarily participate. They only take part in the ‘core group’.
		For more on the scheme elements and how they work, see our overview page at Warm Home Discount:
		https://www.ofgem.gov.uk/environmental-programmes/social-programmes/warm-home-discount-whd
		We update this chart on an annual basis. 	

	Table 1 Structure
		Period, Scheme Year, Support Element, Marker, Value 

#### Sheet: Warm Home Discount: Total expenditure by obligated suppliers in scheme year 8 (2018-19)

	Dimensions:
		Dimension_1: rename as Support Element
		Add Period column with Gregorian-interval value for 15 August 2018 to 31 March 2019 (months or days)
		Add 'Scheme Year' column with value year-8 
	Marker
		Add not-applicable to any empty values
	Measures:
		Measure Type: expenditure
		Unit: gbp
	 dataset_path: gss_data/energy/ofgem-warm-home-discount-scheme/gbpexpenditure
		Title: Home Discount: Total expenditure by obligated suppliers
		Comment: 
		Data details how much suppliers spent fulfilling their obligation of the Warm Home Discount (WHD), a government energy scheme which aims to help people who are in fuel poverty or are at risk of it. 
		Description:	
		Data details how much suppliers spent fulfilling their obligation of the Warm Home Discount (WHD), a government energy scheme which aims to help people who are in fuel poverty or are at risk of it. 
		Energy suppliers with over 250,000 domestic customers (referred to as ‘large suppliers’) are obligated to participate in each support element of the scheme, categorised by a ‘core group’, ‘broader group’ and ‘industry initiatives’. They are also allocated targets based on their share of the domestic GB energy market.
		For more on the scheme elements and how they work, see our overview page at Warm Home Discount:
		https://www.ofgem.gov.uk/environmental-programmes/social-programmes/warm-home-discount-whd
		We update this chart on an annual basis. 	
	Table 2 Structure:
		Period, Scheme Year, Support Element, Supplier, Marker, Year

#### Warm Home Discount: Percentage spend by nation at scheme year 8 (2018-19)

	Dimensions
		Add Period column with Gregorian-interval value for 15 August 2018 to 31 March 2019 (months or days)
		Add 'Scheme Year' column with value year-8
		Nation: change values to ONS Geography codes
		Total Spend: rename as Value
	Measures:
		Measure Type: expenditure
		Unit: percentage
	dataset_path: gss_data/energy/ofgem-warm-home-discount-scheme/nationexpenditure
		Title: Warm Home Discount: Percentage spend by nation
		Comment:
		Description:	
		Data shows a by nation view of the direct support provided to fuel poor customers through energy bill rebates for the ‘core group’ and ‘broader group’ elements of the Warm Home Discount (WHD). It comprises all participating suppliers in year 8 (2018/19) of the scheme.  
		The WHD is a government energy scheme which aims to help people who are in fuel poverty or are at risk of it. It focuses spending against three different support elements, categorised as ‘core group’, ‘broader group’ and ‘industry initiative’ spending. 
		For more on the scheme elements and how they work, see our overview page at Warm Home Discount:
		https://www.ofgem.gov.uk/environmental-programmes/social-programmes/warm-home-discount-whd 	
		We have gathered this information from obligated suppliers for information purposes, and as such it should be considered as advisory only. Scheme year 5 (2015/6) was the first year we have collected this data.  
		We update this chart on an annual basis.
	Table 3 Structure
		Period, Scheme Year, Nation, Value 
			

##### DM Notes

	Columns section has been defined in info.json and codelists created
		If we are able to do multi-measure cubes then add a column called 'Supplier' to Table 1 with value 'all' and join Tables 1 and 2

