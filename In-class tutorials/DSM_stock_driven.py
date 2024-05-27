# -*- coding: utf-8 -*-
"""
Dynamic stock model, J van Oorschot, T Fishman & S Deetman
1. Load modules & data
2. create a single survival curve
3. create survival curve matrix
4. stock driven model
"""

# %% 1. Load modules & data
import pandas as pd
import numpy as np
import scipy.stats
from os import chdir
import matplotlib.pyplot as plt


# Load input data, stock-driven model:
stock_flow_timeseries = pd.read_excel(
    r'MFA_II_tutorial_II.xlsx', sheet_name='stock_driven')

stock_flow_timeseries = stock_flow_timeseries.set_index(['year'])

time_max = stock_flow_timeseries.shape[0]

timesteps = np.arange(0, time_max)


# %% 2. create a single survival curve, if one wasn't supplied as input data

# comment / uncomment the snipet for the curve you want, and modify its parameters

# # Fixed lifetime survival curve
curve_lifetime = 45
curve_surv = np.zeros_like(timesteps)
curve_surv[0:curve_lifetime] = 1

# Weibull distributed survival curve
# curve_shape = 3
# curve_scale = 15
# curve_surv = scipy.stats.weibull_min.sf(timesteps, curve_shape, 0, curve_scale)

# Normally distributed survival curve

# # Geometrically distributed survival curve
# curve_depreciate = 0.05
# curve_surv = scipy.stats.geom.sf(timesteps, curve_depreciate)

# # Uniformly distributed survival curve
# curve_subtract = 0.1
# curve_surv = scipy.stats.uniform.sf(timesteps, loc=0, scale=(1 / curve_subtract))

# Lognorm
# x = np.arange(0.01,1, 2.5)
# s = timesteps
# curve_surv = scipy.stats.lognorm.sf(x,s,loc = 0, scale = 1)
# curve_surv[0] = 1
#
# %% 3. create survival curve matrix

# create survival curve matrix with placeholder zeros
curve_surv_matrix = pd.DataFrame(0, index=timesteps, columns=timesteps)

# populate the survival curve matrix with shifted curves, column by column using slices
for time in timesteps:
    curve_surv_matrix.loc[time:, time] = curve_surv[0:time_max - time]

curve_surv_matrix.loc[1:, 1] = curve_surv[0:time_max - 1]

# %% 4. stock driven model

# create survival matrix with placeholder zeros
cohort_surv_matrix = pd.DataFrame(0, index=timesteps, columns=timesteps)

# iteratively calculate the inflow in stock_flow_timeseries, and
# multiply the inflow times the shifted curves to get the cohorts' behavior over time

for time in timesteps:
    stock_flow_timeseries['inflow'].iloc[time] = (
        stock_flow_timeseries['stock'].iloc[time] - cohort_surv_matrix.loc[time, :].sum()) / curve_surv_matrix.loc[time, time]
    cohort_surv_matrix.loc[:, time] = curve_surv_matrix.loc[:,
                                                            time] * stock_flow_timeseries['inflow'].iloc[time]

# set row index to years instead of timesteps
cohort_surv_matrix.index = stock_flow_timeseries.index

# calculate outflows and nas using the cohort_surv_matrix
# prepending 0 assumes no initial stock
stock_flow_timeseries['nas'] = np.diff(
    stock_flow_timeseries['stock'], prepend=0)
stock_flow_timeseries['outflow'] = stock_flow_timeseries['inflow'] - \
    stock_flow_timeseries['nas']


# %% 5. Export output data to Excel

cohort_surv_matrix.to_excel('cohort_surv_matrix.xlsx')
stock_flow_timeseries.to_excel('stock_flow_timeseries.xlsx')
