# import necessary libraries
import streamlit as st
import pandas as pd
import warnings
from config import *
import hydralit_components as hc
from helper import *
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import google.generativeai as palm
from io import StringIO

PAML_API_KEY = st.secrets["PAML_API_KEY"]
palm.configure(api_key=PAML_API_KEY)

# This will ignore all warning messages
warnings.filterwarnings('ignore')

# setup page
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout='wide'
)


def get_response(prompt):
    response = palm.chat(messages=prompt)
    return response.last


# styling web-page
local_css("styles.css")

with st.sidebar:
    # st.title(PAGE_TITLE + PAGE_ICON)
    # ---- LOAD ASSETS ----
    lottie_coding = load_lottieurl(ANIMATION)
    st_lottie(lottie_coding, height=300, key="coding")
    # st.image(img_url)
    with st.form("my_form"):
        st.header("Personal Details")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Age")
            st.header("Gender")
            st.header("Weight (KG)")
            st.header("Height (M)")
            st.header("Activity Level")
            st.header("Goal")
        with col2:
            age = st.number_input("Please Enter your age", min_value=5,
                                  value=24, step=1, label_visibility="collapsed")
            gender = option = st.selectbox(
                'What is you gender?', gender_list, label_visibility="collapsed")
            weight = st.number_input("Please Enter your weight in kilograms:",
                                     value=90, min_value=2, label_visibility="collapsed")
            height = st.number_input("Please Enter your height in meters:",
                                     value=1.90, min_value=0.5, label_visibility="collapsed")
            activity_level = st.selectbox(
                'What is your activity_level?', activity_level, help=activity_details, label_visibility="collapsed")
            goal = st.selectbox('What is your goal?',
                                goal_list, label_visibility="collapsed")

        c = st.columns((1, 4, 1))
        with c[1]:
            submitted = st.form_submit_button("Submit")
            person_info["age"] = age
            person_info["sex"] = gender
            person_info["height"] = height
            person_info["weight"] = weight
            person_info["activity level"] = activity_level
            person_info["goal"] = goal

# main functions


def home(person_info):
    bmi, bmi_class = calculate_bmi(person_info)
    if bmi_class == "underweight":
        bmi_max = 18.5
    elif bmi_class == "normal weight":
        bmi_max = 25
    elif bmi_class == "overweight":
        bmi_max = 30
    else:
        bmi_max = bmi

    bmr, tdee = energy_calc(person_info)
    macros_req = macro_perc(person_info, tdee)
    hc_theme = {'bgcolor': '#f9e9de', 'title_color': '#3a4664',
                'content_color': '#3e5172', 'icon_color': 'black', 'icon': 'fa fa-dumbbell'}

    cols = st.columns(3)
    with cols[1]:
        if bmi_class == "normal weight":
            hc.info_card(title='Body Mass Index', content=f'{round(bmi, 2)}', sentiment='good', bar_value=round(
                (bmi * 100) / bmi_max, 2))
        else:
            hc.info_card(title='Body Mass Index', content=f'{round(bmi, 2)}', sentiment='bad', bar_value=round(
                (bmi * 100) / bmi_max, 2))
    with cols[0]:
        hc.info_card(title='Metabolic Rate',
                     content=f'{round(bmr, 2)}', bar_value=100, theme_override=hc_theme)
    with cols[2]:
        hc.info_card(title='Daily Expediture',
                     content=f'{round(tdee, 2)}', bar_value=100, theme_override=hc_theme)

    st.header("Macro Management")
    cols = st.columns(3)
    theme_neutral = {'bgcolor': '#FBECB2', 'title_color': '#5272F2',
                     'content_color': '#5272F2', 'icon_color': 'orange', 'icon': 'fa fa-bolt'}
    with cols[1]:
        hc.info_card(
            title='Protein', content=f'{round(macros_req["protein"], 2)}', bar_value=100, theme_override=theme_neutral)
    with cols[0]:
        hc.info_card(
            title='Fats', content=f'{round(macros_req["fat"], 2)}', bar_value=100, theme_override=theme_neutral)
    with cols[2]:
        hc.info_card(title='Carbohydrates',
                     content=f'{round(macros_req["carbs"], 2)}', bar_value=100, theme_override=theme_neutral)


def diet(person_info):
    search = st.text_input("Enter the food Item...",
                           placeholder="Please Enter the food item you want to check macros for...")
    f = st.button("Find Macro Breakdown", type="primary")
    if f:
        with st.spinner(f"Finding marco breakdown of **{search}**"):
            res = get_response(
                f"return a table containing marco breakdown of the item {search}, the table should have columns Nutrient and Amount.")
            res = extract_markdown_table(res)
            st.write(res)
            st.divider()


def plan(person_info):
    with st.form("Planner"):
        st.header("Tell us a bit about your preferences!!")
        cols = st.columns(3)
        with cols[0]:
            loc = st.selectbox('What is your ethnicity?', [
                               "Indian", "American", "Chinese"])
        with cols[1]:
            vg = st.selectbox('Are you Veg or Non-Veg?', ["Veg", "Non-Veg"])
        with cols[2]:
            remarks = st.text_input(
                "Any other preferences", placeholder="Let us know what you like or dislike!")
            prompt = f"""
      Generate a diet plan in a tabular format (make sure to return only the table not any text).
      For a {person_info["sex"]} {loc} person with bmr of {bmr}, bmi of {bmi} and total daily expenditure of {tdee}.
      Suggest dishes for diet which are strictly {vg}.
      and they have following preferences : {remarks}
      The goal is to person_info["goal"].
      the table should be have these features: 1. mealtime (breakfast, lunch, dinner, etc)
      2. food item
      3. macro breakdown
      """
            response = get_response(prompt)
            st.write(response)

        s = st.form_submit_button("Generate Diet Plan")
    with st.spinner('Generating a diet plan suitable for you Please Wait....'):
        if s:
            bmi, bmi_class = calculate_bmi(person_info)
            bmr, tdee = energy_calc(person_info)
            prompt = f"""
      Generate a diet plan in a tabular format (make sure to return only the table not any text).
      For a {person_info["sex"]} {loc} person with bmr of {bmr}, bmi of {bmi} and total daily expenditure of {tdee}.
      Suggest dishes for diet which are strictly {vg}.
      and they have following preferences : {remarks}
      The goal is to person_info["goal"].
      the table should be have these features: 1. mealtime (breakfast, lunch, dinner, etc)
      2. food item
      3. macro breakdown
      """
            response = get_response(prompt)
            st.write(response)


selected = option_menu(
    menu_title=None,  # required
    options=["Home", "Diet Calculator", "Diet Planner"],  # required
    icons=["house", "globe2", "envelope"],  # optional
    menu_icon="cast",  # optional
    default_index=0,  # optional
    orientation="horizontal",
)

if selected == "Home":
    home(person_info)
elif selected == "Diet Calculator":
    diet(person_info)
elif selected == "Diet Planner":
    plan(person_info)
else:
    st.error("Please Submit your information")
