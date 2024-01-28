import sqlite3 
import pandas as pd 
from datetime import datetime

#create database
conn = sqlite3.connect("flightdb")
curs = conn.cursor()

#creating tables
curs.execute("""CREATE TABLE IF NOT EXISTS Aircraft(aircraft_id INTEGER, 
                airline VARCHAR(50), capacity INTEGER, available INTEGER, PRIMARY KEY(aircraft_id));""") 

curs.execute("""CREATE TABLE IF NOT EXISTS Flight(flight_id INTEGER, 
             aircraft_id INTEGER, destination VARCHAR(50), departure_time TEXT, arrival_time TEXT, spaces_taken INTEGER,  
             PRIMARY KEY(flight_id), FOREIGN KEY(aircraft_id) REFERENCES Aircraft(aircraft_id));""")

curs.execute("""CREATE TABLE IF NOT EXISTS Pilot(pilot_id INTEGER, 
             firstname VARCHAR(30), surname VARCHAR(30), available INTEGER, PRIMARY KEY(pilot_id));""")

curs.execute("""CREATE TABLE IF NOT EXISTS Assignment(flight_id INTEGER, 
             pilot_id INTEGER, PRIMARY KEY(flight_id, pilot_id), FOREIGN KEY(flight_id) REFERENCES Flight(flight_id), 
             FOREIGN KEY(pilot_id) REFERENCES Pilot(pilot_id));""")

conn.commit()
conn.close()

#executes SQL statements on the database and returns the result
def executeSQL(sql):
    conn = sqlite3.connect("flightdb")
    curs = conn.cursor()
    result = curs.execute(sql).fetchall()
    conn.commit()
    conn.close()
    return result 

#check any user inputs into fields with the INT type are integers
def validate_integers(table, *attributes):
    field_info = executeSQL(f"PRAGMA table_info({table})")
    fields = [field[1] for field in field_info]
    data_types = [field[2] for field in field_info]
    integer_fields = [fields[i] for i in range(len(data_types)) if data_types[i] == 'INTEGER']
  
    #keep asking the user for values until they are integers for the appropriate attributes
    valid_values = []
    for i in range(len(attributes)):
        valid = validate_integer(attributes[i])
        if valid == True:
            valid_values.append(attributes[i])
        else:
            while not valid:
                attempt = input("Invalid data type for " + integer_fields[i] + " - should be INTEGER. Please try again: ")
                valid = validate_integer(attempt)
            valid_values.append(attempt)
        
    return valid_values 

#checks whether a user input is an integer or not
def validate_integer(value):
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False

#checks whether user inputs a date and time in the correct format
def validate_date_time(given_datetime):
    try:
        date_time = datetime.strptime(given_datetime, "%Y-%m-%d %H:%M:%S")
        date_time_formatted = date_time.strftime("%Y-%m-%d %H:%M:%S")
        return date_time_formatted
    except ValueError:
        return False 

#inserting data into a given table in our database
def insert():
    tables = ["Aircraft", "Flight", "Pilot", "Assignment"]
    table = input("Which table would you like to insert records into? ")
    
    #check if the given table exists
    if table in tables:
        sql = """INSERT INTO """ + table + """ VALUES """
        if table == "Aircraft":
            #allow the user to insert however many records they wish to
            insert_another = "y"
            while insert_another == "y":
                #get the relevant attribute values from the user
                id = input("What is the ID of the aircraft? ")
                airline = input("Which airline does this aircraft belong to? ")
                capacity = input("What is the maximum capacity of this aircraft? ")
                available = input("Is this aircraft currently available? 0/1 ")
                valid_values = validate_integers("Aircraft", id, capacity, available)
                valid_id, valid_capacity, valid_available = valid_values 
                sql += "('" + valid_id + "','" + airline + "','" + valid_capacity + "','" + valid_available + "')"
                insert_another = input("Do you want to add another aircraft? y/n ")
                if insert_another == "y":
                    sql += ","
                else:
                    sql += ";"
            executeSQL(sql)
        #the following is the same functionality but for the rest of the tables
        elif table == "Flight":
            insert_another = "y"
            while insert_another == "y":
                flight_id = input("What is the ID of the flight? ")
                aircraft_id = input("What is the ID of the aircraft? ")
                destination = input("Where is this flight going? ")
                departure = input("When does this flight depart (YYYY-MM-DD HH:MM:SS)? ")
                arrival = input("When does this flight arrive (YYYY-MM-DD HH:MM:SS)? ")

                valid_departure = validate_date_time(departure)
                valid_arrival = validate_date_time(arrival)

                while valid_departure == False:
                    departure = input("Incorrect departure format. Please try again (YYYY-MM-DD HH:MM:SS): ")
                    valid_departure = validate_date_time(departure)

                while valid_arrival == False:
                    arrival = input("Incorrect arrival format. Please try again (YYYY-MM-DD HH:MM:SS): ")
                    valid_arrival = validate_date_time(departure)
                
                valid_values = validate_integers("Flight", flight_id, aircraft_id)
                valid_flight, valid_aircraft = valid_values

                #check whether the aircraft_id attribute exists in the corresponding Aircraft table
                aircraft_exists = check_value_exists("Aircraft", "aircraft_id", valid_aircraft)
                while not aircraft_exists:
                    valid_aircraft = input("Invalid aircraft ID - please try again: ")
                    aircraft_exists = check_value_exists("Aircraft", "aircraft_id", valid_aircraft)

                sql += "('" + valid_flight + "','" + valid_aircraft + "','" + destination + "','" + departure + "','" + arrival + "','" + str(0) + "')"

                insert_another = input("Do you want to add another flight? y/n ")
                if insert_another == "y":
                    sql += ","
                else:
                    sql += ";"
            executeSQL(sql)
        elif table == "Pilot":
            insert_another = "y"
            while insert_another == "y":
                id = input("What is the ID of the pilot? ")
                firstname = input("What is the pilot's first name? ")
                surname = input("What is the pilot's surname? ")
                available = input("Is the pilot currently available? 0/1 ")

                valid_values = validate_integers("Pilot", id, available)
                valid_id, valid_available = valid_values
                sql += "('" + valid_id + "','" + firstname + "','" + surname + "','" + valid_available + "')"
                insert_another = input("Do you want to add another aircraft? y/n ")
                if insert_another == "y":
                    sql += ","
                else:
                    sql += ";"
            executeSQL(sql)
        else:
            #make sure the given IDs exist in their corresponding tables to ensure data is consistent 
            #before adding them to the table
            insert_another = "y"
            while insert_another == "y":
                flight_id = input("What is the ID of the flight? ")
                pilot_id = input("What is the ID of the pilot? ")
                flight_exists = check_value_exists("Flight", "flight_id", flight_id)
                pilot_exists = check_value_exists("Pilot", "pilot_id", pilot_id)

                valid_values = validate_integers("Assignment", flight_id, pilot_id)
                valid_flight, valid_pilot = valid_values

                while not flight_exists and not pilot_exists:
                    if not flight_exists and not pilot_exists:
                        print("Both the flight and pilot ID is invalid - please try again.")
                        flight_id = input("What is the ID of the flight? ")
                        pilot_id = input("What is the ID of the pilot? ")
                        flight_exists = check_value_exists("Flight", "flight_id", flight_id)
                        pilot_exists = check_value_exists("Pilot", "pilot_id", pilot_id)
                    elif not flight_exists:
                        flight_id = input("Invalid flight - please try again: ")
                        flight_exists = check_value_exists("Flight", "flight_id", flight_id)
                    else:
                        pilot_id = input("Invalid pilot - please try again: ")
                        pilot_exists = check_value_exists("Pilot", "pilot_id", pilot_id)
                    
                sql += "('" + valid_flight + "','" + valid_pilot + "')"
                insert_another = input("Do you want to add another assignment? y/n ")
                if insert_another == "y":
                    sql += ","
                else:
                    sql += ";"
            executeSQL(sql)
        print("Data has been added successfully to the " + table + " table!")
    else:
        print("Table not found - please try again.")
        insert()
        

#checks whether a given value exists in the corresponding table
def check_value_exists(table, attribute, value):
    conn = sqlite3.connect("flightdb")
    curs = conn.cursor()
    sql = """SELECT """ + attribute + " FROM " + table + " WHERE " + attribute + " = " + value + ";"
    record = curs.execute(sql).fetchone()
    conn.commit()
    conn.close()

    if record:
        return True
    else:
        return False
    
#checks whether a given field is a foreign key
def check_if_foreign_key(attribute):
    foreign_keys = ["aircraft_id", "flight_id", "pilot_id"]
    if attribute in foreign_keys:
        return True
    else:
        return False

#updates records in a given table
def update():
    sql = """UPDATE """
    tables = ["Aircraft", "Flight", "Pilot", "Assignment"]
    table = input("Which table would you like to update? ")

    #check the given table exists in the database
    while table not in tables:
        table = input("Table does not exist - please try again: ")
    sql += table + " SET "
    
    #asks the user for as many attributes as they wish to change
    update_another = "y"
    while update_another == "y":
        #displays all the fields in the given table and checks the given attribute exists in the table
        field_info = executeSQL(f"PRAGMA table_info({table})")
        fields = [field[1] for field in field_info]
        print(fields)
        attribute = input("Which attribute would you like to update? ")
        while attribute not in fields:
            attribute = input("Attribute does not exist - please try again: ")
        sql += attribute

        #get user input and validate any integer and datetime attributes
        integer_fields = ["aircraft_id", "capacity", "available", "flight_id", "pilot_id", "spaces_taken"]
        datetime_fields = ["departure_time", "arrival_time"]
        value = input("What would you like to change the value of " + attribute + " to? ")

        if attribute in integer_fields:
            valid = validate_integer(value)
            while not valid:
                value = input("Invalid data type for " + attribute + " - should be INTEGER. Please try again: ")
                valid = validate_integer(value)
        elif attribute in datetime_fields:
            valid = validate_date_time(value)
            while not valid:
                value = input("Invalid data type for " + attribute + " - should be DATETIME. Please try again: ")
                valid = validate_date_time(value)

        #if the given attribute is a foreign key, check its corresponding primary key exists before updating
        is_foreign_key = check_if_foreign_key(attribute)
        if is_foreign_key:
            foreign_key_value_exists = False 
            while not foreign_key_value_exists:
                if table == "Flight":
                    if check_value_exists("Aircraft", "aircraft_id", value):
                        sql += " = '" + value + "' "
                        foreign_key_value_exists = True
                    else:
                        value = input("Aircraft does not exist - please try again: ")
                elif table == "Assignment":
                    if attribute == "flight_id" and not check_value_exists("Flight", "flight_id", value):
                        value = input("This flight does not exist - please try again: ")
                    elif attribute == "pilot_id" and not check_value_exists("Pilot", "pilot_id", value):
                        value = input("This pilot does not exist - please try again: ")
                    else:
                        sql += " = '" + value + "' "
                        foreign_key_value_exists = True
        else:
            sql += " = '" + value + "' "
        
        #if the value is a foreign key in another table, update that value also
        if attribute == "aircraft_id" and table == "Aircraft":
            aircrafts = executeSQL("""SELECT aircraft_id FROM Aircraft WHERE """ + condition + ";")
            for aircraft in aircrafts:
                executeSQL("""UPDATE Flight SET aircraft_id = '""" + value + "' WHERE aircraft_id = '" + aircraft + "';")
        elif attribute == "flight_id" and table == "Flight":
            flights = executeSQL("""SELECT flight_id FROM Flight WHERE """ + condition + ";")
            for flight in flights:
                executeSQL("""UPDATE Assignment SET flight_id = '""" + value + "' WHERE flight_id = '" + flight + "';")
        elif attribute == "pilot_id" and table == "Pilot":
            pilots = executeSQL("""SELECT pilot_id FROM Pilot WHERE """ + condition + ";")
            for pilot in pilots:
                executeSQL("""UPDATE Assignment SET pilot_id = '""" + value + "' WHERE pilot_id = '" + pilot + "';")

        update_another = input("Would you like to update another attribute from this table? y/n ")
        if update_another == "y":
            sql += "AND "
        
    condition = input("Which records would you like to update? ")
    sql += "WHERE " + condition + ";"
    executeSQL(sql)
    print("Data has been successfully updated in the " + table + " table!")

#search for specific records using attributes and display the retrieved data
def search():
    sql = """SELECT """
    #check the given table exists
    tables = ["Aircraft", "Flight", "Pilot", "Assignment"]
    table = input("Which table would you like to search from? ")
    while table not in tables:
        table = input("Table does not exist - please try again: ")
    
    #ask the user for as many attributes as they want to search for 
    #and check the given attributes exist in the given table
    field_info = executeSQL(f"PRAGMA table_info({table})")
    valid_attributes = [field[1] for field in field_info]
    print(valid_attributes)

    another_attribute = "y"
    while another_attribute == "y":
        attribute = input("Which attribute would you like to search for? ")
        while attribute not in valid_attributes:
            attribute = input("This attribute does not exist in the " + table + " table - please try again: ")
        sql += attribute

        another_attribute = input("Would you like to search for another attribute? y/n ")
        if another_attribute == "y":
            sql += ","
        else:
            sql += " FROM " + table + " WHERE "

    #apply as many conditions to the search as the user wishes to
    another_condition = "y"
    while another_condition == "y":
        condition = input("Which condition would you like to apply? ")
        sql += condition 
        another_condition = input("Would you like to apply another condition? y/n ")
        if another_condition == "y":
            sql += " AND "
        
    sql += ";"
    #present the retrieved data in a tabular format using pandas
    conn = sqlite3.connect("flightdb")
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    print(df.to_string(index=False))
    conn.commit()
    conn.close()
    
#deletes specific records from a given table
def delete():
    sql = """DELETE FROM """
    #check the given table exists 
    tables = ["Aircraft", "Flight", "Pilot", "Assignment"]
    table = input("Which table would you like to delete from? ")
    while table not in tables:
        table = input("Table does not exist - please try again: ")
    sql += table + " WHERE "

    #filter using as many conditions as the user wishes to
    another_condition = "y"
    while another_condition == "y":
        condition = input("Which condition would you like to apply? ")
        sql += condition
        another_condition = input("Would you like to apply another condition? y/n ")
        if another_condition == "y":
            sql += " AND "
        else:
            sql += ";"

    executeSQL(sql)
    print("Data has been successfully deleted from the " + table + " table!\n")

    #show remaining data after deletion
    conn = sqlite3.connect("flightdb")
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    print(df.to_string(index=False))
    conn.commit()
    conn.close()
    
#display a given table in the database
def view():
    sql = """SELECT * FROM """
    tables = ["Aircraft", "Flight", "Pilot", "Assignment"]
    table = input("Which table would you like to view? ")
    while table not in tables:
        table = input("Table does not exist - please try again: ")
    sql += table 
    print("\n")
    
    #present the data in a tabular format using pandas
    conn = sqlite3.connect("flightdb")
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    print(df.to_string(index=False))
    conn.commit()
    conn.close()

#summary statistic functions

#number of flights in a specific week
def flights_per_week():
     conn = sqlite3.connect("flightdb")
     curs = conn.cursor()

     year = int(input("Which year are you interested in? "))
     week_number = int(input("Which week are you interested in? "))
     departure_sql = """SELECT departure_time
              FROM Flight 
              WHERE strftime('%Y', departure_time) = ? 
              AND strftime('%W', departure_time) = ?"""
     
     curs.execute(departure_sql, (str(year), str(week_number)))
     dates = curs.fetchall()
     num_flights = len(dates)
     conn.commit()
     conn.close()

     if num_flights != 1:
        print(f"There are {num_flights} flights within week {week_number} of {year}!")
     else:
        print(f"There is 1 flight within week {week_number} of {year}!")

#number of flights to a specific destination per month
def flights_to_destination():
    conn = sqlite3.connect("flightdb")
    curs = conn.cursor()

    destination = input("Which destination are you interested in? ")
    year = int(input("Which year are you interested in? "))
    month = int(input("Which month are you interested in? "))

    sql = """SELECT flight_id 
             FROM Flight 
             WHERE strftime('%Y', departure_time) = ? 
             AND strftime('%m', departure_time) = ?
             AND destination = ?"""
    curs.execute(sql, (str(year), str(month).zfill(2), destination))
    flights = curs.fetchall()
    num_flights = len(flights)
    conn.commit()
    conn.close()

    if num_flights != 1:
        print(f"There are {num_flights} flights to {destination} in month {month} of {year}!")
    else:
        print(f"There is 1 flight to {destination} in month {month} of {year}!")

#allow the user to make a booking onto a flight as long as there is enough space left on the flight
def make_booking():
    """I was not able to finish this extra function so it does not work 
    but I have left the code in for an idea of what it was supposed to do"""

    num_people = int(input("How many people would you like to make a booking for? "))
    flight_id = int(input("What is the ID of the flight you would like to make a booking for? "))

    spaces_sql = f"""SELECT spaces_taken FROM Flight WHERE flight_id = '{str(flight_id)}';"""
    aircraft_sql = f"""SELECT aircraft_id FROM Flight WHERE flight_id = '{str(flight_id)}';"""
    spaces_taken = executeSQL(spaces_sql)
    aircraft_id = executeSQL(aircraft_sql)
    capacity_sql = f"""SELECT capacity FROM Aircraft WHERE aircraft_id = '{str(aircraft_id)}';"""
    capacity = executeSQL(capacity_sql)

    spaces_left = capacity - spaces_taken
    if num_people > spaces_left:
        print("Sorry. Not enough spaces left on this flight to make the booking.")
    elif num_people == spaces_left:
        executeSQL(f"""UPDATE Flight SET spaces_taken = '{str(capacity)}' WHERE flight_id = '{str(flight_id)}';""")
        print("Booking successful! This flight is now fully booked.")
    else:
        executeSQL(f"""UPDATE Flight SET spaces_taken = '{str(spaces_taken + num_people)}' WHERE flight_id = '{str(flight_id)}';""")
        print(f"Booking successful! There are {str(spaces_left - num_people)} spaces left on this flight.")


# main program

print("Welcome to FlightsDB. What would you like to do today?\n ")
options = "1. Insert\n2. Update\n3. Search\n4. Delete\n5. View table\n6. Calculate number of flights in a week\n7. Calculate flights to a specific destination in a month\n8. Make a booking"

carry_on = "y"
while carry_on == "y":
    print(options)
    choice = int(input(""))
    while choice not in range(1,9):
        choice = int(input("Invalid choice. Please try again: "))

    if choice == 1:
        insert()
    elif choice == 2:
        update()
    elif choice == 3:
        search()
    elif choice == 4:
        delete()
    elif choice == 5:
        view()
    elif choice == 6:
        flights_per_week()
    elif choice == 7:
        flights_to_destination()
    else:
        make_booking()

    carry_on = input("\nWould you like to carry out another operation? y/n ")

print("Thank you for using FlightsDB - see you next time!")

