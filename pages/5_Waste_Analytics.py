from datetime import date
import streamlit as st
from sqlalchemy import select
from database import InventoryItem, SessionLocal, WasteLog, init_db
from expiry import classify

init_db()
st.title("Waste Log and Analytics")
REASONS = ["Expired", "Spoiled", "Leftover thrown", "Bought too much", "Other"]

st.subheader("Discard an item")
with SessionLocal() as s:
    items = s.scalars(select(InventoryItem).order_by(InventoryItem.expiry_date)).all()
if not items:
    st.info("Inventory is empty, nothing to discard.")
else:
    opts = {f"{it.id} - {it.name} ({classify(it.expiry_date)})": it.id for it in items}
    choice = st.selectbox("Item", list(opts.keys()))
    reason = st.selectbox("Reason", REASONS)
    if st.button("Move to waste log"):
        with SessionLocal() as s:
            it = s.get(InventoryItem, opts[choice])
            if it:
                s.add(WasteLog(item_name=it.name, quantity=it.quantity, unit=it.unit,
                               category=it.category, reason=reason, logged_date=date.today()))
                s.delete(it)
                s.commit()
        st.rerun()

with SessionLocal() as s:
    logs = s.scalars(select(WasteLog).order_by(WasteLog.logged_date, WasteLog.id)).all()

st.subheader("Analytics")
if not logs:
    st.info("No waste logged yet. Discard an item above to see analytics.")
else:
    cats, reasons, days = {}, {}, {}
    for l in logs:
        cats[l.category] = cats.get(l.category, 0) + 1
        reasons[l.reason] = reasons.get(l.reason, 0) + 1
        d = str(l.logged_date)
        days[d] = days.get(d, 0) + 1

    c1, c2 = st.columns(2)
    c1.metric("Items wasted", len(logs))
    c2.metric("Most wasted category", max(cats, key=cats.get))

    def chart(title, data):
        st.markdown("**" + title + "**")
        try:
            import plotly.graph_objects as go
            fig = go.Figure(go.Bar(x=list(data.keys()), y=list(data.values())))
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig)
        except Exception:
            top = max(data.values())
            for k, v in data.items():
                st.write(f"{k}: {'#' * round(10 * v / top)} {v}")

    chart("Waste by category (items)", cats)
    chart("Waste by reason (items)", reasons)
    chart("Waste by date (items)", days)

    st.subheader("Waste log")
    for l in reversed(logs):
        st.write(f"{l.logged_date} | {l.item_name} ({l.quantity:g} {l.unit}) | {l.category} | {l.reason}")
