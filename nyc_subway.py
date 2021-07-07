# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 23:32:03 2021

@author: wesch
"""

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime

nyc_turnstile_data = pd.read_csv('C:/Users/wesch/OneDrive/Documents/Fidap/fidap/nyc_mta_transit_data/body.csv', usecols = ['stop_name', 'daytime_routes', 'line', 'gtfs_longitude', 'gtfs_latitude', 'date', 'entries', 'exits'])

nyc_turnstile_data['date'] = pd.to_datetime(nyc_turnstile_data['date'], format = '%Y-%m-%d')

# nyc_turnstile_data = nyc_turnstile_data.assign(
#     date = lambda x: datetime.strptime(x.date, '%Y:%m:%d')
#     )



header = st.beta_container()
sidebar_input = st.beta_container()
charts = st.beta_container()

with header:
    st.title("MTA Ridership in 2020")
    st.markdown("""
                **Wesley Chioh**  
            
                This web app will utilize turnstile information from NYC MTA, meticulously cleaned and by [Chris Whong](https://qri.cloud/nyc-transit-data/turnstile_daily_counts_2020) for the year 2020.  
              
                What a year 2020 was. We all know that ridership decreased, but by how much? And has it rebounded? An extension of this visual will see us use data from 2019 to compare. 
            
                """)


with sidebar_input:
    st.sidebar.header("MTA 2020")

    # get list of stations

    station_list = []
    station_list = nyc_turnstile_data.stop_name.unique().tolist()
    # station_list = station_list.sort()

    station1 = st.sidebar.selectbox('Station 1:', station_list)
    station2 = st.sidebar.selectbox('Station 2:', station_list)

    # creating df for both stations
    station1_df = nyc_turnstile_data[(nyc_turnstile_data['stop_name'] == station1)].copy()
    station1_df = station1_df.melt(id_vars = ['stop_name', 'daytime_routes', 'line', 'gtfs_longitude', 'gtfs_latitude', 'date'], value_vars = ['entries', 'exits'])
    station1_df['value'] = station1_df.value.astype(int)
    station2_df = nyc_turnstile_data[(nyc_turnstile_data['stop_name'] == station2)].copy()
    station2_df = station2_df.melt(id_vars = ['stop_name', 'daytime_routes', 'line', 'gtfs_longitude', 'gtfs_latitude', 'date'], value_vars = ['entries', 'exits'])
    station2_df['value'] = station2_df.value.astype(int)

with charts:
    
    st.header(f'Entries and Exits at {station1} (T) and {station2} (B)')
    
    
    # left_column, right_column = st.beta_columns(2)
    
    c1 = alt.Chart(station1_df).mark_line().encode(
        x = 'date',
        y = 'value',
        color = 'variable',
        strokeDash = 'variable'
        )
    st.altair_chart(c1, use_container_width = True)
    
    #with right_column:
    c2 = alt.Chart(station2_df).mark_line().encode(
        x = 'date',
        y = 'value',
        color = 'variable',
        strokeDash = 'variable'
        )
    st.altair_chart(c2, use_container_width = True)
    
    
