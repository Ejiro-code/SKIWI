import streamlit as st
import pandas as pd
import pymysql

st.set_page_config(page_title="Skiwi", layout='wide')
st.header("SKIWI Enterprises Database")

st.title("Customer Invoice View")

connection = pymysql.connect(
    user='root', password='goodgradeplease', database='SKIWI_DB', host='mysql', port=3306,     cursorclass=pymysql.cursors.Cursor)

query = '''
            SELECT p.CUSTOMER_INVOICE_NUMBER, c.FIRST_NAME, c.LAST_NAME, p.TOTAL_COST, p.CUSTOMER_ORDER_DATE
            FROM Customer_Invoice as p JOIN Customer AS c 
            ON p.CUSTOMER_ID = c.CUSTOMER_ID
    '''

df = pd.read_sql(query, connection)
df_cols = list(df.columns)

form = st.form("Search by Invoice Number")
invoiceNumber = form.text_input(label="Invoice Number")
form_submit = form.form_submit_button(label='submit')

if form_submit:
    query = f'''
        SELECT p.PURCHASABLE_ITEM_NAME, p.ITEM_COST, c.QUANTITY, (p.ITEM_COST * c.QUANTITY) AS FULL_COST
        FROM Customer_Invoice_Details as c JOIN Purchasable_Items as p
        ON c.PURCHASABLE_ID = p.PURCHASABLE_ID
        WHERE c.CUSTOMER_INVOICE_NUMBER = '{invoiceNumber}'
    '''
    new_df = pd.read_sql(query, connection)
    if new_df.empty:
        st.write("No results found")
    else:
        st.dataframe(new_df)
else:
    st.dataframe(df)
