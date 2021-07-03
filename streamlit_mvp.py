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

# instantiate api connection
fidap = fidap.fidap_client(api_key=api_key)

# sample covid19 data from nyt

nyt_sample = fidap.sql("""
                       SELECT confirmed_cases, deaths
                       FROM bigquery-public-data.covid19_nyt.us_states
                       LIMIT 10;                      
                       """
    )



st.line_chart(nyt_sample)