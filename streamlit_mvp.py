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
                       SELECT confirmed_cases, deaths, date, state_name
                       FROM bigquery-public-data.covid19_nyt.us_states
                       WHERE state_name IN ('New York', 'New Jersey', 'Connecticut');                      
                       """
    )

states_boundaries = fidap.sql("""
                              SELECT state_fips_code, state, state_name, state_geom, int_point_lat AS lat, int_point_lon AS lon
                              FROM bigquery-public-data.geo_us_boundaries.states;
                             """)

c = alt.Chart(nyt_sample).mark_line().encode(
    x = 'date',
    y = 'confirmed_cases',
    color = 'state_name',
    strokeDash = 'state_name'
    )

st.altair_chart(c, use_container_width = True)

# it appears that streamlit cannot support polygons for mapping.
st.map(states_boundaries)

