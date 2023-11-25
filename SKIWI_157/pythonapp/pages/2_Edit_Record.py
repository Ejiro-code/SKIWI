import streamlit as st
import math
import pandas as pd
import pymysql
import re

regex = re.compile("[0-9]{4}\-[0-9]{2}\-[0-9]{2}")

st.set_page_config(page_title="Skiwi Record Insertions", layout='wide')
st.header("SKIWI Enterprises Database")


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def convert_int(my_dict, k, string):
    try:
        my_dict[k] = int(string)
        return True
    except ValueError:
        return False


def convert_float(my_dict, k, string):
    try:
        my_dict[k] = round(float(string), 2)
        return True
    except ValueError:
        return False


st.title('Update Records')

connection = pymysql.connect(
    user='root', password='goodgradeplease', database='SKIWI_DB', host='mysql', port=3306,     cursorclass=pymysql.cursors.Cursor)


cursor = connection.cursor()

option = st.selectbox(
    'Insert the primary key(s) of the record you would like to update?',
    ('Customer', 'Purchasable_Items', 'Ski_Conditions', 'Cart', 'Cart_Details', 'Tickets', 'Rental_Item',
     'Lodges', 'Lodge_Amenities', 'Lessons', 'Bundles', 'Customer_Invoice', 'Customer_Invoice_Details')
)

query = f"SHOW COLUMNS FROM {option}"

# Execute the query
cursor.execute(query)

# Fetch all the results as a list of tuples
column_names_tuples = cursor.fetchall()

# Extract column names from the list of tuples and store them in a list
df_cols = [column[0] for column in column_names_tuples]

# Store primary keys belonging to tables
pk1 = ""
pk2 = ""
enter_pk2 = False

# Check for relations with multiple primary keys vs those with a single key
if option == "Ski_Conditions" or option == "Cart_Details" or option == "Lodge_Amenities" or option == "Customer_Invoice_Details":
    pk1 = st.text_input(label=df_cols[0])
    pk2 = st.text_input(label=df_cols[1])
    enter_pk2 = True
else:
    pk1 = st.text_input(label=df_cols[0])

if "Search" not in st.session_state:
    st.session_state["Search"] = False

if "Update" not in st.session_state:
    st.session_state["Update"] = False


# search = st.button('Search')


if st.button("Search"):
    st.session_state["Search"] = not st.session_state["Search"]


if st.session_state["Search"]:
    # Save corresponding record if it exists
    my_dict = {}
    if enter_pk2:
        df = pd.read_sql(
            f"SELECT * FROM {option} WHERE {df_cols[0]} = '{pk1}' AND {df_cols[1]} = '{pk2}'", connection)
    else:
        df = pd.read_sql(
            f"SELECT * FROM {option} WHERE {df_cols[0]} = '{pk1}'", connection)
    df_cols = list(df.columns)

    if df.empty:
        st.write("Didn't find any corresponding rows")
    else:
        for i, val in enumerate(df_cols):
            if (enter_pk2 and i < 2) or i < 1:
                continue

            my_dict[df_cols[i]] = st.text_input(
                label=f"Enter {val}", value=df[df_cols[i]].iloc[0], key=f'col{i}')
        if st.button("Update"):
            finished = True
            for i, (k, user_val) in enumerate(my_dict.items()):
                # st.write(f'SUCCESS FOR {k} with {user_val}')
                if k.endswith('_COST') or k.endswith('PRICE') or k == 'LANE_ALTITUDE' or k == 'NIGHTLY_RATES' or k == 'DISCOUNT_PERCENTAGE' or k == 'TEMPERATURE' or k == 'WIND_SPEEDS':
                    if convert_float(my_dict, k, user_val):
                        my_dict[k] = round(float(user_val), 2)
                    else:
                        st.write(
                            f"Invalid numeric input for float conversion on {k}")
                        finished = False
                        break

                if k == 'CREDIT_CARD_NUMBER' or k == 'CREDIT_CARD_SECURITY_CODE' or k == 'AGE' or k == 'QUANTITY' or k == 'SIZE' or k == 'OPEN':
                    if convert_int(my_dict, k, user_val):
                        my_dict[k] = int(user_val)
                    else:
                        st.write(
                            f"Invalid numeric input for integer conversion on {k}")
                        finished = False
                        break

                if option == 'Bundles' or option == 'Customer' and k.endswith('_ID'):
                    if k != 'BUNDLE_ID' and k != 'PURCHASABLE_ID' and k != 'CUSTOMER_ID' and (user_val == None or len(user_val) == 0):
                        my_dict[k] = None
                        finished = True
                        continue
                    elif len(user_val) == 0:
                        st.write(
                            "Issues with BUNDLE_ID or PURCHASABLE_ID or LESSON_ID")
                        finished = False

                elif k == 'CREDIT_CARD_NUMBER':
                    if int(math.log10(my_dict[k]))+1 != 16:
                        st.write('Credit card number is invalid')
                        finished = False

                elif k == 'CREDIT_CARD_SECURITY_CODE':
                    if int(math.log10(my_dict[k]))+1 != 3:
                        st.write('Credit card security code number is invalid')
                        finished = False

                elif k == 'AGE':
                    if 0 > my_dict[k] or my_dict[k] > 200:
                        st.write('Invalid age range. Must be between 0 and 200')
                        finished = False

                elif (k.endswith('_COST') or k.endswith('PRICE') or k == 'LANE_ALTITUDE' or k == 'NIGHTLY_RATES'):
                    if 0.00 > my_dict[k] or my_dict[k] > 9999.99:
                        st.write(
                            'Invalid COST, PRICE, LANE_ALTITUDE or NIGHTLY_RATES range. Must be between 0 and 9999.99')
                        finished = False

                elif k == 'DISCOUNT_PERCENTAGE':
                    if my_dict[k] < 0 or my_dict[k] > 100:
                        st.write(
                            'Inappropriate percentage count. Must be between 0 and 100')
                        finished = False

                elif k == 'TEMPERATURE':
                    if my_dict[k] < -100 or my_dict[k] > 150:
                        st.write(
                            'Inappropriate temperature measurement. Must be between -100 and 150')
                        finished = False

                elif k == 'WIND_SPEEDS':
                    if my_dict[k] < 0 or my_dict[k] > 100:
                        st.write(
                            'Inappropriate wind speed measurement. Must be between 0 and 100')
                        finished = False

                elif k == 'OPEN':
                    if my_dict[k] < 0 or my_dict[k] > 1:
                        st.write(
                            'Inappropriate Open value. Must be between 0 (closed) or 1(open)')
                        finished = False

                # elif k == 'QUANTITY' or k.endswith('SIZE'):
                #     if not user_val.isnumeric():
                #         st.write('Inappropriate QUANTITY or SIZE value. Must be a number')
                #         finished = False
                elif k == 'DAY' or k.endswith('_DATE'):
                    match = re.match(regex, user_val)
                    if not match:
                        st.write(
                            'Inappropriate DATE Format. Expecting YYYY-MM-DD')
                        finished = False
                    # else:
                    #     my_dict[k] = datetime.strptime(user_val, '%Y-%m-%d').date()
                    #     st.write(my_dict[k])

                elif (k.endswith('_ID') or k.endswith('_NUMBER')) and len(user_val) == 0:
                    st.write(k)
                    st.write(
                        'Inappropriate ID value. Should be have 10 characters exactly')
                    finished = False
                elif user_val == '':
                    st.write(f'Value cannot be Null... Error on column {k}')
                else:
                    continue

            if finished:
                string_vals = ", ".join(
                    [f"{key} = %s" for key in my_dict.keys()])
                # Check for relations with multiple primary keys vs those with a single key
                if option == "Ski_Conditions" or option == "Cart_Details" or option == "Lodge_Amenities" or option == "Customer_Invoice_Details":
                    part2 = f"WHERE {df_cols[0]} = '{df[df_cols[0]].iloc[0]}' AND {df_cols[1]} = '{df[df_cols[1]].iloc[0]}'"
                else:
                    part2 = f"WHERE {df_cols[0]} = '{df[df_cols[0]].iloc[0]}'"

                query = f'''
                UPDATE {option}
                SET {string_vals}
                {part2}
                '''

                # st.write(query)
                try:
                    cursor.execute(query, tuple(my_dict.values()))
                    connection.commit()
                    st.write("Record Updated into table Successfully!")
                except:
                    st.write("Issues occurred updating the record")
                    connection.rollback()
            st.session_state["Update"] = not st.session_state["Update"]
