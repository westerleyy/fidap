# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import streamlit as st
import numpy as np
import pandas as pd
import fidap 
from config import api_key
import matplotlib.pyplot as plt
import altair as alt

# instantiate api connection
fidap = fidap.fidap_client(api_key=api_key)

# sample covid19 data from nyt

nyt_sample = fidap.sql("""
                       SELECT confirmed_cases AS Cases, deaths AS Deaths, date, state_name
                       FROM bigquery-public-data.covid19_nyt.us_states
                       WHERE state_name IN ('New York', 'New Jersey', 'Connecticut');                      
                       """
    )

nyt_sample_long = nyt_sample.melt(id_vars = ['state_name', 'date'], value_vars = ['Cases', 'Deaths'])

states_boundaries = fidap.sql("""
                              SELECT state_fips_code, state, state_name, state_geom, int_point_lat AS lat, int_point_lon AS lon
                              FROM bigquery-public-data.geo_us_boundaries.states;
                             """)
                             
state_options = st.selectbox("State", nyt_sample_long['state_name'].unique())


if state_options:
    
    line_df = nyt_sample_long.loc[(nyt_sample_long['state_name'] == state_options),:]
    c = alt.Chart(line_df).mark_line().encode(
        x = 'date',
        y = 'value',
        color = 'variable',
        strokeDash = 'variable'
        )
    st.altair_chart(c, use_container_width = True)




# types_options = st.selectbox("Statistic", nyt_sample_long['variable'].unique())                             

# state_option, types_options = st.beta_columns(2)

# if state_options and types_options:
    
#     line_df = nyt_sample_long.loc[((nyt_sample_long['state_name'] == state_options) & (nyt_sample_long['variable'] == types_options)),:]
    
#     c = alt.Chart(line_df).mark_line().encode(
#             x = 'date:T',
#             y = 'value:Q'
#             )
#     st.altair_chart(c, use_container_width = True)
    
        
        





# it appears that streamlit cannot support polygons for mapping.
st.map(states_boundaries)

#line_df = nyt_sample_long.loc[((nyt_sample_long['state_name'] == 'New York') & (nyt_sample_long['variable'] == 'Cases')),:]
#alt.Chart(line_df).mark_line().encode(
#            x = 'date:T',
#            y = 'value:Q'
#            )