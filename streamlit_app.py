import streamlit as st

st.button("Reset", type="primary")

st.button("Just a button", type="secondary")

if st.button('Say hello'):
	st.write('Why hello there')
else:
	st.write('Goodbye')