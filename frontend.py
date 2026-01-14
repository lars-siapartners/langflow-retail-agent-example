from database import Product, process_order, CustomerOrder
import streamlit as st


@st.fragment
def product_fragment(product: Product):
    st.subheader(product.name)
    st.write(f"Description: {product.description or 'N/A'}")
    st.write(f"Price: ${product.price:.2f}")
    st.write(f"Supplier ID: {product.supplier}")
    if st.button("Order now", key=product.id):
        order = CustomerOrder(product_id=product.id, quantity=1)
        try:
            process_order(order, st.session_state.engine)
            st.success(f"Ordered {product.name} successfully!")
        except ValueError as e:
            st.error(str(e))
