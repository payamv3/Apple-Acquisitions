import streamlit as st
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
import seaborn as sn
import os
import altair as alt
import requests
import csv
import sys
import time
from io import StringIO

st.set_page_config(
    page_title="Apple Acquisitions Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme through custom CSS
st.markdown("""
<style>
    /* Force light theme */
    [data-testid="stAppViewContainer"] {
        background-color: white;
    }
    [data-testid="stHeader"] {
        background-color: white;
    }
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

def load_data_from_web():
    """Attempt to scrape data from Wikipedia"""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_mergers_and_acquisitions_by_Apple"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/128.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        }
        page = requests.get(url, headers=headers)
        page.raise_for_status()
        
        # Parse HTML
        soup = bs(page.text, "html.parser")
        
        # Use pandas read_html directly on the URL - more reliable
        df = pd.read_html(url, attrs={'class': 'wikitable'})[0]
        return df, "web"
        
    except Exception as e:
        st.warning(f"Failed to load data from web: {e}")
        return None, "error"

def load_data_from_csv():
    """Load data from CSV file"""
    try:
        # Try to load from CSV
        df = pd.read_csv('data.csv')
        return df, "csv"
    except FileNotFoundError:
        st.error("data.csv file not found. Please upload the CSV file to your repository.")
        return None, "error"
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None, "error"

def process_data(df):
    """Process the dataframe regardless of source"""
    # Handle year extraction more robustly
    if 'Date' in df.columns:
        df['Year'] = df['Date'].astype(str).str[-4:]
    elif 'year' in df.columns:
        df['Year'] = df['year']
    elif 'Year' in df.columns:
        pass  # Year column already exists
    else:
        st.error("No date/year column found in the data")
        return None
    
    # Handle the specific data correction you had
    try:
        if len(df) > 11:
            df.iloc[11, df.columns.get_loc('Year')] = '2000'
    except:
        pass
    
    # Convert year to int
    try:
        df['Year'] = df['Year'].astype('int')
    except:
        # If conversion fails, try to clean the data
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df = df.dropna(subset=['Year'])
        df['Year'] = df['Year'].astype('int')
    
    return df

# Main data loading logic
df = None
data_source = None

# Try web scraping first
df, data_source = load_data_from_web()

# If web scraping fails, try CSV
if df is None:
    df, data_source = load_data_from_csv()

# If both fail, show error and stop
if df is None:
    st.error("Unable to load data from either web or CSV file.")
    st.stop()

# Process the data
df = process_data(df)
if df is None:
    st.stop()

# Show data source info
if data_source == "web":
    st.success("✅ Data loaded from Wikipedia")
elif data_source == "csv":
    st.info("📁 Data loaded from CSV file (web scraping failed)")

# Group data for visualization
company_col = 'Company' if 'Company' in df.columns else df.columns[0]
source = df.groupby('Year').count()[[company_col]]
source = source.rename(columns={company_col: 'Company'})

# Sidebar content
st.sidebar.header("Apple Acquisitions through the years")
st.sidebar.markdown("""
This visualization tracks Apple's corporate acquisitions over time, 
revealing distinct patterns between the <span style='color: grey; font-weight: bold;'>Steve Jobs era</span> 
and the <span style='color: steelblue; font-weight: bold;'>Tim Cook era</span>.
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:**")
if data_source == "web":
    st.sidebar.markdown("[Wikipedia - List of mergers and acquisitions by Apple](https://en.wikipedia.org/wiki/List_of_mergers_and_acquisitions_by_Apple)")
else:
    st.sidebar.markdown("Local CSV file (data.csv)")
st.sidebar.markdown("---")
st.sidebar.markdown("*A Small Project by Payam Saeedi*")

# Create visualization
bars = alt.Chart(source.reset_index()).mark_bar(
    cornerRadiusTopLeft=3,
    cornerRadiusTopRight=3, 
    size=30
).encode(
    alt.X('Year:O', axis=alt.Axis(grid=False, labelAngle=0, labelFontSize=12, tickSize=0, labelPadding=10)),
    alt.Y('Company:Q', axis=alt.Axis(title='Number of Acquisitions', labels=False, grid=False)),
    color=alt.condition(
        alt.datum.Year > 2011,
        alt.value('steelblue'),
        alt.value('grey')
    )
).properties(title='Apple Acquisitions Through Time', width=1000, height=400)

text = bars.mark_text(
    align='center',
    baseline='middle',
    dy=-6
).encode(
    text='Company:Q'
)

st.altair_chart((bars + text).configure_view(stroke='transparent', strokeOpacity=0), use_container_width=True)
