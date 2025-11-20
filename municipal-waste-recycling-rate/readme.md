# Municipal waste recycling rate - Data package

This data package contains the data that powers the chart ["Municipal waste recycling rate"](https://ourworldindata.org/grapher/municipal-waste-recycling-rate?v=1&csvType=full&useColumnShortNames=false&utm_source=chatgpt.com) on the Our World in Data website. It was downloaded on October 26, 2025.

### Active Filters

A filtered subset of the full data was downloaded. The following filters were applied:

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For normal countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The final column is the data column, which is the time series that powers the chart. If the CSV data is downloaded using the "full data" option, then the column corresponds to the time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data column is transformed depending on the chart type and thus the association with the time series might not be as straightforward.

## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

## Detailed information about the data


## Variable:% Recycling - MUNW
Unit: Percentage  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
OECD - Environment - Municipal waste, Generation and Treatment – processed by Our World in Data

#### Full citation
OECD - Environment - Municipal waste, Generation and Treatment – processed by Our World in Data. “Variable:% Recycling - MUNW” [dataset]. OECD - Environment - Municipal waste, Generation and Treatment [original data].
Source: OECD - Environment - Municipal waste, Generation and Treatment – processed by Our World In Data

### Additional information about this data
Contact person/organisation
ENV.Stat@oecd.org
Data source(s) used
This dataset shows data provided by Member countries' authorities through the questionnaire on the state of the environment (OECD/Eurostat). They were updated or revised on the basis of data from other national and international sources available to the OECD Secretariat, and on the basis of comments received from national Delegates. Selected updates were also done in the context of the OECD Environmental Performance Reviews. The data are harmonised through the work of the OECD Working Party on Environmental Information (WPEI) and benefit from continued data quality efforts in OECD member countries, the OECD itself and other international organisations.In many countries systematic collection of environmental data has a short history; sources are typically spread across a range of agencies and levels of government, and information is often collected for other purposes. When interpreting these data, one should  keep in mind that definitions and measurement methods vary among countries, and that inter-country comparisons require careful interpretation. One should also note that data presented here refer to national level and may conceal major subnational differences.
Key statistical concept
This dataset presents trends in amounts of municipal (including household waste), and the treatment and disposal method used.The amount of waste generated in each country is related to the rate of urbanisation, the types and pattern of consumption, household revenue and lifestyles.
Metadata
http://stats.oecd.org/wbos/fileview2.aspx?IDFile=9bc27df8-1205-468c-b178-ce0d200f2641


    