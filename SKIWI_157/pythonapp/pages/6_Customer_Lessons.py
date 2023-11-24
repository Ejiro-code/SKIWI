import streamlit as st
import pandas as pd
import pymysql

st.set_page_config(page_title="Skiwi", layout='wide')
st.header("SKIWI Enterprises Database")


connection = pymysql.connect(
    user='root', password='goodgradeplease', database='SKIWI_DB', host='mysql', port=3306,     cursorclass=pymysql.cursors.Cursor)

query = '''
SELECT
    Customer.EMAIL,
    Customer.FIRST_NAME,
    Customer.LAST_NAME,
    Customer.PHONE_NUMBER,
    Customer.AGE,
    Lessons.LESSON_NAME,
    Lessons.LESSON_LEVEL,
    Lessons.PRICE,
    Lessons.INSTRUCTOR_NAME,
    Lessons.INSTRUCTOR_SKILL_LEVEL
FROM
    Customer
JOIN
    Lessons ON Customer.LESSON_ID = Lessons.LESSON_ID;
    '''

df = pd.read_sql(query, connection)
df_cols = list(df.columns)

form = st.form("Search by Column")
col_selection = form.selectbox('column filter', df_cols)
col_val = form.text_input(label="")
form_submit = form.form_submit_button(label='submit')


html = df.to_html
if form_submit and len(col_val) > 0:
    query = f'''
    SELECT * FROM CS157_FP.customer_lessons
    WHERE {col_selection} = '{col_val}'
    '''
    new_df = pd.read_sql(query, connection)
    st.dataframe(new_df)
else:
    if form_submit and len(col_val) == 0:
        form.write('input is blank!')
    st.dataframe(df)
