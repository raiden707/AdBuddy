from datetime import datetime
from logging import log
from sqlite3 import Error
from sqlite3.dbapi2 import Cursor
from map import get_coords
from pprint import pprint

import sqlite3
import bcrypt
import crypto
import random
import time
import json
"""
/Users/raiden/Dropbox/Final Project/App/adbuddy
"""

#db_file = r"D:/Documents/Dropbox/Dropbox/Final Project/App/adbuddy/adbuddy.db"

db_file = "/Users/raiden/Dropbox/Final Project/App/adbuddy/adbuddy.db"


def create_connection(db_file):
    """
    Establishes a connection with the SQLite DB
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(e)

    return conn


connection = create_connection(db_file)


def pull_id(username):
    """
    (string) - > string or Bool
    1. Take username
    2. Pull UID from user table
    """
    sql_statement = "SELECT UID from users where username = ?"
    cursor = connection.cursor()
    rows = cursor.execute(sql_statement, [username]).fetchone()

    if rows != None:
        UID = rows[0]
        return UID
    else:
        return False


def initialize_setup_status(username):
    """
    (string) -> NoneType
    This method adds false to the setup status upon user sign up

    1. Pull UID
    2. Add False to status table upon signup

    """
    UID = str(pull_id(username))

    sql_statement = "INSERT INTO status VALUES (?,?)"
    cursor = connection.cursor()

    try:
        cursor.execute(sql_statement, [UID, "False"])
        connection.commit()

    except Error as e:
        return(e)


def signup(username, password):
    '''
    (string,string) -> NoneType
    Append new user to users table
    1. Hash password
    2. Perform SQL Insert transaction for both values into users
    3. Upon succesfull sign up, redirect to the login page
    TODO: 

    '''

    hashed_password = crypto.encrypt(password)

    sql_statement = "INSERT into users (UID, username, password) VALUES (?,?,?)"
    cursor = connection.cursor()

    try:
        cursor.execute(sql_statement, [random.randint(
            1000, 9999), username, hashed_password])
        connection.commit()
        initialize_setup_status(username)

    except Error as e:
        return(e)


def check_user(username):
    '''
    (string) -> string or Bool
    input: email, password
    output: True if user exists

    1. Check if username exists
    '''
    sql_statement = "SELECT * FROM users WHERE username = ?"
    cursor = connection.cursor()

    rows = cursor.execute(sql_statement, [username]).fetchone()

    if rows != None:
        return rows[1] == username
    else:
        return False


def signup_flow(username, password):
    '''
    (string, string) -> Bool
    Initiates Sign Up flow
    1. Check if user exists
    2. If not, invoke the signup function
    '''

    if check_user(username) == True:
        print("Username already exists")
        return False
    else:
        signup(username, password)
        print(datetime.now(), " - User created with username:", username)
        print("User has been created!")
        return True


def login_flow(username, password):
    """
    (string, string) -> Bool

    1. Pull up hashed password in DB
    2. Compare it with clients password

    """
    stored_password = None
    if check_user(username) == True:
        sql_statement = "SELECT * FROM users WHERE username = ?"
        cursor = connection.cursor()
        rows = cursor.execute(sql_statement, [username]).fetchone()
        stored_password = rows[2]
        if password != None:
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                # print("Match")  debugging, remove before submission
                return True
            else:
                # debugging, remove before submission
                #print("It Does Not Match")
                return False
    else:
        return "User does not exist"

print(login_flow("duckpile","badpassword"))

def check_setup_status(username):
    """
    (string) -> Bool
    This method checks if a user has finished setup

    1. Get ID from username
    2. Access the status table
    """
    UID = pull_id(username)

    sql_statement = "SELECT setup_status from status where UID = ?"
    cursor = connection.cursor()

    rows = cursor.execute(sql_statement, [UID]).fetchone()
    if rows is not None:
        setup_status = rows[0]
        return setup_status


def update_setup_status(username):
    """
    This method updates the False value to True upon completing the setup process
    1. Update Flase for given UID to True
    """
    return None


def insert_business(username, business_name, URL):
    """
    (string,string,string) -> Bool
    1. Check to see if anything is there with the UID
    2. If not, commit
    3. If yes, return error "Business name and URL already entered"
    """
    UID = pull_id(username)
    conn = connection

    preflight_sql = "SELECT * from business WHERE UID = ?"
    cursor = conn.cursor()
    rows = cursor.execute(preflight_sql, [UID]).fetchone()

    if rows == None:
        sql_statement = "INSERT INTO business (UID,business_name, URL) VALUES (?, ?, ?) "
        cursor = conn.cursor()
        try:
            cursor.execute(sql_statement, [UID, business_name, URL])
            conn.commit()
            print("Business has been added with this User ID")
            return True
        except Error as e:
            return(e)
    else:
        print("Business Already exists with current User ID")
        return False


def generate_campaign_id():
    """
    (NoneType) -> str
    Generates new campaign and adds it to the campaign table
    Note: Campaign ID is randomly generated here

    example campaign ID: 10009812

    1000 + 4 digits as a string

    1. Pull UID from current session
    2. Pull campaign_name and cityfrom form data (this needs to be a table)
    3. Check if campaign ID exists
    4. If not, append to table. Otherwise make new one and check that
    """
    id_cap = random.randint(1000, 9999)
    campaign_id = '1000' + str(id_cap)

    sql_statement = "SELECT campaign_id from campaign"
    cursor = connection.cursor()
    rows = cursor.execute(sql_statement).fetchone()
    if rows != campaign_id:
        id_cap = random.randint(1000, 9999)
        new_campaign_id = '1000' + str(id_cap)
        return new_campaign_id


def generate_campaign_row(UID, location):
    """
    (int,str) -> Bool
    1. Generate Lat, Long from location name
    2. Parses str into list, then adds list items using a for loop for given UID

    """
    campaign_id = generate_campaign_id()

    location_dictionary = {"UID": "", "campaign_id": "",
                           "city": "", "lattitude": "", "longitude": ""}

    geodata = get_coords(location)

    location_dictionary["UID"] = UID
    location_dictionary["campaign_id"] = campaign_id
    location_dictionary["city"] = geodata[0]
    location_dictionary["lattitude"] = geodata[1]
    location_dictionary["longitude"] = geodata[2]

    return location_dictionary


def insert_campaign_row(location_row):
    """
    (dict) -> Bool

    Insert one row of full location data for a campaign
    """
    UID = location_row['UID']
    campaign_id = location_row['campaign_id']
    city = location_row['city']
    lattitude = location_row['lattitude']
    longitude = location_row['longitude']

    sql_statement = "INSERT INTO campaign (UID,campaign_id,city,lattitude,longitude) values (?,?,?,?,?)"
    conn = connection
    cursor = conn.cursor()
    try:
        cursor.execute(sql_statement, [
                       UID, campaign_id, city, lattitude, longitude])
        conn.commit()
        print("Campaign has been added with id:", campaign_id)
        return True
    except Error as e:
        return(e)


def multiple_campaigns(UID, raw_locations):
    """
    (str,str) -> Bool
    """
    #"loc1, loc2, loc3"

    location_list = raw_locations.split(", ")
    True_count = 0
    for place in location_list:

        row = (generate_campaign_row(UID, place))
        if (insert_campaign_row(row)) == True:
            True_count += 1

    if True_count == len(location_list):

        return True
    else:
        return False


def insert_product(UID, product):
    """
    (str,str) -> Bool

    Insert one product for a given UID
    """
    sql_statement = "INSERT INTO product (UID,product) values (?,?)"
    conn = connection
    cursor = conn.cursor()
    try:
        cursor.execute(sql_statement, [UID, product])
        conn.commit()
        print("Product with name", product, "been added", "for user ID:", UID)
    except Error as e:
        return(e)


def product_controller(UID, raw_products):
    """
    (str,str) -> NoneType
    """
    True_count = 0
    product_list = raw_products.split(",")
    for product in product_list:
        True_count += 1
        insert_product(UID, product.strip())

    if True_count == len(product_list):
        return True
    else:
        return False


def get_markers(username):
    """
    duckpile UID = 6350
    (str) -> list
    TODO:
    Need to make a dict out of each row
    """
    location_list = []
    UID = pull_id(username)
    sql_statement = "SELECT city, lattitude, longitude FROM campaign WHERE UID = ?"
    cursor = connection.cursor()
    location_list = cursor.execute(sql_statement, [UID]).fetchall()

    return location_list


def campaign_num(username):
    """
    (str) -> int

    Returns the number of campaigns for a given username 
    """
    UID = pull_id(username)
    sql_statement = "SELECT COUNT(*) FROM campaign WHERE UID = ?"
    cursor = connection.cursor()
    city_count = cursor.execute(sql_statement, [UID]).fetchone()
    return city_count[0]


def campaign_retrieval(username):
    """
    TODO
    1. make a dict ready for json parsing
    2. Pull info from campaign table
    """

    markers = {
        "city": "", "lattitude": "", "longitude": ""}

    
    jsonStr = json.dumps(markers)
    return jsonStr



