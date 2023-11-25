import streamlit as st
import math
from datetime import datetime
import pandas as pd
import pymysql
import decimal
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


connection = pymysql.connect(
    user='root', password='goodgradeplease', database='SKIWI_DB', host='mysql', port=3306,     cursorclass=pymysql.cursors.Cursor)

cursor = connection.cursor()

option = st.selectbox(
    'Where would you like to insert the record?',
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

# df = pd.read_sql(f'SELECT * FROM {option} LIMIT 1', connection)
# df_cols = list(df.columns)

my_dict = {}


for i, val in enumerate(df_cols):
    my_dict[df_cols[i]] = st.text_input(
        label=f"Enter {val}", key=f'col{i}')

submit = st.button('Insert')

if submit:
    finished = True
    for i, (k, user_val) in enumerate(my_dict.items()):
        # st.write(f'SUCCESS FOR {k} with {user_val}')
        if k.endswith('_COST') or k.endswith('PRICE') or k == 'LANE_ALTITUDE' or k == 'NIGHTLY_RATES' or k == 'DISCOUNT_PERCENTAGE':
            if convert_float(my_dict, k, user_val):
                my_dict[k] = round(float(user_val), 2)
            else:
                st.write("Invalid numeric input for float conversion")
                finished = False
                break

        if k == 'CREDIT_CARD_NUMBER' or k == 'CREDIT_CARD_SECURITY_CODE' or k == 'AGE' or k == 'TEMPERATURE' or k == 'WIND_SPEEDS' or k == 'QUANTITY' or k == 'SIZE' or k == 'OPEN':
            if convert_int(my_dict, k, user_val):
                my_dict[k] = int(user_val)
            else:
                st.write("Invalid numeric input for integer conversion")
                finished = False
                break

        if option == 'Bundles' or option == 'Customer' and k.endswith('_ID'):
            if k != 'BUNDLE_ID' and k != 'PURCHASABLE_ID' and k != 'CUSTOMER_ID' and len(user_val) == 0:
                my_dict[k] = None
                finished = True
                continue
            elif len(user_val) == 0:
                st.write("Issues with BUNDLE_ID or PURCHASABLE_ID or LESSON_ID")
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
                st.write('Inappropriate DATE Format. Expecting YYYY-MM-DD')
                finished = False
            # else:
            #     my_dict[k] = datetime.strptime(user_val, '%Y-%m-%d').date()
            #     st.write(my_dict[k])

        elif (k.endswith('_ID') or k.endswith('_NUMBER')) and len(user_val) == 0:
            st.write('Inappropriate ID value. Should be have 10 characters exactly')
            finished = False
        elif user_val == '':
            st.write(f'Value cannot be Null... Error on column {k}')
            finished = False
        else:
            continue

    if finished:
        # print(my_dict)
        columns = ', '.join(my_dict.keys())
        string_vals = ", ".join(['%s'] * len(my_dict))
        query = f'''
        INSERT INTO {option}
        ({columns})
        VALUES({string_vals})
        '''

        try:
            # st.write(my_dict.values())
            # st.write("Made into insertion?")
            cursor.execute(query, tuple(my_dict.values()))
            connection.commit()
            st.write("Record Inserted into table Successfully!")
        except:
            st.write(
                "An error occurred.. likely due to an unobserved foreign constraint")
            connection.rollback()


connection.close()
cursor.close()

# if k.endswith('_COST') or k.endswith('PRICE') or k == 'LANE_ALTITUDE' or k == 'NIGHTLY_RATES' or k == 'DISCOUNT_PERCENTAGE':
#     if convert_float(my_dict, k, user_val):
#         my_dict[k] = round(float(user_val), 2)
#     else:
#         st.write("Invalid numeric input for float conversion")
#         finished = False
#         break

# if k == 'CREDIT_CARD_NUMBER' or k == 'CREDIT_CARD_SECURITY_CODE' or k == 'AGE' or k == 'TEMPERATURE' or k == 'WIND_SPEEDS' or k == 'QUANTITY' or k == 'SIZE' or k == 'OPEN':
#     if convert_int(my_dict, k, user_val):
#         my_dict[k] = int(user_val)
#     else:
#         st.write("Invalid numeric input for integer conversion")
#         finished = False
#         break

# if option == 'Bundles' or option == 'Costumer' and k.endswith('_ID'):
#     if k != 'BUNDLE_ID' and k != 'PURCHASABLE_ID' and k != 'CUSTOMER_ID' and len(user_val) == 0:
#         finished = True
#         continue
#     elif len(user_val) == 0:
#         st.write("Issues with BUNDLE_ID or PURCHASABLE_ID or LESSON_ID")
#         finished = False

# elif k == 'CREDIT_CARD_NUMBER':
#     if my_dict[k] != 16:
#         st.write('Credit card number is invalid')
#         finished = False

# elif k == 'CREDIT_CARD_SECURITY_CODE':
#     if my_dict[k] != 3:
#         st.write('Credit card security code number is invalid')
#         finished = False

# elif k == 'AGE':
#     if 0 > my_dict[k] or my_dict[k] > 200:
#         st.write('Invalid age range. Must be between 0 and 200')
#         finished = False

# elif (k.endswith('_COST') or k.endswith('PRICE') or k == 'LANE_ALTITUDE' or k == 'NIGHTLY_RATES'):
#     if 0.00 > my_dict[k] or my_dict[k] > 9999.99:
#         st.write(
#             'Invalid COST, PRICE, LANE_ALTITUDE or NIGHTLY_RATES range. Must be between 0 and 9999.99')
#         finished = False

# elif k == 'DISCOUNT_PERCENTAGE':
#     if my_dict[k] < 0 or my_dict[k] > 100:
#         st.write(
#             'Inappropriate percentage count. Must be between 0 and 100')
#         finished = False

# elif k == 'TEMPERATURE':
#     if my_dict[k] < -100 or my_dict[k] > 150:
#         st.write(
#             'Inappropriate temperature measurement. Must be between -100 and 150')
#         finished = False

# elif k == 'WIND_SPEEDS':
#     if my_dict[k] < 0 or my_dict[k] > 100:
#         st.write(
#             'Inappropriate wind speed measurement. Must be between 0 and 100')
#         finished = False

# elif k == 'OPEN':
#     if my_dict[k] < 0 or my_dict[k] > 1:
#         st.write(
#             'Inappropriate Open value. Must be between 0 (closed) or 1(open)')
#         finished = False

# # elif k == 'QUANTITY' or k.endswith('SIZE'):
# #     if not user_val.isnumeric():
# #         st.write('Inappropriate QUANTITY or SIZE value. Must be a number')
# #         finished = False
# elif k == 'DAY' or k.endswith('_DATE'):
#     match = re.match(regex, user_val)
#     if not match:
#         st.write('Inappropriate DATE Format. Expecting YYYY-MM-DD')
#         finished = False
#     else:
#         my_dict[k] = datetime.strptime(user_val, '%Y-%m-%d').date()
#         st.write(my_dict[k])

# elif (k.endswith('_ID') or k.endswith('_NUMBER')) and len(user_val) == 0:
#     st.write('Inappropriate ID value. Should be have 10 characters exactly')
#     finished = False
# else:
#     continue
