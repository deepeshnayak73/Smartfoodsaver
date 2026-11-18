import json
from datetime import date
import streamlit as st
from sqlalchemy import select
from database import MealPlan, SessionLocal, init_db

init_db()
st.title("Meal Planner")
SLOTS = ["Breakfast", "Lunch", "Snack", "Dinner"]

recipes = st.session_state.get("recipes", [])
st.subheader("Add a meal")
if not recipes:
    st.info("Generate recipes on the Recipes page first, then come back here.")
else:
    titles = [r.title for r in recipes]
    choice = st.selectbox("Recipe", titles)
    c1, c2 = st.columns(2)
    d = c1.date_input("Date", value=date.today())
    slot = c2.selectbox("Meal", SLOTS)
    if st.button("Add to plan"):
        r = recipes[titles.index(choice)]
        with SessionLocal() as s:
            s.add(MealPlan(plan_date=d, slot=slot, title=r.title,
                           used=json.dumps(r.ingredients_used),
                           missing=json.dumps(r.missing_ingredients)))
            s.commit()
        st.success("Added to plan.")

st.subheader("Your plan")
with SessionLocal() as s:
    plans = s.scalars(select(MealPlan).order_by(MealPlan.plan_date, MealPlan.id)).all()
if not plans:
    st.info("No meals planned yet.")
for p in plans:
    c1, c2 = st.columns([5, 1])
    c1.write(f"{p.plan_date} | {p.slot}: {p.title}")
    if c2.button("Remove", key=f"del{p.id}"):
        with SessionLocal() as s:
            obj = s.get(MealPlan, p.id)
            if obj:
                s.delete(obj)
                s.commit()
        st.rerun()
