import streamlit as st
from database import get_product_data

engine = st.session_state.engine
df = get_product_data(engine)

st.write(
    [
        {
            "ID": i,
            "NAME": row["Name"],
            "STOCK QTY": row["Stock Quantity"],
            "MINIMUM STOCK QTY": row["Minimum Stock"],
            "ORDER QTY": row["Order Quantity"],
        }
        for i, row in df.iterrows()
    ]
)
