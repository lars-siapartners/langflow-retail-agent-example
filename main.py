import streamlit as st
from database import create_db, get_product_data, get_products
from frontend import product_fragment




if "engine" not in st.session_state:
    st.session_state.engine = create_db()
    


st.title("Webshop")

products = get_products(st.session_state.engine)


col1, col2 = st.columns(2)
for i, p in enumerate(products):
    with col1 if i % 2 == 0 else col2:
        product_fragment(p)


st.divider()
st.title("Database Viewer")

df = get_product_data(st.session_state.engine)
st.write(df)
