import streamlit as st
import pandas as pd
import numpy as np
from config import *
import requests
import re


def calculate_bmi(person_info):
    bmi = person_info["weight"] / person_info["height"] ** 2

    if bmi < 18.5:
        bmi_class = "underweight"
    elif bmi < 25:
        bmi_class = "normal weight"
    elif bmi < 30:
        bmi_class = "overweight"
    else:
        bmi_class = "obese"

    return bmi, bmi_class


def energy_calc(person_info):
    # Calculate the BMR using the Harris-Benedict equation
    if person_info["sex"] == "Male":
        bmr = 88.362 + (13.397 * person_info["weight"]) + (
            4.799 * person_info["height"]) - (5.677 * person_info["age"])
    else:
        bmr = 447.593 + (9.247 * person_info["weight"]) + (
            3.100 * person_info["height"]) - (4.330 * person_info["age"])

    # Calculate the TDEE using the activity level multiplier
    tdee = bmr * activity_level_multipliers[person_info["activity level"]]
    return bmr, tdee


def macro_perc(person_info, calories):
    if person_info["goal"].lower() == 'lose weight':
        protein_percentage = 30
        fat_percentage = 25
    elif person_info["goal"].lower() == 'maintain':
        protein_percentage = 25
        fat_percentage = 30
    elif person_info["goal"].lower() == 'gain muscle':
        protein_percentage = 35
        fat_percentage = 20
    else:
        raise ValueError("Invalid goal. Use 'lose', 'maintain', or 'gain'.")

    carb_percentage = 100 - (protein_percentage + fat_percentage)

    protein = (protein_percentage / 100) * calories / 4
    fat = (fat_percentage / 100) * calories / 9
    carbs = (carb_percentage / 100) * calories / 4

    return {'protein': protein, 'fat': fat, 'carbs': carbs}

# load css


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# to load lottie animation


def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# extract table from markdown


def extract_markdown_table(markdown_string):
    # Define the regular expression pattern for extracting Markdown tables
    table_pattern = re.compile(
        r'\|(.+?)\|(.+?)\|.*?\n((?:\|.*?\|.*?\n)+)', re.DOTALL)

    # Find the first match in the Markdown string
    match = table_pattern.search(markdown_string)

    if not match:
        print("No Markdown table found.")
        return None

    # Extract the matched table content
    table_content = match.group(0)

    return table_content
