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

nyc_turnstile_data['date'] = nyc_turnstile_data['date'].dt.normalize()

nyc_turnstile_data = nyc_turnstile_data.rename(columns = {
    'gtfs_latitude': 'latitude',
    'gtfs_longitude': 'longitude'
    })

station_geom = nyc_turnstile_data.copy().reset_index()[['stop_name', 'longitude', 'latitude']].drop_duplicates()


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

    station1 = st.sidebar.selectbox('Station 1:', station_list)
    station2 = st.sidebar.selectbox('Station 2:', station_list)
    
    # get date range
    
    df_start_date = nyc_turnstile_data.date.min()
    df_end_date = nyc_turnstile_data.date.max()
    
    dates = st.sidebar.date_input('Dates', max_value = df_end_date, min_value = df_start_date, value = (df_start_date, df_end_date))
    
    start_date, end_date = dates
    
    start_date = np.datetime64(start_date)
    end_date = np.datetime64(end_date)

    # creating df and geom for both stations
    station1_df = nyc_turnstile_data[(nyc_turnstile_data['stop_name'] == station1) & (nyc_turnstile_data['date'] >= start_date) & (nyc_turnstile_data['date'] <= end_date)].copy()
    station1_df = station1_df.melt(id_vars = ['stop_name', 'daytime_routes', 'line', 'longitude', 'latitude', 'date'], value_vars = ['entries', 'exits'])
    station1_df['value'] = station1_df.value.astype(int)
    
    station2_df = nyc_turnstile_data[(nyc_turnstile_data['stop_name'] == station2) & (nyc_turnstile_data['date'] >= start_date) & (nyc_turnstile_data['date'] <= end_date)].copy()
    station2_df = station2_df.melt(id_vars = ['stop_name', 'daytime_routes', 'line', 'longitude', 'latitude', 'date'], value_vars = ['entries', 'exits'])
    station2_df['value'] = station2_df.value.astype(int)
    
    stations_geom = station_geom[(station_geom['stop_name'] == station1) | (station_geom['stop_name'] == station2) ]
    

with charts:
    
    st.header(f'Entries and Exits at {station1} (L) and {station2} (R) between {start_date} and {end_date}')
    st.markdown("""
                We can see that there is a sharp drop in the ridership levels beginning the middle of March 2020. Even up till the end of 2020, ridership levels had yet to recover.  
                  
                It is not advisable to view data over long time periods with the line charts stacked side by side. 
                """)
    
    left_column, right_column = st.beta_columns((2,2))
    
    with left_column:
        c1 = alt.Chart(station1_df).mark_line().encode(
            	x = 'date',
                y = 'value',
                color = 'variable',
                strokeDash = 'variable',
                tooltip = ['date', 'value', 'variable']
                ).interactive()
        st.altair_chart(c1, use_container_width = True)
       
    #with right_column:
    with right_column:
        c2 = alt.Chart(station2_df).mark_line().encode(
            x = 'date',
            y = 'value',
            color = 'variable',
            strokeDash = 'variable',
            tooltip = ['date', 'value', 'variable']
            ).interactive()
        st.altair_chart(c2, use_container_width = True)
        

    st.map(stations_geom)
    
