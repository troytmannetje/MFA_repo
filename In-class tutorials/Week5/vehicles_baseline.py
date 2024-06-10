# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 15:35:20 2018

@author: Tomer Fishman
"""

# %% load packages and data, and set initial parameters

import numpy as np
import scipy.stats
import pandas as pd
from os import chdir

chdir('C:/Users/tomer//Leiden CML/2024 4 MFA2/5 scenarios 2/assignment scenarios in dmfa')

vehicles_baseline = pd.read_excel("vehicles.xlsx", sheet_name="stocks")  # load the historical and projected future stock of hybrid electric vehicles
vehicles_baseline = vehicles_baseline.rename(columns={"vehicle_stock": "stock"})  # rename the column to stock to keep things consistent

time_max = vehicles_baseline.shape[0]  # the final timestep of this timeseries
timesteps = np.arange(0, time_max)  # an array of the timesteps

curve_parameters = pd.read_excel("vehicles.xlsx", sheet_name="survival_weibull", index_col="parameter")  # load the parameters of the Weibull survival curve
curve_surv = scipy.stats.weibull_min.sf(timesteps, curve_parameters.loc["shape", "value"], 0, curve_parameters.loc["scale", "value"])
curve_surv_matrix = pd.DataFrame(0, index=timesteps, columns=timesteps)  # create a dataframe for the survival curve matrix
for time in timesteps:  # loop through the columns
    curve_surv_matrix.loc[time:, time] = curve_surv[0:time_max - time]  # populate each column with the survival curve, shifted one row down

material_intensities = pd.read_excel("vehicles.xlsx", sheet_name="material_intensities", index_col="grams/car")  # load the parameters of the Weibull survival curve


# %% baseline scenario: all hybrid electric vehicles (HEVs) with steel frames

vehicles_baseline['inflow'] = np.nan  # add an empty column that the stock-driven model in the next few lines can populate with the inflows

vehicles_baseline_surv_matrix = pd.DataFrame(0, index=timesteps, columns=timesteps)  # create an empty (zeros) cohort survival matrix for the stock driven model

# the next 5 lines are the stock driven model
for time in timesteps:
    vehicles_baseline['inflow'].loc[time] = (vehicles_baseline['stock'].loc[time] - vehicles_baseline_surv_matrix.loc[time, :].sum()) / curve_surv_matrix.loc[time, time]
    vehicles_baseline_surv_matrix.loc[:, time] = curve_surv_matrix.loc[:, time] * vehicles_baseline['inflow'].loc[time]
vehicles_baseline['nas'] = np.diff(vehicles_baseline['stock'], prepend=0)  # nas is the delta of the stock
vehicles_baseline['outflow'] = vehicles_baseline['inflow'] - vehicles_baseline['nas']  # estimate outflows using mass balance

# convert to materials
# using the inflow-driven dMFA model
aluminum_baseline = pd.DataFrame({'year': vehicles_baseline['year']})
aluminum_baseline['inflow'] = vehicles_baseline['inflow'] * material_intensities.loc["Al", "HEV_NiMH"]
aluminum_surv_matrix = pd.DataFrame(0, index=timesteps, columns=timesteps)
for time in timesteps:
    aluminum_surv_matrix.loc[:, time] = curve_surv_matrix.loc[:, time] * aluminum_baseline['inflow'].iloc[time]
aluminum_baseline['stock'] = aluminum_surv_matrix.sum(axis=1)  # sum the surviving inflow cohorts to get the stock
aluminum_baseline['nas'] = np.diff(aluminum_baseline['stock'], prepend=0)  # nas is the delta of the stock
aluminum_baseline['outflow'] = aluminum_baseline['inflow'] - aluminum_baseline['nas']

# or using a shortcut when there's only one vehicle type and the MI doesn't change over time: just multiply all of the columns of stocks and flows by the MI instead of running a flow-driven dynamic model
# you can compare these results with the ones above to confirm. Note that you could do this with the cohort matrix too, if you need it.
aluminum_baseline2 = vehicles_baseline.copy()
aluminum_baseline2[['stock', 'inflow', 'outflow', 'nas']] *= material_intensities.loc["Al", "HEV_NiMH"]
steel_baseline = vehicles_baseline.copy()
steel_baseline[['stock', 'inflow', 'outflow', 'nas']] *= material_intensities.loc["Fe", "HEV_NiMH"]

# combine the material dataframes to make it easier to plot figures
materials_baseline = pd.concat([aluminum_baseline, steel_baseline], axis=1, keys=['aluminum', 'steel'])
materials_baseline.loc[:, (slice(None), ['inflow', 'outflow'])].plot()
materials_baseline.loc[:, (slice(None), 'stock')].plot(kind="area")
