from datetime import date, timedelta

import streamlit as st
from pydantic import ValidationError
from sqlalchemy import select
from database import InventoryItem, SessionLocal, init_db
from expiry import classify, days_left
from schemas import ItemCreate

init_db()
st.title("Inventory")
CATEGORIES = ["Vegetables", "Fruits", "Dairy", "Grains", "Pulses", "Meat/Eggs", "Snacks", "Other"]
UNITS = ["pcs", "kg", "g", "L", "ml", "packet"]

st.subheader("Add item")
with st.form("add_item", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Item name")
    quantity = c2.number_input("Quantity", min_value=0.0, value=1.0, step=0.5)
    unit = c3.selectbox("Unit", UNITS)
    c4, c5, c6 = st.columns(3)
    category = c4.selectbox("Category", CATEGORIES)
    purchase_date = c5.date_input("Purchase date", value=date.today())
    expiry_date = c6.date_input("Expiry date", value=date.today() + timedelta(days=7))
    submitted = st.form_submit_button("Add item")

if submitted:
    try:
        data = ItemCreate(name=name, quantity=quantity, unit=unit, category=category,
                          purchase_date=purchase_date, expiry_date=expiry_date)
        with SessionLocal() as s:
            s.add(InventoryItem(**data.model_dump()))
            s.commit()
        st.success(f"{data.name} added.")
    except ValidationError as e:
        for err in e.errors():
            st.error(err["msg"])

st.subheader("Your items")
search = st.text_input("Search by name")
with SessionLocal() as s:
    items = s.scalars(select(InventoryItem).order_by(InventoryItem.expiry_date)).all()
if search:
    items = [it for it in items if search.lower() in it.name.lower()]

if not items:
    st.info("No items yet.")
else:
    rows = []
    for it in items:
        rows.append({"ID": it.id, "Item": it.name, "Qty": f"{it.quantity:g} {it.unit}",
                     "Category": it.category, "Expiry": it.expiry_date,
                     "Days left": days_left(it.expiry_date), "Status": classify(it.expiry_date)})
    st.markdown("\n".join(["| " + " | ".join(rows[0].keys()) + " |", "|" + "---|" * len(rows[0]), *["| " + " | ".join(str(v) for v in r.values()) + " |" for r in rows]]))
    st.subheader("Remove item")
    options = {f"{it.id} - {it.name}": it.id for it in items}
    choice = st.selectbox("Select item", list(options.keys()))
    if st.button("Delete selected item"):
        with SessionLocal() as s:
            obj = s.get(InventoryItem, options[choice])
            if obj:
                s.delete(obj)
                s.commit()
        st.rerun()
