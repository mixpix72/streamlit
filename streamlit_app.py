import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# st.button("Reset", type="primary")

# st.button("Just a button", type="secondary")

# if st.button('Say hello'):
# 	st.write('Why hello there')
# else:
# 	st.write('Goodbye')

st.header('st.write demo')

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
