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

page = requests.get('https://en.wikipedia.org/wiki/List_of_mergers_and_acquisitions_by_Apple')
soup = bs(page.text, 'html.parser')   
table = soup.find_all('table')
df = pd.read_html(str(table))[0]
df['Year'] = df['Date'].str[-4:]
df.iloc[11,7] = '2000'
df['Year'] = df['Year'].astype('int32')
source = df.groupby('Year').count()[['Company']]

#col1, col2 = st.columns(2)
#with col1:
    #st.header("Apple Acquisitions through the years")
    #st.markdown("""With the increasing pace of technological advancement, Apple seems to have increased the number of companies it acquires every year. The difference in approach is more evident when you break down Apple's history into two eras. Tim Cook and his mastery of a global suuply chains has seen the need to acquire more start ups along the way in order to remain competitive in a fiercely saturating marketing.""")

st.sidebar.header("Apple Acquisitions through the years")
st.sidebar.markdown("""Since Tim Cook was appointed CEO in 2011, Apple seems to have increased the number of companies it acquires every year. Steve Jobs was always innovation-first. In notable contrast, Tim Cook seems to have realised the increasing pace of innovation and has focused on acquiring more start ups along the way in order to remian competitive in a fiercely saturating market.""")

#st.title('Apple\'s Acquisitions through the years')
#st.dataframe(df)
#st.markdown("""With the increasing pace of technological advancement, Apple seems to have increased the number of companies it acquires every year. The difference in approach is more evident when you break down Apple's history into two eras. Tim Cook and his mastery of a global suuply chains has seen the need to acquire more start ups along the way in order to remain competitive in a fiercely saturating marketing.""")

#st.sidebar.header('Select a year in order to see derived products')
#selected_year= st.sidebar.selectbox('Year', list(reversed(range(1950,2022))))

bars = alt.Chart(source.reset_index()).mark_bar(cornerRadiusTopLeft=3,
    cornerRadiusTopRight=3, size = 30, stroke = 'transparent', strokeOpacity = 0).encode(
    alt.X('Year:O', axis = alt.Axis(grid = False, labelAngle=0, labelFontSize=12, tickSize=0, labelPadding=10)),
    alt.Y('Company:Q', axis=alt.Axis(title='Number of Acquisitions', labels = False, grid=False)),
    # The highlight will be set on the result of a conditional statement
    color=alt.condition(
        alt.datum.Year > 2011,  # If the year is 1810 this test returns True,
        alt.value('steelblue'),     # which sets the bar orange.
        alt.value('grey')   # And if it's not true it sets the bar steelblue.
    )
).properties(title = 'Apple Acquisitions Through Time', width = 800, height = 400)

text = bars.mark_text(
    align='center',
    baseline='middle' , dy = -6
).encode(
    text='Company:Q'
)


st.altair_chart(bars + text, use_container_width = True)