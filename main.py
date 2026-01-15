import streamlit as st
from database import create_db, get_product_data, get_products
from frontend import product_component
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet


if "engine" not in st.session_state:
    st.session_state.engine = create_db()

# Update static db_file_path for Streamlit static serving
with open("static/inventory.json", "w") as f:
    json.dump(get_product_data(st.session_state.engine, return_json=True), f)


st.title("Webshop")

products = get_products(st.session_state.engine)


col1, col2 = st.columns(2)
for i, p in enumerate(products):
    with col1 if i % 2 == 0 else col2:
        product_component(p)


st.divider()
st.title("Database Viewer")

df = get_product_data(st.session_state.engine)
st.write(df)


def builld_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    title = Paragraph("Inventory Report", styles["Title"])
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data, colWidths=[120] * len(df.columns))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    doc.build([title, table])
    buffer.seek(0)
    return buffer


if st.download_button(
    label="Download PDF",
    data=builld_pdf(),
    file_name="inventory.pdf",
    mime="application/pdf",
):
    st.success("PDF generated successfully!")
