import threading
import socket
import sqlite3
import os



#Connect to other servers and get responses
def SendRequest(command,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", port))
    sock.send(b'GET '+command.encode()+b' HTTP/1.1\r\nHost:localhost:'+str(port).encode()+b'\r\n\r\n')
    response = sock.recv(4096)
    sock.close()
    Splitted_Response=response.decode().split("\r\n\r\n")
    error_part=Splitted_Response[0].split(" ")
    ResponseMassage=[]
    ResponseMassage.append(error_part[1])
    ResponseMassage.append(Splitted_Response)
    return ResponseMassage
#find reservation id
def find_reservation_id(reservation_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Reservation WHERE reservation_id=?", (reservation_id,))
    data=cursor.fetchone()
    conn.close()
    return data
#Update reservation id
def reservation_update_activity(room,activityname,day,hour,duration):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE Reservation SET activity_name=? WHERE room_name=? AND day=? And hour=? AND duration=?", (activityname,room,day,hour,duration))
    conn.commit()
    conn.close()
#Update reservation id
def reseervation_update_reservationid(room,day,hour,duration,reservationid):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE Reservation SET reservation_id=? WHERE room_name=? AND day=? And hour=? AND duration=?",
                   (reservationid, room, day, hour, duration))
    conn.commit()
    conn.close()
#find max reservation id
def find_max_reservationid():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(reservation_id) FROM Reservation WHERE reservation_id IS NOT NULL")
    max_reservation_id = cursor.fetchone()
    if max_reservation_id is None:
        return None
    else:
        return max_reservation_id[0]
#remove Activitiy and Update reservation table activities
def remove_activity(data):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Activity WHERE name=?", (data,))
    cursor.execute("UPDATE Reservation SET activity_name=NULL WHERE activity_name=?", (data,))
    conn.commit()
    conn.close()

# add activity
def add_Activity(data):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Activity (name) VALUES (?)", (data,))
    #cursor.execute(f"INSERT INTO Rooms (name) VALUES ({data})")
    conn.commit()
    conn.close()
# Check availability of a day.
def CheckAvailability(roomname,day):
    starthour=9
    hourtemp=9
    endhour=17
    allhours=[]
    avaiable_hours=[]
    not_available=[]
    #append all hours
    while(hourtemp<endhour+1):
        allhours.append(hourtemp)
        hourtemp+=1

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    #retrieve data from reservation table
    cursor.execute(
        "SELECT * FROM Reservation WHERE room_name=? AND day=?",
        (roomname,day))
    results=cursor.fetchall()
    conn.close()
    for result in results:
        temp=result[4]
        startinghour=result[3]
        while(temp>0):
            not_available.append(startinghour)
            startinghour+=1
            temp-=1
    for i in allhours:
        if (i not in not_available):
            avaiable_hours.append(i)
        else:
            pass
    return avaiable_hours
#check reservation according to day hour and durations
def reservation_add_check(name, day, hour, duration):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    total=int(hour)+int(duration)
    hour=int(hour)
    duration=int(duration)
    # Check if the hour and duration overlap with any existing reservations
    cursor.execute("SELECT * FROM Reservation WHERE room_name=? AND day=? AND ((hour>? And hour<?) OR (hour<=? AND hour+duration>?))",(name, day, hour, total,hour, hour))
    overlaps = cursor.fetchall()

    if overlaps:
        # Return False if the hour and duration overlap with any existing reservations
        conn.close()
        return False
    else:
        # Insert the new reservation if there are no overlaps
        cursor.execute("INSERT INTO Reservation (room_name, day, hour, duration) VALUES (?, ?, ?, ?)", (name, day, hour, duration))
        conn.commit()
        conn.close()
        return True

#Check if there is no reservation for the given day
def reservation_check(Room, day):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Reservation WHERE room_name=? AND day=?", (Room, day))
    results = cursor.fetchall()
    conn.close()
    if results:
        # Return the list of results if there are any
        return results
    else:
        # Return an empty list if there are no results
        return []

# Add reservation to the database
def reservation_add(name, day, hour, duration):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Reservation (room_name, day, hour, duration) VALUES (?, ?, ?, ?)", (name, day, hour, duration))
    conn.commit()
    conn.close()

#Printing the table
def show_database(database):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {database}")
    results = cursor.fetchall()
    print(results)
    conn.close()
# Removing room from database
def remove_room(data):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Rooms WHERE name=?", (data,))
    cursor.execute("DELETE FROM Reservation WHERE room_name=?", (data,))
    # cursor.execute(f"INSERT INTO Rooms (name) VALUES ({data})")
    conn.commit()
    conn.close()
# add room to the database
def add_room(data):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Rooms (name) VALUES (?)", (data,))
    #cursor.execute(f"INSERT INTO Rooms (name) VALUES ({data})")

    conn.commit()
    conn.close()

#Check if the given value exists in the database or not
def data_search(database_name,Searched_data):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {database_name} WHERE name=?", (Searched_data,))
    result = cursor.fetchone()
    if (result==None):
        result=0
    else:
        result=1

    conn.close()
    return result

#Rooom server
def RoomServer():

    print("room server")
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a specific IP and port
    s.bind(('localhost', 8080))
    # Set the socket to listen for incoming connections
    s.listen(5)

    days_of_week = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}

    while True:
        # Accept incoming connections
        connS, addr = s.accept()

        # Receive the HTTP request
        request = connS.recv(1024)

        #Split operations
        request_lines = request.split(b'\r\n')
        request_line = request_lines[0]
        request_line = request_line.decode('utf-8')
        method, path, version = request_line.split(' ')
        #If method Name is get enter here
        if method == 'GET':
            #Counter for day hour and durations
            IsDayValid = 0
            IsHourValid = 0
            IsDurationValid = 0
            #split operations
            Operation, AllVariables = path.split('?')
            Variables = AllVariables.split('&')
            #Appending to the dictionary
            dictionary = {}
            for i in Variables:
                temp = i.split("=")
                dictionary[temp[0]] = temp[1]
            # Add operation /add enter here
            if Operation == '/add':
                #IF variable name is not valid enter here
                if ("name" not in dictionary):
                    # name değişkeninin adı doğru girilmediyse
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>Wrong variable name</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY> Wrong variable name</BODY></HTML>'
                    connS.send(response)
                    #IF varible name id valid enter here
                else:
                    #remove blank spaceses
                    dictionary["name"] = dictionary["name"].replace("%0A", "")
                    #check if data data is exists
                    result = data_search("Rooms", dictionary["name"])
                    #if exists send 403
                    if (result == 1):
                        response = b'HTTP/1.1 403 Forbidden\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Could not add room</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary[
                            "name"].encode() + b' already exists in database</BODY></HTML>'
                        connS.send(response)
                    #if not exists add to the database and send 200 Ok
                    else:
                        add_room(dictionary["name"])
                        response = b'HTTP/1.1 200 OK\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Room successfully added</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary["name"].encode() + b' added</BODY></HTML>'
                        connS.send(response)


            #If operationis  /remove enter here
            elif Operation == '/remove':
                #If variable name is wrong send 400
                if ("name" not in dictionary):
                    # name değişkeninin adı doğru girilmediyse
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>Wrong variable name</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY>Wrong variable name</BODY></HTML>'
                    connS.send(response)
                # IF variable name is valid

                else:
                    # Remove blank spaceses
                    dictionary["name"] = dictionary["name"].replace("%0A", "")
                    # Check if data is exists
                    result = data_search("Rooms", dictionary["name"])
                    #If exists remove the room and send 200 ok
                    if (result == 1):
                        remove_room(dictionary["name"])
                        response = b'HTTP/1.1 200 OK\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Room removed</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary[
                            "name"].encode() + b' successfully removed</BODY></HTML>'
                        connS.send(response)
                    #If not exists send 403
                    else:

                        response = b'HTTP/1.1 403 Forbidden\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Could not remove room</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>There is no room named ' + dictionary["name"].encode() + b'</BODY></HTML>'
                        connS.send(response)

            #If operation name is /reserve enter here
            elif Operation == '/reserve':
                #check variable names
                if (("name" not in dictionary) or ("day" not in dictionary) or ("hour" not in dictionary) or (
                        "duration" not in dictionary)):
                    response = b'HTTP/1.1 400 Bad Request bas\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>Wrong variable names</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY>Wrong variable names</body></HTML>'
                    connS.send(response)
                #If variable names are valid enter here
                else:
                    # Check If day is valid
                    if (int(dictionary["day"]) < 1 or int(dictionary["day"]) > 7):
                        IsDayValid = 1
                        response = b'HTTP/1.1 400 Bad Request day\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Wrong variable names</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>Day ' + dictionary[
                            "day"].encode() + b' is not valid. Should be between 1 and 7</BODY></HTML>'
                        connS.send(response)
                        connS.close()
                    # Check If hour is valid
                    if ((int(dictionary["hour"]) > 17 or int(dictionary["hour"]) < 9) and IsDayValid == 0):
                        IsHourValid = 1
                        response = b'HTTP/1.1 400 Bad Request hour\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Wrong variable names</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>Hour ' + dictionary[
                            "hour"].encode() + b' is not valid. Should be between 9 and 17</BODY></HTML>'
                        connS.send(response)
                        connS.close()
                    # Check If hour is valid
                    if ((int(dictionary["hour"]) + int(
                            dictionary["duration"]) > 18) and IsDayValid == 0 and IsHourValid == 0):
                        IsDurationValid = 1
                        response = b'HTTP/1.1 400 Bad Request duration\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Wrong variable names</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>Duration ' + dictionary[
                            "duration"].encode() + b' is not valid. The sum of duration and hour should not be more than 18</BODY></HTML>'
                        connS.send(response)
                        connS.close()
                    # If all are valid enter here
                    if (IsDayValid == 0 and IsHourValid == 0 and IsDurationValid == 0):
                        #check if room name exists or not
                        if (data_search("Rooms", dictionary["name"]) == 0):
                            response = b'HTTP/1.1 404 Not Found\r\n\r\n'
                            response += b'<HTML>\n'
                            response += b'<HEAD>\n'
                            response += b'<TITLE>Reservation could not be made</TITLE>\n'
                            response += b'</HEAD>\n'
                            response += b'<BODY>' + dictionary[
                                "name"].encode() + b' room not exists</BODY></HTML>'
                            connS.send(response)

                        #If exists enter here
                        else:
                            ReservationData = reservation_check(dictionary["name"], dictionary["day"])
                            #If there is no reservation for that day enter here and add reservation
                            if (len(ReservationData) == 0):

                                reservation_add(dictionary["name"], dictionary["day"], dictionary["hour"],
                                                dictionary["duration"])
                                maxid = find_max_reservationid()
                                # max id not exists update as a 1
                                if (maxid == None):
                                    reseervation_update_reservationid(dictionary["name"], dictionary["day"],
                                                                      dictionary["hour"], dictionary["duration"], 1)
                                # else update as max id + 1
                                else:
                                    reseervation_update_reservationid(dictionary["name"], dictionary["day"],
                                                                      dictionary["hour"], dictionary["duration"],
                                                                      maxid + 1)
                                endtime = (int(dictionary["hour"]) + int(dictionary["duration"]))
                                response = b'HTTP/1.1 200 OK\r\n\r\n'
                                response += b'<HTML>\n'
                                response += b'<HEAD>\n'
                                response += b'<TITLE>Reservation made successfully</TITLE>\n'
                                response += b'</HEAD>\n'
                                response += b'<BODY>' + dictionary["name"].encode() + b' ' + days_of_week[
                                    int(dictionary["day"])].encode() + b' ' + dictionary["hour"].encode() + b'-' + str(
                                    endtime).encode() + b' reserved</BODY></HTML>'
                                connS.send(response)

                            # If there is a reservation for that day enter here
                            else:

                                #check reservation hours are valid or not.IF valid append to the database
                                ReservedOrNot = reservation_add_check(dictionary["name"], dictionary["day"],
                                                                      dictionary["hour"], dictionary["duration"])
                                #IF valid return true send 200 ok
                                if (ReservedOrNot == True):
                                    # eklendi
                                    maxid = find_max_reservationid()
                                    # max id not exists update as a 1
                                    if (maxid == None):
                                        reseervation_update_reservationid(dictionary["name"], dictionary["day"],
                                                                          dictionary["hour"], dictionary["duration"], 1)
                                    # else update as max id + 1
                                    else:
                                        reseervation_update_reservationid(dictionary["name"], dictionary["day"],
                                                                          dictionary["hour"], dictionary["duration"],
                                                                          maxid + 1)
                                    endtime = (int(dictionary["hour"]) + int(dictionary["duration"]))
                                    response = b'HTTP/1.1 200 OK\r\n\r\n'
                                    response += b'<HTML>\n'
                                    response += b'<HEAD>\n'
                                    response += b'<TITLE>Reservation made successfully</TITLE>\n'
                                    response += b'</HEAD>\n'
                                    response += b'<BODY>' + dictionary["name"].encode() + b' ' + days_of_week[
                                        int(dictionary["day"])].encode() + b' ' + dictionary[
                                                    "hour"].encode() + b'-' + str(
                                        endtime).encode() + b' reserved</BODY></HTML>'
                                    connS.send(response)
                                #If already reserved then send 403
                                else:
                                    response = b'HTTP/1.1 403 Forbidden\r\n\r\n'
                                    response += b'<HTML>\n'
                                    response += b'<HEAD>\n'
                                    response += b'<TITLE>Reservation could not be made</TITLE>\n'
                                    response += b'</HEAD>\n'
                                    response += b'<BODY>' + dictionary[
                                        "name"].encode() + b' already reserved</BODY></HTML>'
                                    connS.send(response)
            #if operation is /checkavailablity enter here
            elif Operation == '/checkavailability':
                #check variable names
                if (("name" not in dictionary) or ("day" not in dictionary)):
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>Check availability</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY>Wrong variable name</BODY></HTML>'
                    connS.send(response)
                else:
                    #check if day is valid
                    if (int(dictionary["day"]) < 1 or int(dictionary["day"]) > 7):
                        IsDayValid = 1
                        response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Check availability</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>Day ' + dictionary[
                            "day"].encode() + b' not valid. Should be between 1 and 7</BODY></HTML>'
                        connS.send(response)
                        connS.close()

                    if (IsDayValid == 0):
                        #check data exists or not
                        if (data_search("Rooms", dictionary["name"]) == 1):
                            # check room is exists
                            available_hours = CheckAvailability(dictionary["name"], dictionary["day"])
                            # If there is no available hour enter here
                            if (len(available_hours) == 0):
                                response = b'HTTP/1.1 200 OK\r\n\r\n'
                                response += b'<HTML>\n'
                                response += b'<HEAD>\n'
                                response += b'<TITLE>Check availability</TITLE>\n'
                                response += b'</HEAD>\n'
                                response += b'<BODY>' + days_of_week[int(
                                    dictionary["day"])].encode() + b' Available Hours: no available hour</BODY></HTML>'
                                connS.send(response)
                            # else enter here and send the response
                            else:
                                available_hours_str = ', '.join(str(hour) for hour in available_hours)
                                response = b'HTTP/1.1 200 OK\r\n\r\n'
                                response += b'<HTML>\n'
                                response += b'<HEAD>\n'
                                response += b'<TITLE>Check availability</TITLE>\n'
                                response += b'</HEAD>\n'
                                response += b'<BODY>' + days_of_week[int(dictionary[
                                                                                   "day"])].encode() + b' Available Hours: ' + available_hours_str.encode() + b'</BODY></HTML>'
                                connS.send(response)
                        #if data is not in the database send 404
                        else:
                            response = b'HTTP/1.1 404 Not Found\r\n\r\n'
                            response += b'<HTML>\n'
                            response += b'<HEAD>\n'
                            response += b'<TITLE>Check availability</TITLE>\n'
                            response += b'</HEAD>\n'
                            response += b'<BODY>' + dictionary["name"].encode() + b' not exists</BODY></HTML>'
                            connS.send(response)
            #If the operation is not valid send 400
            else:
                response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                response += b'<HTML>\n'
                response += b'<HEAD>\n'
                response += b'<TITLE>NOT Valid Operation</TITLE>\n'
                response += b'</HEAD>\n'
                response += b'<BODY>Operation ' + Operation.encode() + b' is not valid.</BODY></HTML>'
                connS.send(response)


            print("room server database datas")
            show_database("Rooms")
            show_database("Activity")
            show_database("Reservation")
            connS.close()


#activity server
def ActivityServer():
    print("activity server")
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a specific IP and port
    s.bind(('localhost', 8081))
    # Set the socket to listen for incoming connections
    s.listen(5)

    while True:
        # Accept incoming connections
        connS, addr = s.accept()
        # Receive the HTTP request
        request = connS.recv(1024)
        #split operations
        request_lines = request.split(b'\r\n')
        request_line = request_lines[0]
        request_line = request_line.decode('utf-8')
        method, path, version = request_line.split(' ')
        #if method is get enter here
        if method == 'GET':
            #split operations
            Operation, AllVariables = path.split('?')
            Variables = AllVariables.split('&')
            #append to the dictionary
            dictionary = {}
            for i in Variables:
                temp = i.split("=")
                dictionary[temp[0]] = temp[1]
            #If operation is /add enter here
            if Operation == '/add':
                #check variable name is valid
                if ("name" not in dictionary):
                    # name değişkeninin adı doğru girilmediyse
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>Add activity operation</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY>Wrong variable name</BODY></HTML>'
                    connS.send(response)
                else:
                    #remove blank spaces
                    dictionary["name"] = dictionary["name"].replace("%0A", "")
                    #Check data exists or not
                    result = data_search("Activity", dictionary["name"])
                    #If exists enther here and send 403 already existed
                    if (result == 1):
                        response = b'HTTP/1.1 403 Forbidden\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Could not add activity</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary[
                            "name"].encode() + b' already exists in database</BODY></HTML>'
                        connS.send(response)
                    #If not add activity to the database and send 200 ok
                    else:

                        add_Activity(dictionary["name"])
                        response = b'HTTP/1.1 200 OK\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Activity successfully added</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary["name"].encode() + b' added</BODY></HTML>'
                        connS.send(response)

            #If operation is remove enter here
            elif Operation == '/remove':
                if ("name" not in dictionary):
                    # Check variable name
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>Activity server remove operation</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY>Wrong variable name</BODY></HTML>'
                    connS.send(response)

                else:
                    #remove blank spaces
                    dictionary["name"] = dictionary["name"].replace("%0A", "")
                    #check If data exists or not
                    result = data_search("Activity", dictionary["name"])
                    #if exists enter here remove activitiy and send 200 ok
                    if (result == 1):

                        remove_activity(dictionary["name"])
                        response = b'HTTP/1.1 200 OK\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Activity succesfully removed</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary[
                            "name"].encode() + b' successfully removed</BODY></HTML>'
                        connS.send(response)
                    #If not exists send 403
                    else:

                        response = b'HTTP/1.1 403 Forbidden\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Activity could not be removed</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary["name"].encode() + b' not exists</BODY></HTML>'
                        connS.send(response)
            #If operation is /check
            elif Operation == '/check':
                # If variable name is valid
                if ("name" not in dictionary):
                    # name değişkeninin adı doğru girilmediyse
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>Activity check</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY>Wrong variable name</BODY></HTML>'
                    connS.send(response)
                else:
                    #remove blank spaces
                    dictionary["name"] = dictionary["name"].replace("%0A", "")
                    #Check if data exists
                    result = data_search("Activity", dictionary["name"])
                    #IF exists send 200 ok
                    if (result == 1):
                        response = b'HTTP/1.1 200 OK\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Activity exists</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary["name"].encode() + b' activity exists</BODY></HTML>'
                        connS.send(response)

                    #If not exists send 404
                    else:
                        response = b'HTTP/1.1 404 Not Found\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>No activity found</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary[
                            "name"].encode() + b' activity not exists</BODY></HTML>'
                        connS.send(response)

            #If operation name is not valid send 400
            else:
                response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                response += b'<HTML>\n'
                response += b'<HEAD>\n'
                response += b'<TITLE>Operation name is wrong</TITLE>\n'
                response += b'</HEAD>\n'
                response += b'<BODY>Operation ' + Operation.encode() + b' is not valid.</BODY></HTML>'
                connS.send(response)

            print("activity server database datas")
            show_database("Rooms")
            show_database("Activity")
            show_database("Reservation")
            connS.close()

#Reservation server
def ReservationServer():
    print("reservation server")
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a specific IP and port
    s.bind(('0.0.0.0', 8082))
    # Set the socket to listen for incoming connections
    s.listen(5)

    days_of_week = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}

    while True:
        # Accept incoming connections
        connS, addr = s.accept()
        # Receive the HTTP request
        request = connS.recv(1024)
        # split operations
        request_lines = request.split(b'\r\n')
        request_line = request_lines[0]
        request_line= request_line.decode('utf-8')
        method, path, version = request_line.split(' ')
        # If method is get enter here
        if method == 'GET':

            Operation, AllVariables = path.split('?')
            Variables = AllVariables.split('&')
            #append to the dictionary
            dictionary = {}
            for i in Variables:
                temp = i.split("=")
                dictionary[temp[0]] = temp[1]

            #If operation name is reserve enter here
            if Operation == '/reserve':
                #check variable names
                if (("room" not in dictionary) or ("activity" not in dictionary) or ("day" not in dictionary) or ("hour" not in dictionary) or (
                        "duration" not in dictionary)):
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>Reservation server</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY>Wrong variable name</BODY></HTML>'
                    connS.send(response)

                else:
                    #Connect to the activity server
                    StatusCode=SendRequest("/check?name="+dictionary["activity"],8081)
                    #If Activity server response is 404 enter here
                    if(StatusCode[0]=="404"):
                        response = b'HTTP/1.1 404 Not Found\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>No activity found</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>' + dictionary["activity"].encode() + b' does not exist</BODY></HTML>'
                        connS.send(response)
                    #If activity exists enter here
                    else:
                        #connect to the room server
                        RoomsServerStatusCode = SendRequest("/reserve?name="+dictionary["room"]+"&day="+dictionary["day"]+"&hour="+dictionary["hour"]+"&duration="+dictionary["duration"], 8080)

                        #If received status code is 400 enter here
                        if(RoomsServerStatusCode[0]=="400"):
                            response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                            response += b'<HTML>\n'
                            response += b'<HEAD>\n'
                            response += b'<TITLE>Wrong variable or variable name</TITLE>\n'
                            response += b'</HEAD>\n'
                            response += b'<BODY>Invalid variable name or values</BODY></HTML>'
                            connS.send(response)
                        # If received status code is 403 enter here
                        elif(RoomsServerStatusCode[0]=="403"):
                            response = b'HTTP/1.1 403 Forbidden\r\n\r\n'
                            response += b'<HTML>\n'
                            response += b'<HEAD>\n'
                            response += b'<TITLE>Room is already reserved</TITLE>\n'
                            response += b'</HEAD>\n'
                            response += b'<BODY>' + dictionary["room"].encode() + b' not available</BODY></HTML>'
                            connS.send(response)
                        # If received status code is 200 enter here
                        elif (RoomsServerStatusCode[0] == "200"):
                            #Update reservation activity and reservation id
                            reservation_update_activity(dictionary["room"],dictionary["activity"],dictionary["day"],dictionary["hour"],dictionary["duration"])


                            response = b'HTTP/1.1 200 OK\r\n\r\n'
                            response += b'<HTML>\n'
                            response += b'<HEAD>\n'
                            response += b'<TITLE>Room successfully reserved</TITLE>\n'
                            response += b'</HEAD>\n'
                            response += b'<BODY>' + dictionary[
                                "room"].encode() + b' reservation successfully added</BODY></HTML>'
                            connS.send(response)

                        else:
                            print("yanlış statu döndü")

            #If the operation is /listavailability enter here
            elif Operation== '/listavailability':
                #if the len of dict is 2 enter
                if(len(dictionary)==2):
                    #check variable names
                    if (("room" not in dictionary) or ("day" not in dictionary)):
                        response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Wrong variable name</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>Wrong variable name</BODY></HTML>'
                        connS.send(response)

                    else:
                        #connect to the room server
                        availabilitymessage=SendRequest("/checkavailability?name="+dictionary["room"]+"&day="+dictionary["day"],8080)
                        #If the response is 200 enter here
                        if(availabilitymessage[0]=="200"):
                            #split operations
                            AllMessage=str(availabilitymessage[1]).split(":")
                            Hourdata=str(AllMessage[1]).split("<")
                            #If there is no available hour
                            if(Hourdata[0]==" no available hour"):
                                response = b'HTTP/1.1 200 OK\r\n\r\n'
                                response += b'<HTML>\n'
                                response += b'<HEAD>\n'
                                response += b'<TITLE>No available hour found</TITLE>\n'
                                response += b'</HEAD>\n'
                                response += b'<BODY>'+dictionary["room"].encode()+b' '+days_of_week[int(dictionary["day"])].encode()+b' '+b'no available hour</BODY></HTML>'
                                connS.send(response)

                            #if there is available hour
                            else:
                                response = b'HTTP/1.1 200 OK\r\n\r\n'
                                response += b'<HTML>\n'
                                response += b'<HEAD>\n'
                                response += b'<TITLE>Available hours</TITLE>\n'
                                response += b'</HEAD>\n'
                                response += b'<BODY>' + dictionary["room"].encode() + b' ' + days_of_week[
                                    int(dictionary["day"])].encode()+b' available hours' + Hourdata[0].encode()+b'</BODY></HTML>'
                                connS.send(response)


                        #IF room could not found
                        elif (availabilitymessage[0] == "404"):
                            response = b'HTTP/1.1 404 Not Found\r\n\r\n'
                            response += b'<HTML>\n'
                            response += b'<HEAD>\n'
                            response += b'<TITLE>Room does not exist</TITLE>\n'
                            response += b'</HEAD>\n'
                            response += b'<BODY>' + dictionary["room"].encode() + b' does not exist</BODY></HTML>'
                            connS.send(response)
                        #IF invalid or wrong variable name typed
                        elif (availabilitymessage[0] == "400"):

                            response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                            response += b'<HTML>\n'
                            response += b'<HEAD>\n'
                            response += b'<TITLE>Wrong variable name or invalid variables</TITLE>\n'
                            response += b'</HEAD>\n'
                            response += b'<BODY>Wrong variable name</BODY></HTML>'
                            connS.send(response)

                        #For other status codes
                        else:
                            print("yanlıs girdin")

                # For the second method list availability
                elif(len(dictionary)==1):
                    #check if variable name is valid or not
                    if (("room" not in dictionary)):
                        response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Wrong variable name</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<html><body>Wrong variable name</body></html>'
                        connS.send(response)
                    #if valid enter here

                    else:
                        counter=0
                        tempresponse=b''
                        #Sending request for all days
                        while(counter<7):
                            counter+=1
                            temprequest=SendRequest("/checkavailability?name=" + dictionary["room"] + "&day="+str(counter), 8080)
                            #if room not found
                            if (temprequest[0] == "404"):
                                response = b'HTTP/1.1 404 Not Found\r\n\r\n'
                                response += b'<HTML>\n'
                                response += b'<HEAD>\n'
                                response += b'<TITLE>Room does not exist</TITLE>\n'
                                response += b'</HEAD>\n'
                                response += b'<BODY>' + dictionary[
                                    "room"].encode() + b' does not exist</BODY></HTML>'
                                connS.send(response)
                                break
                            #If invalid variable name and etc.
                            elif (temprequest[0] == "400"):
                                response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                                response += b'<HTML>\n'
                                response += b'<HEAD>\n'
                                response += b'<TITLE>Wrong variable name</TITLE>\n'
                                response += b'</HEAD>\n'
                                response += b'<BODY>Wrong variable name</BODY></HTML>'
                                connS.send(response)
                                break
                            #if everthing is fine enter here
                            elif (temprequest[0] == "200"):
                                #split operations
                                AllMessage = str(temprequest[1]).split(":")
                                Hourdata = str(AllMessage[1]).split("<")
                                #design html file according to if elses
                                if(counter==1):
                                    if (Hourdata[0] == " no available hour"):
                                        tempresponse += b'<HTML><BODY>' + dictionary["room"].encode() + b' ' + days_of_week[counter].encode() + b' ' + b'no available hour<BR>\n'

                                    else:
                                        tempresponse +=b'<HTML><BODY>' + dictionary["room"].encode() + b' ' + days_of_week[counter].encode()+b' available hours' + Hourdata[0].encode()+b'<BR>\n'
                                else:
                                    if (Hourdata[0] == " no available hour"):
                                        tempresponse += dictionary["room"].encode() + b' ' + days_of_week[
                                            counter].encode() + b' ' + b'no available hour<BR>\n'

                                    else:
                                        tempresponse +=dictionary["room"].encode() + b' ' + days_of_week[
                                            counter].encode() + b' available hours' + Hourdata[0].encode() + b'<BR>\n'
                            else:
                                print("satatus code yanlış girdi")
                                print(temprequest)
                        #sending response
                        if(tempresponse!=b''):
                            response = b'HTTP/1.1 200 OK\r\n\r\n'
                            response += b'<HTML>\n'
                            response += b'<HEAD>\n'
                            response += b'<TITLE>Available hours for week</TITLE>\n'
                            response += b'</HEAD>\n'
                            response += tempresponse
                            response += b'</BODY></HTML>'
                            connS.send(response)

                #wrong variable
                else:
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>List availability operation</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY>Wrong variable name</BODY></HTML>'
                    connS.send(response)

            #If operation is display
            elif Operation == '/display':
                #check variable name
                if (("id" not in dictionary)):
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    response += b'<HTML>\n'
                    response += b'<HEAD>\n'
                    response += b'<TITLE>Wrong variable name</TITLE>\n'
                    response += b'</HEAD>\n'
                    response += b'<BODY>Wrong variable name</BODY></HTML>'
                    connS.send(response)

                else:
                    #find reservation id
                    result=find_reservation_id(dictionary["id"])
                    #if none
                    if(result==None):
                        response = b'HTTP/1.1 404 Not Found\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Reservation id does not exist</TITLE>\n'
                        response += b'</HEAD>\n'
                        response += b'<BODY>'+dictionary["id"].encode()+b' reservation id not exists</BODY></HTML>'
                        connS.send(response)
                    #if found
                    else:
                        response = b'HTTP/1.1 200 OK\r\n\r\n'
                        response += b'<HTML>\n'
                        response += b'<HEAD>\n'
                        response += b'<TITLE>Available hours for week</TITLE>\n'
                        response += b'</HEAD>\n'
                        info="Reservation details ->"+"<BR>\n"+ "Room name:"+str(result[0])+"<BR>\n"+"Activity:"+str(result[1])+"<BR>\n"+"Day:"+days_of_week[int(result[2])]+"<BR>\n"+"Hour:"+str(result[3])+"<BR>\n"+"Duration:"+str(result[4])+"<BR>\n"+"Reservation id:"+str(result[5])
                        response += b'<BODY>' + info.encode() + b'</BODY></HTML>'
                        connS.send(response)

            #invalid operation name
            else:
                print("operasyon yanlış girildi")

            print("Reservation server database datas")
            show_database("Rooms")
            show_database("Activity")
            show_database("Reservation")
            connS.close()


#check if database exists or not. IF not create
if __name__=='__main__':
    if not os.path.exists("database.db"):
        connD = sqlite3.connect("database.db")
        cursor = connD.cursor()
        cursor.execute("CREATE TABLE Rooms (name TEXT PRIMARY KEY)")
        cursor.execute(
            "CREATE TABLE Reservation (room_name TEXT, activity_name TEXT, day INTEGER, hour INTEGER, duration INTEGER,reservation_id INTEGER )")
        cursor.execute("CREATE TABLE Activity (name TEXT PRIMARY KEY)")
        connD.commit()
        connD.close()
    else:
        pass
    #thread operations
    t1 = threading.Thread(target=RoomServer)
    t2 = threading.Thread(target=ActivityServer)
    t3 = threading.Thread(target=ReservationServer)
    t1.start()
    t2.start()
    t3.start()
