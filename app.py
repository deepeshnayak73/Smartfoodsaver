import streamlit as st
from sqlalchemy import select
from database import InventoryItem, SessionLocal, init_db
from expiry import classify, days_left

st.set_page_config(page_title="Smart Food Saver", layout="wide")
init_db()
st.title("Smart Food Saver")
st.caption("Track your food, use it before it expires, waste less.")

with SessionLocal() as s:
    items = s.scalars(select(InventoryItem).order_by(InventoryItem.expiry_date)).all()

counts = {"Fresh": 0, "Expiring Soon": 0, "Expired": 0}
for it in items:
    counts[classify(it.expiry_date)] += 1

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total items", len(items))
c2.metric("Fresh", counts["Fresh"])
c3.metric("Expiring soon", counts["Expiring Soon"])
c4.metric("Expired", counts["Expired"])

st.subheader("Needs attention")
shown = False
for it in items:
    status = classify(it.expiry_date)
    if status == "Fresh":
        continue
    shown = True
    d = days_left(it.expiry_date)
    when = f"expired {-d} day(s) ago" if d < 0 else f"expires in {d} day(s)"
    st.write(f"{status}: {it.name} ({it.quantity:g} {it.unit}) - {when}")
if not shown:
    st.success("Nothing is expiring soon.")
