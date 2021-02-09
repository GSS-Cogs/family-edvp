# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import json

import pandas as pd

from gssutils import *

# +
infoFileName = 'info.json'
 
info    = json.load(open(infoFileName))
scraper = Scraper(seed=infoFileName)
cubes   = Cubes(infoFileName)
distro  = scraper.distribution(latest=True, mediaType='text/csv')
# -

df = distro.as_pandas(encoding='cp1252')

df.head()

cubes.add_cube(scraper, df, scraper.title)

cubes.output_all()


