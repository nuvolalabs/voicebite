"""Seed menu: Hakka Legend (Markham). Shared by the in-memory data backend.
Menu modeling notes for voice:
- Each base dish is one item. `options` lists selectable proteins/styles the bot
  can offer (e.g. chicken/beef/shrimp/vegetable). When options share one price,
  `option_prices` is omitted and the base `price` applies.
- Soups have size-based pricing, captured in `option_prices` (small/medium/large).
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models import TakeoutOrder, Reservation, OrderItem


# ---- Seed menu: Hakka Legend ----
def _m(iid, name, cat, price, options=None, option_prices=None):
    d = {"id": iid, "name": name, "category": cat, "price": float(price)}
    if options:
        d["options"] = options
    if option_prices:
        d["option_prices"] = {k: float(v) for k, v in option_prices.items()}
    return d


PROTEIN = ["chicken", "beef", "shrimp", "vegetable"]
SOUP_SIZES = {"small": 6.99, "medium": 9.99, "large": 13.99}

MENU: dict[str, dict] = {}

# APPETIZERS
for iid, name, price in [
    ("a1", "Lollipop Chicken (8 pcs)", 15.50), ("a2", "Shrimp Pakora (10 pcs)", 15.50),
    ("a3", "Spicy Pepper Chicken", 15.50), ("a4", "Fish Pakora (10 pcs)", 15.50),
    ("a5", "Chicken Pakora (10 pcs)", 15.50), ("a6", "Deep Fried Calamari", 15.50),
    ("a7", "Guyanese Style Chicken", 15.50), ("a8", "Vegetable Pakora (10 pcs)", 14.25),
    ("a9", "Chilli Chicken Wings Dry (10 pcs)", 12.25), ("a10", "Honey Garlic Chicken Wings Dry (10 pcs)", 12.25),
    ("a11", "Fried Chicken Wings (10 pcs)", 11.50), ("a12", "Fried Shrimp Wonton (15 pcs)", 9.75),
    ("a13", "Fried Chicken Wonton (15 pcs)", 9.75), ("a14", "Legend's Spicy Poutine", 9.75),
    ("a15", "Legend's Chili Fries Dry", 9.75), ("a16", "Chicken Dumplings (10 pcs)", 10.00),
    ("a17", "Mango Salad", 8.75), ("a18", "French Fries", 7.50), ("a19", "Onion Rings", 7.50),
    ("a20", "Fried Vegetable Spring Roll (3 pcs)", 5.95), ("a21", "Fried Shrimp Spring Roll (2 pcs)", 5.95),
    ("a22", "Fried Curry Chicken Spring Roll (2 pcs)", 5.95),
]:
    MENU[iid] = _m(iid, name, "appetizers", price)

# SOUPS (size pricing)
for iid, name in [
    ("s1", "Manchurian Soup (Chicken & Shrimp)"), ("s2", "Vegetable Manchurian Soup"),
    ("s3", "Chicken Hot & Sour Soup"), ("s4", "Seafood Hot & Sour Soup"),
    ("s5", "Vegetable Hot & Sour Soup"), ("s6", "Chicken Corn Soup"), ("s7", "Crab Corn Soup"),
    ("s8", "Vegetable Corn Soup"), ("s9", "Manchow Soup (Chicken & Shrimp)"),
    ("s10", "Vegetable Manchow Soup"), ("s11", "Chicken & Shrimp Thai Soup"),
    ("s12", "Vegetable Thai Soup"), ("s13", "Shrimp or Chicken Wonton Soup"),
]:
    MENU[iid] = _m(iid, name, "soups", 9.99, options=list(SOUP_SIZES.keys()), option_prices=SOUP_SIZES)

# NOODLES
MENU["n1"] = _m("n1", "Hakka Noodle", "noodles", 14.00,
                options=["seafood", "house special", "chicken", "shrimp", "beef", "vegetable", "paneer"],
                option_prices={"seafood": 16.00, "house special": 15.00, "paneer": 15.00})
MENU["n2"] = _m("n2", "Shanghai Noodles", "noodles", 14.00,
                options=["seafood", "chicken", "shrimp", "beef", "vegetable"],
                option_prices={"seafood": 16.00})
MENU["n3"] = _m("n3", "Singapore Noodle (Curry Rice Vermicelli)", "noodles", 14.00,
                options=["seafood", "house special", "chicken", "shrimp", "beef", "vegetable"],
                option_prices={"seafood": 16.00, "house special": 15.00})
MENU["n4"] = _m("n4", "Cantonese Chow Mein", "noodles", 15.00,
                options=["seafood", "chicken & shrimp", "vegetable"],
                option_prices={"seafood": 16.00, "chicken & shrimp": 16.00})
MENU["n5"] = _m("n5", "Hakka Rice Vermicelli", "noodles", 14.00,
                options=["seafood", "house special", "chicken", "shrimp", "beef", "vegetable"],
                option_prices={"seafood": 16.00, "house special": 15.00})
for iid, name, price in [
    ("n6", "Chilli Chicken on Wok Fried Noodles", 16.00), ("n7", "Manchurian Chicken on Wok Fried Noodles", 16.00),
    ("n8", "Triple Szechuan - Vegetable (3 layers)", 16.00), ("n9", "Triple Szechuan - Chicken (3 layers)", 16.00),
    ("n10", "Guyanese Chicken on Hakka Noodles", 15.00), ("n11", "Chicken Sweet American Chop Suey", 15.00),
    ("n12", "Vegetable Sweet American Chop Suey", 15.00),
]:
    MENU[iid] = _m(iid, name, "noodles", price)

# RICE
MENU["r1"] = _m("r1", "House Special Fried Rice", "rice", 15.00,
                options=["shrimp", "chicken", "beef", "vegetable", "seafood", "paneer"],
                option_prices={"seafood": 15.00, "paneer": 15.00})
MENU["r2"] = _m("r2", "Bombay Fried Rice", "rice", 14.00,
                options=["house special", "chicken", "shrimp", "beef", "vegetable"],
                option_prices={"house special": 15.00})
for iid, name, price in [
    ("r3", "Guyanese Chicken on Egg Fried Rice", 15.00), ("r4", "Seafood Fried Rice", 15.00),
    ("r5", "Paneer Fried Rice", 15.00), ("r6", "Fried Rice Vegetable", 14.00),
    ("r7", "Mushroom Fried Rice", 14.00), ("r8", "Egg Fried Rice", 14.00), ("r9", "Steamed Rice", 2.50),
]:
    MENU[iid] = _m(iid, name, "rice", price)

# CHEF'S SPECIALTIES ($17.50 flat)
for iid, name in [
    ("c1", "Bollywood Chicken"), ("c2", "Bollywood Paneer"), ("c3", "Chilli Mutton"),
    ("c4", "Phoenix Chicken or Beef"), ("c5", "Phoenix Fish or Prawns"),
    ("c6", "88 Legend's Chicken or Paneer or Veg Ball or Prawns"),
]:
    MENU[iid] = _m(iid, name, "chef", 17.50)

# CHICKEN
MENU["k1"] = _m("k1", "Chicken", "chicken", 15.50,
                options=["chili", "manchurian", "szechuan", "spicy garlic", "hot garlic",
                         "general tso", "mongolian", "orange", "yellow curry", "sweet garlic",
                         "ginger", "black bean", "mixed vegetables", "snow peas & mushrooms", "sweet & sour"],
                option_prices={"sweet & sour manchurian": 16.50, "mango": 16.50, "sesame": 16.50,
                               "crispy ginger": 16.50, "bombay": 16.50, "honey garlic": 15.50,
                               "sliced black pepper": 15.50, "eggplant": 15.50})
for iid, name, price in [
    ("k2", "Bombay Chicken (Dry)", 16.50), ("k3", "Crispy Ginger Chicken (Dry)", 16.50),
    ("k4", "Sweet & Sour Manchurian Chicken (Dry)", 16.50), ("k5", "Mango Chicken (Dry)", 16.50),
    ("k6", "Sesame Chicken (Dry)", 16.50), ("k7", "Honey Garlic Chicken (Dry)", 15.50),
    ("k8", "Chicken in Hot Garlic Sauce", 15.50), ("k9", "General TSO Chicken", 15.50),
    ("k10", "Mongolian Chicken", 15.50), ("k11", "Orange Chicken", 15.50),
    ("k12", "Chicken in Yellow Curry Sauce", 15.50), ("k13", "Chicken Ma Po Tofu", 15.50),
    ("k14", "Sliced Chicken in Black Pepper Sauce", 15.50), ("k15", "Chicken with Eggplant", 15.50),
    ("k16", "Chicken in Sweet Garlic Sauce", 15.50), ("k17", "Ginger Chicken", 15.50),
    ("k18", "Chicken with Black Bean Sauce", 15.50), ("k19", "Chicken with Mixed Vegetables", 15.50),
    ("k20", "Chicken with Snow Peas & Fresh Mushrooms", 15.50), ("k21", "Sweet & Sour Chicken", 15.50),
]:
    MENU[iid] = _m(iid, name, "chicken", price)

# SEAFOOD / PRAWNS
MENU["p1"] = _m("p1", "Prawns", "seafood", 16.50,
                options=["chili", "manchurian", "szechuan", "spicy garlic", "eggplant",
                         "yellow curry", "ma po tofu", "general tso", "sweet garlic", "sweet & sour",
                         "lobster sauce", "black bean", "mixed vegetables", "snow peas & mushrooms"])
for iid, name, price in [
    ("p2", "Spicy Deep Fried Mixed Seafood (Dry)", 18.95), ("p3", "Bombay Prawns (Dry)", 17.50),
    ("p4", "Sweet & Sour Manchurian Prawns", 17.50), ("p5", "Mango Prawns (Sweet & Spicy)", 16.50),
    ("p6", "Spicy Deep Fried Prawns (Dry)", 16.50), ("p7", "Prawns with Eggplant", 16.50),
    ("p8", "Prawns in Yellow Curry Sauce", 16.50), ("p9", "Prawns Ma Po Tofu", 16.50),
    ("p10", "General TSO Prawns (Sweet & Spicy)", 16.50), ("p11", "Prawns in Sweet Garlic Sauce", 16.50),
    ("p12", "Sweet & Sour Prawns", 16.50), ("p13", "Prawns in Lobster Sauce (w/ diced Chicken)", 16.50),
    ("p14", "Prawns with Black Bean Sauce", 16.50), ("p15", "Prawns with Mixed Vegetables", 16.50),
    ("p16", "Prawns with Snow Peas & Fresh Mushrooms", 16.50),
]:
    MENU[iid] = _m(iid, name, "seafood", price)

# VEGETARIAN
MENU["v1"] = _m("v1", "Vegetable Entree", "vegetarian", 14.50,
                options=["bombay paneer", "vegetable ball", "paneer", "eggplant", "mixed vegetable",
                         "cauliflower", "okra", "tofu", "manchurian tofu", "spicy garlic tofu",
                         "spicy deep fried tofu", "yellow curry", "home style bean curd", "garlic sauce",
                         "sweet & sour", "green beans", "broccoli", "beansprout chop suey"],
                option_prices={"bombay paneer": 14.95})
for iid, name, price in [
    ("v2", "Stir Fried Green Beans (Dry)", 14.50), ("v3", "Stir Fried Broccoli", 14.50),
    ("v4", "Beansprout Chop Suey", 14.50),
]:
    MENU[iid] = _m(iid, name, "vegetarian", price)

# THAI
MENU["t1"] = _m("t1", "Red Coconut Curry", "thai", 16.50,
                options=["seafood", "shrimp", "beef", "chicken", "vegetable"],
                option_prices={"seafood": 18.95, "shrimp": 18.95})
MENU["t2"] = _m("t2", "Green Coconut Curry", "thai", 16.50,
                options=["seafood", "shrimp", "beef", "chicken", "vegetable"],
                option_prices={"seafood": 18.95, "shrimp": 18.95})
for iid, name, price in [
    ("t3", "Thai Seafood Fried Rice", 15.50), ("t4", "Thai Shrimp Fried Rice", 15.50),
    ("t5", "Thai Chicken or Beef Fried Rice", 14.50), ("t6", "Pad Thai Shrimp or Chicken", 14.25),
    ("t7", "Pad Thai Vegetable", 14.25),
]:
    MENU[iid] = _m(iid, name, "thai", price)

# LUNCH SPECIALS ($11.50 + tax, weekdays 11-3)
for iid, name in [
    ("l1", "Mango Chicken or Shrimp (Dry)"), ("l2", "General TSO Chicken or Shrimp"),
    ("l3", "Honey Garlic Chicken or Shrimp (Dry)"), ("l4", "Sesame Chicken or Shrimp (Dry)"),
    ("l5", "Bombay Chicken (Dry)"), ("l6", "Shrimp with Lobster Sauce (w/ diced Chicken)"),
    ("l7", "Thai Green or Red Curry Chicken or Vegetable"), ("l8", "Crispy Ginger Chicken or Beef (Dry)"),
    ("l9", "Chicken or Beef in Black Bean Sauce w/ Fried Noodles"), ("l10", "Chicken or Beef with Green Beans"),
    ("l11", "Sliced Chicken or Beef in Black Pepper Sauce"), ("l12", "Chicken or Vegetable Cantonese Chow Mein"),
    ("l13", "Chicken or Vegetable Singapore Noodles"), ("l14", "Chicken or Vegetable Pad Thai"),
    ("l15", "Chilli Chicken or Beef or Fish or Shrimp"), ("l16", "Manchurian Chicken or Beef or Fish or Shrimp"),
    ("l17", "Black Bean Sauce with Chicken or Beef or Fish or Shrimp"),
    ("l18", "Curry Chicken or Beef or Fish or Shrimp"),
    ("l19", "Mixed Vegetables with Chicken or Beef or Fish or Shrimp"),
    ("l20", "Szechuan Chicken or Beef or Fish or Shrimp"),
    ("l21", "Sweet & Sour Chicken or Beef or Fish or Shrimp"),
    ("l22", "Chicken Wings (5) with Egg Fried Rice"), ("l23", "Ma Po Tofu Chicken or Shrimp"),
    ("l24", "Chilli Sauce with Mixed Vegetables or Tofu or Eggplant or Veg Balls"),
    ("l25", "Manchurian Sauce with Mixed Vegetables or Tofu or Eggplant or Veg Balls"),
    ("l26", "Spicy Garlic Sauce with Mixed Vegetables or Tofu or Eggplant or Veg Balls"),
    ("l27", "Chicken or Shrimp Eggplant"), ("l28", "Beef with Broccoli"),
]:
    MENU[iid] = _m(iid, name, "lunch", 11.50)


# Public export used by db.py
MENU = MENU
