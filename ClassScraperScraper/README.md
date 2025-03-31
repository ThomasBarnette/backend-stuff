## Class Scraper Scraper
We steal most recent json file contating gt term data from 

[https://github.com/gt-scheduler/crawler-v2](https://github.com/gt-scheduler/crawler-v2)

To update term data for this app:
1) download the term data from the linked gt-scheduler repo
2) Replace ./data.json with this file
3) Run the python script ./src/update_class_data.py 

What this does:

A) Deletes everything previously in the classes table

B) Attempts to add each section of every class in the updated json file
