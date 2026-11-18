import streamlit as st
from sqlalchemy import select
from database import InventoryItem, SessionLocal, init_db
from expiry import classify, days_left
from recipes import suggest_recipes

init_db()
st.title("AI Recipe Suggestions")
st.caption("Recipes use your inventory, items expiring soonest come first.")

with SessionLocal() as s:
    all_items = s.scalars(select(InventoryItem).order_by(InventoryItem.expiry_date)).all()

items = [it for it in all_items if classify(it.expiry_date) != "Expired"]
expired = [it for it in all_items if classify(it.expiry_date) == "Expired"]

if expired:
    st.warning("Expired items are not used in recipes: " + ", ".join(it.name for it in expired))

if not items:
    st.info("Add some non-expired items in the Inventory page first.")
else:
    st.subheader("Ingredients that will be used")
    for it in items:
        st.write(f"{it.name} ({it.quantity:g} {it.unit}) - {classify(it.expiry_date)}, {days_left(it.expiry_date)} day(s) left")

    c1, c2 = st.columns(2)
    diet = c1.selectbox("Diet", ["Any", "Vegetarian", "Vegan", "Eggetarian"])
    num = c2.slider("Number of recipes", 1, 5, 3)

    if st.button("Get recipes"):
        data = [{"name": it.name, "qty": f"{it.quantity:g} {it.unit}",
                 "status": classify(it.expiry_date), "days_left": days_left(it.expiry_date)} for it in items]
        with st.spinner("Asking Gemini, this can take up to a minute..."):
            try:
                st.session_state["recipes"] = suggest_recipes(data, num, diet)
            except Exception as e:
                st.session_state["recipes"] = []
                st.error(f"Could not get recipes: {e}")

    for r in st.session_state.get("recipes", []):
        with st.expander(f"{r.title} - {r.time_minutes} min", expanded=True):
            st.write(r.description)
            st.write("**Uses:** " + ", ".join(r.ingredients_used))
            if r.missing_ingredients:
                st.write("**You also need:** " + ", ".join(r.missing_ingredients))
            for i, step in enumerate(r.steps, 1):
                st.write(f"{i}. {step}")
