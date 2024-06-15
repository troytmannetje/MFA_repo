# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 13:43:47 2024

@author: troyt
"""

# %% load packages

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats

# %% import data


# define temporal boundaries
years = np.arange(1975, 2051)
no_of_years = len(years)

# define lifetime/survival function
lifetime_params = pd.DataFrame(columns=['mean', 'std'],
                               dtype=np.float32)
lifetime_params.loc[1975, :] = [20, 2]

# %% main code
#
lifetime_curve = pd.DataFrame(columns=lifetime_params.index,
                              dtype=np.float32)
survival_curve = pd.DataFrame(columns=lifetime_params.index,
                              dtype=np.float32)

for year in lifetime_params.index:  # calculate survival functions for each eyar
    lifetime = scipy.stats.norm(lifetime_params.loc[year, 'mean'],
                                lifetime_params.loc[year, 'std'])
    lifetime_curve.loc[:, year] = lifetime.pdf(range(no_of_years))
    survival_curve.loc[:, year] = lifetime.sf(range(no_of_years))


# calculate survival matrix
survival_matrix = pd.DataFrame(0, columns=years, index=years,
                               dtype=np.float32)
for year
