import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime, time 

st.header('Button demo', divider=True)
st.button("Reset", type="primary")

st.button("Just a button", type="secondary")

if st.button('Say hello'):
	st.write('Why hello there')
else:
	st.write('Goodbye')

st.header('st.write demo', divider=True)

st.header('Display Text', divider=True)
st.write('Hello, *World!* :sunglasses:')

st.header('Display Numbers', divider=True)
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

age = st.slider('How old are you?', 0, 130, 25)
st.write("I'm ", age, 'years old')
