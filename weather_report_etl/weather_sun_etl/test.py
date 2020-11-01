import datetime
import logging
import requests
import json
from datetime import date
import pymongo
import azure.functions as func

# get weather report json
weather_url = 'https://api.weather.gov/gridpoints/AKQ/45,77/forecast/hourly'
r = requests.get(weather_url)
data = r.json()

# get first 3 days of hourly weather
per = data['properties']['periods']

# get dates
today_date = date.today()
tomorrow_date = today_date + datetime.timedelta(days=1)
day_after_date = tomorrow_date + datetime.timedelta(days=1)

# cast dates to string
today_date = str(today_date)
tomorrow_date = str(tomorrow_date)
day_after_date = str(day_after_date)

todays_hours = []
tomorrow_hours = []
day_after_hours = []

count = 0
for hour in per:
    curr_date = str(hour['startTime'])[:10]
    if curr_date == today_date:
        hour['number'] = count
        todays_hours.append(hour)
        count += 1
    elif curr_date == tomorrow_date:
        hour['number'] = count
        tomorrow_hours.append(hour)
        count += 1
    elif curr_date == day_after_date:
        hour['number'] = count
        day_after_hours.append(hour)
        count += 1
    if count == 24:
        count = 0

# get sunrise/sunset json for today
sun_url_1 = 'https://api.sunrise-sunset.org/json?lat=37.556933&lng=-77.427022&formatted=0&date=' + today_date
sun_url_2 = 'https://api.sunrise-sunset.org/json?lat=37.556933&lng=-77.427022&formatted=0&date=' + tomorrow_date
sun_url_3 = 'https://api.sunrise-sunset.org/json?lat=37.556933&lng=-77.427022&formatted=0&date=' + day_after_date

# send requests
r_1 = requests.get(sun_url_1)
r_2 = requests.get(sun_url_2)
r_3 = requests.get(sun_url_3)

# extract data
data_1 = r_1.json()
data_2 = r_2.json()
data_3 = r_3.json()

# get sunrise/sunset for the next few days
sunrise_1 = data_1['results']['sunrise']
sunrise_2 = data_2['results']['sunrise']
sunrise_3 = data_3['results']['sunrise']

sunset_1 = data_1['results']['sunset']
sunset_2 = data_2['results']['sunset']
sunset_3 = data_3['results']['sunset']

solar_noon_1 = data_1['results']['solar_noon']
solar_noon_2 = data_2['results']['solar_noon']
solar_noon_3 = data_3['results']['solar_noon']

payload_1 = {
    'date':today_date,
    'sunrise':sunrise_1,
    'sunset':sunset_1,
    'solar_noon':solar_noon_1,
    'periods':todays_hours
}

payload_2 = {
    'date':tomorrow_date,
    'sunrise':sunrise_2,
    'sunset':sunset_2,
    'solar_noon':solar_noon_2,
    'periods':tomorrow_hours
}

payload_3 = {
    'date':day_after_date,
    'sunrise':sunrise_3,
    'sunset':sunset_3,
    'solar_noon':solar_noon_3,
    'periods':day_after_hours
}

uri = "mongodb://weather-report-mongodb:2YCR1nxsdoHtvyFJRYwEESBAbkDDmC9QGtnh3cK9zarK5uvWDFCWLpy3jA0vErtr6muGmVpwWz5mQ3TxeEKOOw==@weather-report-mongodb.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@weather-report-mongodb@&retrywrites=false"
client = pymongo.MongoClient(uri)
wrdb = client["weather_report"]
cont1 = wrdb["daily_temps"]
# x = cont1.insert_one(data)

res = cont1.update_one({'date':today_date},{'$set':payload_1},upsert=True)
res = cont1.update_one({'date':tomorrow_date},{'$set':payload_2},upsert=True)
res = cont1.update_one({'date':day_after_date},{'$set':payload_3},upsert=True)

utc_timestamp = datetime.datetime.utcnow().replace(
tzinfo=datetime.timezone.utc).isoformat()

logging.info('Python timer trigger function ran at %s', utc_timestamp)