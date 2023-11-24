import streamlit as st
import pandas as pd
import pymysql

st.set_page_config(page_title="Skiwi", layout='wide')
st.header("SKIWI Enterprises Database")


connection = pymysql.connect(
    user='root', password='goodgradeplease', database='SKIWI_DB', host='mysql', port=3306,     cursorclass=pymysql.cursors.Cursor)

query = '''
SELECT
	b.BUNDLE_ID,
	b.BUNDLE_NAME,
	b.PURCHASABLE_ID,
	t.TICKET_ID,
	t.TICKET_NAME,
	ri.RENTAL_ID,
	ri.NAME AS "RENTAL_ITEM_NAME",
	l.LODGE_ID,
	l.LODGE_NAME,
	l2.LESSON_ID,
	l2.LESSON_NAME,
	TOTAL_COST
FROM
	Bundles b
JOIN
	Tickets t ON b.TICKET_ID = t.TICKET_ID
JOIN 
	Rental_Item ri ON b.RENTAL_ID = ri.RENTAL_ID
JOIN
	Lodges l ON b.LODGE_ID = l.LODGE_ID
JOIN 
	Lessons l2 ON b.LESSON_ID = l2.LESSON_ID
    '''

# try:
#     cursor.execute(query)
#     connection.commit()
# except:
#     st.write("Issues occurred creating the view")
#     connection.rollback()

# query = '''
#     SELECT * FROM Bundle_Details
#     '''

df = pd.read_sql(query, connection)
df_cols = list(df.columns)

form = st.form("Search by Column")
col_selection = form.selectbox('column filter', df_cols)
col_val = form.text_input(label="")
form_submit = form.form_submit_button(label='submit')


html = df.to_html
if form_submit and len(col_val) > 0:
    query = f'''
    SELECT * FROM CS157_FP.bundle_details
    WHERE {col_selection} = '{col_val}'
    '''
    new_df = pd.read_sql(query, connection)
    st.dataframe(new_df)
else:
    if form_submit and len(col_val) == 0:
        form.write('input is blank!')
    st.dataframe(df)
