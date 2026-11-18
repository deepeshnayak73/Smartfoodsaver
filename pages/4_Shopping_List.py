import json
import streamlit as st
from sqlalchemy import select
from database import InventoryItem, MealPlan, SessionLocal, init_db

init_db()
st.title("Shopping List")
st.caption("Built from the missing ingredients of your planned meals.")

with SessionLocal() as s:
    plans = s.scalars(select(MealPlan).order_by(MealPlan.plan_date)).all()
    stock = [i.name.lower() for i in s.scalars(select(InventoryItem)).all()]

need = {}
for p in plans:
    for ing in json.loads(p.missing):
        key = ing.strip().lower()
        if not key:
            continue
        if any(key in have or have in key for have in stock):
            continue
        need.setdefault(key, {"name": ing.strip(), "meals": []})
        need[key]["meals"].append(p.title)

if not plans:
    st.info("Plan some meals on the Meal Planner page first.")
elif not need:
    st.success("You already have everything for your planned meals.")
else:
    st.subheader(f"{len(need)} item(s) to buy")
    for i, (key, v) in enumerate(need.items()):
        st.checkbox(f"{v['name']}  (for: {', '.join(sorted(set(v['meals'])))})", key=f"buy{i}")
    text = "\n".join("- " + v["name"] for v in need.values())
    st.download_button("Download list (.txt)", text, file_name="shopping_list.txt")
