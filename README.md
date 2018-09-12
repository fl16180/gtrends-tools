# gtrends-tools
gtrends-tools provides an unofficial interface for automating the retrieval of search frequency data from the Google Health Trends API. While Google Trends has a publicly available browser tool at <http://trends.google.com/trends> with unofficial interfaces in Python [[1]](https://github.com/GeneralMills/pytrends) and R [[2]](https://github.com/PMassicotte/gtrendsR), the Google Health Trends API provides more control in selecting data, has higher download rates, and arguably returns more precise search trends. However, to use this tool, a Google Health Trends API key is required for access to Google's servers.

I hope to expand this package by adding tools for Google Correlate and methodologies for feature selection and engineering of search queries. The aim is to provide more relevant and accurate data for machine learning projects.

## Installation

To install gtrends-tools with pip, run: `pip install healthtrends`

To install gtrends-tools from source, first clone the repository and then run:
`python setup.py install`


## Usage

Here is a simple example of `gtrends-tools` usage.

```python
import healthtrends

DIR = '/home/fl16180/'

queries = ['tofu', 'exercise']

gt = healthtrends.TrendsSession(api_key='xxx')
gt.request_trends(term_list=queries, geo_level='country', geo_id='US')
gt.save_to_csv(directory=DIR, fname='healthy_trends.csv')

```

Parameters for request_trends are:
- term_list: list of search term queries
- geo_level: geographic location, one of 'country', 'region', or 'dma'
- geo_id: name of the geographic location, e.g. 'US' (country), 'US-NY' (region), '501' (dma)
- start_date: first day to download data from, in form 'YYYY-MM-DD'. Defaults to 2004-01-04.
- end_date: last day to download data from, in form 'YYYY-MM-DD'. Defaults to today's date.
- freq: time interval of data, one of 'day', 'week', 'month', 'year'. Defaults to 'week'

For additional examples, refer to the [included scripts](bin/example.py). I will add more detailed documentation of parameters later, as well as scripts to get data remotely (for IP restrictions on API access).


## Research
Search frequencies obtained from the Google Trends API using this code (or previous versions) have been an integral part of research papers including [[1]](https://publichealth.jmir.org/2018/1/e4/).

## Credits
Package structure inspired by <https://github.com/GeneralMills/pytrends>

The original Google Health Trends API script has been passed around a few times before being adapted by Andre Nguyen and passed to me. I don't know what the original source is but have seen duplicate of the original script in other github repos. As such, I felt that converting it into a package with OOP interface would best facilitate scientific sharing of research methods.
