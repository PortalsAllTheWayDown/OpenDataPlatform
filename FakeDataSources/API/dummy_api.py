from flask import Flask, jsonify, request
import duckdb
import pandas as pd
from datetime import datetime as dt, timedelta
from faker import Faker
import random


CSV_FILE_PATH = "data/airbnb-listings.csv"

# Data scaling coefficients to make sure data generation
# is proportional to real Airbnb proportions: 
# REF: https://www.searchlogistics.com/learn/statistics/airbnb-statistics/#:~:text=There%20are%20currently%20over%205,booked%20over%201.5%20billion%20stays
BOOKING_SCALE = 1
CUSTOMER_SCALE = .1 # the number of customers is about a tenth of the number of bookings
HOST_SCALE = .0033
LISTING_SCALE = .0053



# initializes flask
app = Flask(__name__)

#initialize Faker
fake = Faker()

app.config["REQUEST_TIMESTAMP"] = dt.now() 

# prepare the data prior to fulfilling the request
@app.before_request
def initialize_database():

    # establish DB connection
    app.config['DB_CONNECTION'] = duckdb.connect('data/airbnb.duckdb')
    
    # set the volume scale to the default of Medium
    app.config['BASE_RECORD_SCALE'] = set_volume_scale()

    # save request time to session var
    app.config["REQUEST_TIMESTAMP"] = dt.now()

    # if the specified file in the connection above already exists, we won't load the CSV data again
    app.config['DB_CONNECTION'].execute(f"""
        CREATE TABLE IF NOT EXISTS listings AS 
        SELECT 
            *
            ,COALESCE("Last Scraped"||' 00:00:00', '{app.config["REQUEST_TIMESTAMP"].strftime("%Y-%m-%d %H:%M:%S")}') as last_modified_ts
        FROM read_csv('{CSV_FILE_PATH}', delim=';', header=true, ignore_errors=true)
    """)

    # create hosts table
    app.config['DB_CONNECTION'].execute(f"""
        CREATE TABLE IF NOT EXISTS hosts AS 
        SELECT 
            "Host ID"
            ,"Host URL"
            ,"Host Name"
            ,"Host Since"
            ,"Host Location"
            ,"Host About"
            ,"Host Response Time"
            ,"Host Response Rate"
            ,"Host Acceptance Rate"
            ,"Host Thumbnail Url"
            ,"Host Picture Url"
            ,"Host Neighbourhood"
            ,"Host Listings Count"
            ,"Host Total Listings Count"
            ,"Host Verifications"
            ,last_modified_ts
        FROM listings                              
    """)    

    # create customer table
    app.config['DB_CONNECTION'].execute(f"""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER,
            fname VARCHAR,
            lname VARCHAR,
            email VARCHAR,
            phone VARCHAR,
            rating FLOAT,
            billing_address_street VARCHAR,
            billing_address_city VARCHAR,
            billing_address_state VARCHAR,
            billing_address_country VARCHAR,
            billing_address_postal_code VARCHAR,
            account_create_ts TIMESTAMP,
            last_modified_ts TIMESTAMP
        )
    """)

    # create bookings table
    app.config['DB_CONNECTION'].execute(f"""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER,
            listing_id INTEGER,
            host_id INTEGER,
            primary_customer_id INTEGER,
            start_date DATE,
            end_date DATE,
            customer_rating FLOAT,
            host_rating FLOAT,
            last_modified_ts TIMESTAMP
        )
    """)

def set_volume_scale(size='M'):

    match size:

        # The base scale defines the number of records to generate for the 
        # bookings table per hour.
        case 'MIN':
            base_record_scale = 1
        case 'XS':
            base_record_scale = 10
        case 'S':
            base_record_scale = 1e2
        case 'M':
            base_record_scale = 1e3
        case 'L':
            base_record_scale = 1e4
        case 'XL':
            base_record_scale = 1e5
        case 'MAX':
            base_record_scale = 1e6
        case _: #default case 'M'
            base_record_scale = 1e3

    app.config['BASE_RECORD_SCALE'] = base_record_scale

def generate_data(low_watermark=app.config["REQUEST_TIMESTAMP"] - timedelta(hours=1), high_watermark=app.config["REQUEST_TIMESTAMP"]):
    """
    Stochastically generates data for each concept (Host, Customer, Listing, Booking). Volume is dependent on the 
    BASE_RECORD_SCALE config variable, and each concept's volume is scaled based on <concept>_SCALE. Data is 
    generated at the time of the request and scales based on the amount of time that's passed since the provided
    watermark value.

    Parameters:
    low_watermark (datetime): Grab data generated after this timestamp.
    high_watermark (datetime): Grab data generated before or on this timestamp.

    Returns:
    string: The JSON payload of the requested data, including pagination metadata

    Raises:
    TypeError: If the watermarks cannot be parsed into datetime values.
    """

    hours = high_watermark - low_watermark

    generate_customers()

def generate_customers():
    
    # Generate random number between .9 and 1.1 to acheive +/- 10% records
    variance = random.uniform(0.9, 1.1)

    num_records = app.config["BASE_RECORD_SCALE"] * CUSTOMER_SCALE * variance

    new_customers = {
        'id': [random.randint(10000000, 99999999) for _ in range(num_records)], # collisions are possible on the ID, but that's okay because they will be treated as updates
        'fname': [fake_or_none(fake.first_name, null_probability=.2) for _ in range(num_records)],
        'lname': [fake_or_none(fake.last_name, null_probability=.2) for _ in range(num_records)],
        'email': [fake_or_none(fake.email(), null_probability=.1) for _ in range(num_records)],
        'phone': [fake_or_none(fake.phone_number(), null_probability=.3) for _ in range(num_records)],
        #'rating': [fake_or_none(fake., null_probability=.3) for _ in range(num_records)],
    }



def generate_hosts():
    pass

def generate_bookings():
    pass

def generate_listings():
    pass

def fake_or_none(fake_func, null_probability=0.1):
    """
    Generate a fake value or None. Simulates NULLs in the database.

    Parameters:
    fake_func (callable): The Faker function to generate the value.
    null_probability (float): The probability of returning None. Default is 0.1 (10%).

    Returns:
    The generated fake value or None.
    """
    if random.random() < null_probability:
        return None
    return fake_func()

@app.teardown_appcontext
def close_session(context):

    if 'DB_CONNECTION' in app.config.keys() and app.config['DB_CONNECTION'] is not None:
        app.config['DB_CONNECTION'].close()


@app.route('/sample', methods=['GET'])
def sample():
    app.config['DB_CONNECTION'].execute("SELECT * FROM listings USING SAMPLE 5")
    return app.config['DB_CONNECTION'].fetch_df().to_json(orient='records')

if __name__ == '__main__':
    app.run()