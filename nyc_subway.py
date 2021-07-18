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
# from config import api_key
import fidap

# instantiate api connection
fidap = fidap.fidap_client(api_key=api_key)


# get us holidays
us_holidays = fidap.sql("""
SELECT holidayName, SUBSTR(CAST(ph.date AS STRING),1,10) AS holidayDate   
FROM fidap-301014.azure_open_datasets.public_holidays AS ph
WHERE EXTRACT(YEAR FROM ph.date) BETWEEN 2019 AND 2021
AND ph.countryRegionCode = 'US'
                        """)

us_holidays['holidayDate'] = pd.to_datetime(us_holidays['holidayDate'], format = '%Y-%m-%d')
us_holidays['holidayDate'] = us_holidays['holidayDate'].dt.normalize()

# read nyc turnstile data
nyc_turnstile_data_2019 = pd.read_csv('C:/Users/wesch/OneDrive/Documents/Fidap/fidap/nyc_mta_transit_data/body_2019.csv', usecols = ['stop_name', 'daytime_routes', 'line', 'gtfs_longitude', 'gtfs_latitude', 'date', 'entries', 'exits'])
nyc_turnstile_data_2020 = pd.read_csv('C:/Users/wesch/OneDrive/Documents/Fidap/fidap/nyc_mta_transit_data/body_2020.csv', usecols = ['stop_name', 'daytime_routes', 'line', 'gtfs_longitude', 'gtfs_latitude', 'date', 'entries', 'exits'])
nyc_turnstile_data_2021 = pd.read_csv('C:/Users/wesch/OneDrive/Documents/Fidap/fidap/nyc_mta_transit_data/body_2021.csv', usecols = ['stop_name', 'daytime_routes', 'line', 'gtfs_longitude', 'gtfs_latitude', 'date', 'entries', 'exits'])

def initial_df_processing(df):
    
    df['date'] = pd.to_datetime(df['date'], format = '%Y-%m-%d')
    df['date'] = df['date'].dt.normalize()
    df = df.rename(columns = {
        'gtfs_latitude': 'latitude',
        'gtfs_longitude': 'longitude'
        })
    return df

nyc_turnstile_data_2019 = initial_df_processing(nyc_turnstile_data_2019)
nyc_turnstile_data_2020 = initial_df_processing(nyc_turnstile_data_2020)
nyc_turnstile_data_2021 = initial_df_processing(nyc_turnstile_data_2021)
    

# get station geom
station_geom = nyc_turnstile_data_2020.copy().reset_index()[['stop_name', 'longitude', 'latitude']].drop_duplicates()

# get station list
station_list = []
station_list = station_geom.stop_name.unique().tolist()

# get holiday list
holiday_list = []
holiday_list = us_holidays.holidayName.unique().tolist()

header = st.beta_container()
sidebar_input = st.beta_container()
charts = st.beta_container()

with header:
    st.title("MTA Ridership between 2019 and 2021")
    st.markdown("""
                **Wesley Chioh**  
            
                This web app will utilize holiday data from the [Fidap platform](https://app.fidap.com), turnstile information from NYC MTA, meticulously cleaned and by [Chris Whong](https://qri.cloud/nyc-transit-data/turnstile_daily_counts_2020) for the years 2019 - 2021.  
              
                What a year 2020 was. We all know that ridership decreased, but by how much? And has it rebounded? How much did it decline year on year anyway?   
                   
                This app will center on the year 2020. Select a period of time in 2020, and we will tell you how 2020 compares to 2019, and 2021 if you select an end date that is on or before July 2, 2020. 
            
                """)


with sidebar_input:
    
    st.sidebar.header("MTA and Holidays")

    station1 = st.sidebar.selectbox('Station 1:', station_list)
    # station2 = st.sidebar.selectbox('Station 2:', station_list)
    
    # get date range
    
    df_start_date = nyc_turnstile_data_2020.date.min()
    df_end_date = nyc_turnstile_data_2020.date.max()
    
    dates = st.sidebar.date_input('Dates', max_value = df_end_date, min_value = df_start_date, value = (df_start_date, df_end_date))
    
    start_date, end_date = dates
    
    start_date = np.datetime64(start_date)
    end_date = np.datetime64(end_date)
    
    # select holidays 
    holidays = st.sidebar.selectbox('Public Holiday:', holiday_list)

    # creating df and geom for stations
    station1_df = nyc_turnstile_data_2020[(nyc_turnstile_data_2020['stop_name'] == station1) & (nyc_turnstile_data_2020['date'] >= start_date) & (nyc_turnstile_data_2020['date'] <= end_date)].copy()
    station1_df = station1_df.melt(id_vars = ['stop_name', 'daytime_routes', 'line', 'longitude', 'latitude', 'date'], value_vars = ['entries', 'exits'])
    station1_df['value'] = station1_df.value.astype(int)
    
    # station2_df = nyc_turnstile_data[(nyc_turnstile_data['stop_name'] == station2) & (nyc_turnstile_data['date'] >= start_date) & (nyc_turnstile_data['date'] <= end_date)].copy()
    # station2_df = station2_df.melt(id_vars = ['stop_name', 'daytime_routes', 'line', 'longitude', 'latitude', 'date'], value_vars = ['entries', 'exits'])
    # station2_df['value'] = station2_df.value.astype(int)
    
    stations_geom = station_geom[(station_geom['stop_name'] == station1)]
    
    # get 2019 equivalent  
    
    start_date_2019 = start_date - np.timedelta64(365, 'D')
    end_date_2019 = end_date - np.timedelta64(365, 'D')
    
    station_2019_df = nyc_turnstile_data_2019[(nyc_turnstile_data_2019['stop_name'] == station1) & (nyc_turnstile_data_2019['date'] >= start_date_2019) & (nyc_turnstile_data_2019['date'] <= end_date_2019)].copy()
    station_2019_df = station_2019_df.melt(id_vars = ['stop_name', 'daytime_routes', 'line', 'longitude', 'latitude', 'date'], value_vars = ['entries', 'exits'])
    station_2019_df['value'] = station_2019_df.value.astype(int)
    
    # get holidays and ridership accordingly 
    
    selected_holidays = us_holidays[(us_holidays['holidayName'] == holidays)]
    ridership_holiday_2019 = station_2019_df.merge(selected_holidays, left_on = 'date', right_on = 'holidayDate', how = 'inner' )
    ridership_holiday_2020 = station1_df.merge(selected_holidays, left_on = 'date', right_on = 'holidayDate', how = 'inner' )
    combined_ridership_holiday = pd.concat([ridership_holiday_2019, ridership_holiday_2020])
    
    # get 2021 equivalent
    
    start_date_2021 = start_date + np.timedelta64(365, 'D')
    end_date_2021 = end_date + np.timedelta64(365, 'D')
    
    if end_date_2021 <= np.datetime64("2021-07-02"):
        
        station_2021_df = nyc_turnstile_data_2021[(nyc_turnstile_data_2021['stop_name'] == station1) & (nyc_turnstile_data_2021['date'] >= start_date_2021) & (nyc_turnstile_data_2021['date'] <= end_date_2021)].copy()
        station_2021_df = station_2021_df.melt(id_vars = ['stop_name', 'daytime_routes', 'line', 'longitude', 'latitude', 'date'], value_vars = ['entries', 'exits'])
        station_2021_df['value'] = station_2021_df.value.astype(int)
        ridership_holiday_2021 = station_2021_df.merge(selected_holidays, left_on = 'date', right_on = 'holidayDate', how = 'inner' )
        combined_ridership_holiday = pd.concat([combined_ridership_holiday, ridership_holiday_2021])

    combined_ridership_holiday['year'] = combined_ridership_holiday['date'].dt.year
    

with charts:
    
    st.header(f'Entries and Exits at {station1}')
    
    #left_column, right_column = st.beta_columns((2,2))
    
    st.map(stations_geom)
    
    st.markdown("""
                We can see that there is a sharp drop in the ridership levels beginning the middle of March 2020. Even up till the end of 2020, ridership levels had yet to recover.  
                  
                """)
    
    c1 = alt.Chart(station1_df,
                   title = '2020 Ridership').mark_line().encode(
        x = 'date',
        y = 'value',
        color = 'variable',
        strokeDash = 'variable',
        tooltip = ['date', 'value', 'variable']
        ).interactive()
    st.altair_chart(c1, use_container_width = True)
       
    st.markdown("""
                These are the corresponding numbers for 2019.  
                  
                """)

    c2 = alt.Chart(station_2019_df,
                   title = '2019 Ridership').mark_line().encode(
        x = 'date',
        y = 'value',
        color = 'variable',
        strokeDash = 'variable',
        tooltip = ['date', 'value', 'variable']
        ).interactive()
    st.altair_chart(c2, use_container_width = True)
    
    if end_date_2021 <= np.datetime64("2021-07-02"):
        
        st.markdown("""
                And of course, 2021.  
                  
                """)

        
        c3 = alt.Chart(station_2021_df,
                       title = '2021 Ridership').mark_line().encode(
            x = 'date',
            y = 'value',
            color = 'variable',
            strokeDash = 'variable',
            tooltip = ['date', 'value', 'variable']
            ).interactive()
    
        st.altair_chart(c3, use_container_width = True)
    
    c4 = alt.Chart(combined_ridership_holiday,
                   title = 'Holiday Ridership',
                   width = 200).mark_bar().encode(
                       x = 'variable',
                       y = 'value',
                       color = 'variable',
                       column = 'year'
                       )
                       
    c4                 
        
        
        

    
    
