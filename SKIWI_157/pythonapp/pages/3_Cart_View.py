import streamlit as st
import pandas as pd
import pymysql

st.set_page_config(page_title="Skiwi", layout='wide')
st.header("SKIWI Enterprises Database")

# app.config['SECRET_KEY'] = 'mega_top_secret'

# db_config = {
#     'host': 'localhost',
#     'user': 'admin157',
#     'password': 'goodgradeplease',
#     'database': 'CS157_FP',
#     'cursorclass': pymysql.cursors.DictCursor
# }

connection = pymysql.connect(
    user='root', password='goodgradeplease', database='SKIWI_DB', host='mysql', port=3306,     cursorclass=pymysql.cursors.Cursor)

query = '''
            SELECT p.CART_ID, c.FIRST_NAME, c.LAST_NAME, p.TOTAL_COST
            FROM Customer AS c JOIN Cart as p
            ON c.CUSTOMER_ID = p.CUSTOMER_ID
    '''

df = pd.read_sql(query, connection)
df_cols = list(df.columns)

form = st.form("Search by Cart ID")
cartID = form.text_input(label="Cart ID")
form_submit = form.form_submit_button(label='submit')

if form_submit:
    query = f'''
    SELECT p.PURCHASABLE_ITEM_NAME, p.ITEM_COST, c.QUANTITY, (p.ITEM_COST * c.QUANTITY) AS FULL_COST
    FROM Cart_Details as c JOIN Purchasable_Items as p
    ON c.PURCHASING_ID = p.PURCHASING_ID
    WHERE c.CART_ID = '{cartID}'
    '''
    new_df = pd.read_sql(query, connection)
    if new_df.empty:
        st.write("No results found")
    else:
        st.dataframe(new_df)
else:
    st.dataframe(df)
