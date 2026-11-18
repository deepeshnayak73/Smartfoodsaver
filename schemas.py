from datetime import date
from pydantic import BaseModel, field_validator, model_validator

class ItemCreate(BaseModel):
    name: str
    quantity: float
    unit: str
    category: str
    purchase_date: date
    expiry_date: date

    @field_validator("name")
    @classmethod
    def name_ok(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Item name cannot be empty")
        return v.title()

    @field_validator("quantity")
    @classmethod
    def qty_ok(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @model_validator(mode="after")
    def dates_ok(self):
        if self.expiry_date < self.purchase_date:
            raise ValueError("Expiry date cannot be before purchase date")
        return self


class Recipe(BaseModel):
    title: str
    description: str = ""
    time_minutes: int = 0
    ingredients_used: list[str] = []
    missing_ingredients: list[str] = []
    steps: list[str] = []


class RecipeList(BaseModel):
    recipes: list[Recipe]
