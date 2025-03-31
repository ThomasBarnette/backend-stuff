# Backend Documenation
## Steps to host django locally
1) Clone the repository
2) Navigate to backend
   ```cd ../theta-chi-classes/backend```
3) Activate the python virtual environment
   ```source venv/bin/activate```
4) ```cd ./Django```
5) Start django server locally
   ```python manage.py runserver```

## To update schema
Update contents in backend/api/models.py
Updates will only apply after running
```
python manage.py makemigrations
python manage.py migrate
```

## Api documentation (Also in backend/api)
Current endpoints:

## POST http://.../api/classes/add_class
This adds a class to the classes table

It will return err code 400 if any of these fields are missing in the request body:

``` ["class_name", "class_name_long", "room", "description", "crn", "days", "time", "instructor", "section"] ```

It will return 201 upon succesfull addition to the db

Example request body:
```
{
  "id": 19411,
  "course_id": "VIP 6603",
  "course_name": "VIP Proj Team: GR III",
  "crn": "34884",
  "instructor": "Donald Webster",
  "room": "TBA",
  "time": "1001 - 1450",
  "days": "W",
  "section": "VYO",
  "description": "Multidisciplinary course supporting faculty research. Students can participate multiple semesters. Graduate students will pursue needed knowledge/skills; make meaningful contributions; provide leadership in technical areas/team management."
}
```


## DELETE http://.../api/classes/delete_everything
This deletes every single item in the classes table

The idea is that everytime we want to update the current course list, we steal the json from gt scheduler and completley refresh our db with their updated data

No request body

Returns 204 on success

## DELETE http://.../api/classes/delete_class
Deletes a single class by its crn or id (row id given by django)

Example request body: 
```
{
crn: 123456
}
```
returns 204 on success

## GET http://.../api/classes/get_users_in_class
This gets the data of all users in a class by crn

Example request body: 
```
{
crn: 12345
}
```
Example response:
```
{
crn: 123456
users:
     [ {
      first_name: "thomas",
      last_name: "barnette",
      roster: "1857"
     }, ... ]
```

## POST http://.../api/users/create_user
Adds a user to the table

Example request body: 
```
{
    first_name: "thomas",
    last_name: "barnette",
     roster: "1857"
}
```
returns 201 on success

## POST http://.../api/users/add_classes_to_user
Adds any number of classes to a user. Classes added by list of crns. User identified by first and last name.

Example request body: 
```
{
    first_name: "thomas",
    last_name: "barnette",
    crn_list: [
         12345,
         55555,
         ...
    ]
}
```
Returns 201 on success

## GET http://.../api/users/get_user_classes
Gets all classes associated with a user

Example request body: 
```
{
    first_name: "thomas",
    last_name: "barnette"
}
```

Example response
```
{
    "user": "thomas barnette",
    "classes": [
        {
            "crn": "28210",
            "course_id": "CS 3510",
            "course_name_long": "Dsgn&amp;Analysis-Algorithms",
            "description": "Basic techniques of design and analysis of efficient algorithms for standard computational problems. NP-Completeness.  Credit not allowed for both CS 3510 and CS 3511.",
            "instructor": "Zongchen Chen (P)",
            "days": "TR",
            "time": "0930 - 1045",
            "room": "Clough UG Learning Commons 152",
            "section": "B"
        },
       {...},
       ...
    ]
}
```
Returns 200 on success

## DELETE http://.../api/users/delete_user_classes
Removes any number of classes by crn

Example request:
```
{
    "first_name": "thomas",
    "last_name": "barnette",
    "crn_list": [
        "28210"
    ]
}
```

Example response:
```
{
    "removed": [
        "28210"
    ],
    "failed": []
}
```
returns 200 on success


