import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime, time 

##This is a tutorial to get familiar with some of the basic Streamlit components##

st.header('Button demo', divider=True)
st.button("Reset", type="primary")

st.button("Just a button", type="secondary")

if st.button('Say hello'):
	st.write('Why hello there')
else:
	st.write('Goodbye')

st.header('Display Text & Numbers', divider=True)
st.write('Hello, *World!* :sunglasses:')
st.write(1234)

st.header('Display Data Frame', divider=True)
df = pd.DataFrame({
	'first column': [1, 2, 3, 4],
	'second column': [10, 20, 30, 40]
})
st.write('**Below** is a DataFrame:', df, '**Above** is a dataframe.')

st.header('Display Data Plot', divider=True)
df2 = pd.DataFrame(
     np.random.randn(200, 3),
     columns=['a', 'b', 'c'])
c = alt.Chart(df2).mark_circle().encode(
     x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
st.write(c)

st.header('Slider demo', divider=True)

st.subheader('Slider')
age = st.slider('How old are you?', 0, 100, 25)
st.write("I'm ", age, 'years old')

st.subheader('Range slider')
values = st.slider(
     'Select a range of values',
     0.0, 100.0, (25.0, 75.0))
st.write('Values:', values)

st.subheader('Range time slider')
appointment = st.slider(
     "Schedule your appointment:",
     value=(time(11, 30), time(12, 45)))
st.write(f"You're scheduled for: {appointment[0].strftime('%I:%M %p')} - {appointment[1].strftime('%I:%M %p')}")

st.subheader('Datetime slider')
start_time = st.slider(
     "When do you start?",
     value=datetime(2020, 1, 1, 9, 30),
     format="MM/DD/YY - hh:mm")
st.write("Start time:", start_time.strftime('%m/%d/%y - %I:%M %p'))

st.header('Line Chart demo', divider=True)
chart_data = pd.DataFrame(
	 np.random.randn(20, 3),
	 columns=['a', 'b', 'c'])
st.line_chart(chart_data)

