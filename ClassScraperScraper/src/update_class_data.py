import requests
import json
import os
import sqlite3
from sqlite3 import Error

def build_and_send_requests():
    api_url = "http://127.0.0.1:8000/api/classes/add_class/"

    current_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of this script
    file_path = os.path.join(current_dir, '../data.json')  # Parent folder of src

    with open(file_path, 'r') as file:
        data = json.load(file)
        # print("data: " + data)

    periods = data["caches"]["periods"]
    lecture_types = data["caches"]["scheduleTypes"]
    
    for course_id, course_data in data["courses"].items():

        course_name_long = course_data[0] 

        dict_of_sections = course_data[1]

        emptpy_list_maybe = course_data[2] # not used but its in the json but its usually empty and I have no idea what it is

        description = course_data[3]

        for section_id, section_data in dict_of_sections.items():
            crn = section_data[0]

            nother_list = section_data[1]
            try:
                nother_nother_list = nother_list[0]
                time_block = nother_nother_list[0]
                time = periods[time_block]
                days = nother_nother_list[1]
                room = nother_nother_list[2]
                lecture_block = section_data[3]
                lecture_type = lecture_types[lecture_block]
                if days == "" or time == "":
                    days = "Asyncronous / TBA"
                    time = "Asyncronous / TBA"
            except:
                time = "Cannot find time"
                days = "Cannot find days"
                room = "Cannot find room"

            
            try:
                prof = nother_nother_list[4][0]
            except:
                prof = "Cannot find professor"

            json_payload = {
                "class_name": course_id,
                "class_name_long": course_name_long,
                "section": section_id,
                "crn": crn,
                "time": time,
                "days": days,
                "room": room,
                "instructor": prof,
                "description": description,
                "type": lecture_type,
            }
            
            response = requests.post(api_url, json=json_payload)
            print(response.text)
                                
def delete_table():
    url = "http://127.0.0.1:8000/api/classes/delete_everything/"
    response = requests.delete(url)
    print(response.text)

delete_table()
build_and_send_requests()
