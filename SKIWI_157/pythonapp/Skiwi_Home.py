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

cursor = connection.cursor()

option = st.selectbox(
    'What table would you like to view?',
    ('Customer', 'Purchasable_Items', 'Ski_Conditions', 'Cart', 'Cart_Details', 'Tickets', 'Rental_Item',
     'Lodges', 'Lodge_Amenities', 'Lessons', 'Bundles', 'Customer_Invoice', 'Customer_Invoice_Details')
)

st.write('You selected:', option)

# st.sidebar()

df = pd.read_sql(f'SELECT * FROM {option}', connection)
df_cols = list(df.columns)

form = st.form("Search by Column")
col_selection = form.selectbox('column filter', df_cols)
col_val = form.text_input(label="")
form_submit = form.form_submit_button(label='submit')

if form_submit and len(col_val) > 0:
    query = f'''
    SELECT * FROM {option}
    WHERE {col_selection} = '{col_val}'
    '''
    new_df = pd.read_sql(query, connection)
    st.dataframe(new_df)

else:
    if form_submit and len(col_val) == 0:
        form.write('input is blank!')
    st.dataframe(df)


val_deletion = st.button(label="Delete")

if val_deletion and len(col_val) > 0:
    query = f'''
            DELETE FROM {option} 
            WHERE {col_selection} = '{col_val}' 
        '''
    try:
        cursor.execute(query)
        connection.commit()
    except:
        connection.rollback()

    st.write('Matching rows have been deleted from database')
else:
    st.write('Can only delete filtered data which requires input be "submitted" ')


cursor.close()
connection.close()
