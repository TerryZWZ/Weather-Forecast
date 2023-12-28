import os # For abstraction
import time # Date formatting
import datetime # Date formatting
import requests # To get information from API
from flask import Flask, render_template, request, redirect, url_for, flash # To create webpage
from flask_sqlalchemy import SQLAlchemy # To create a database

# For environmental variables
from dotenv import load_dotenv
load_dotenv()

# Setup for Flask and SQLAlchemypip ins
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI', "sqlite:///weather.db")
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY', "default_secret")
db = SQLAlchemy(app)

# Creating City class
class City(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)

    def __repr__(city):
        return f"City:  { city.name }"

unit = "metric" # Can set unit to be Celsius or Fahrenheit

# Function to request information of a city from API
def weatherData(city, choice):
    key = os.getenv('OPENWEATHER_API_KEY', 'default_api_key')

    if choice == "forecast":
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={ city }&units={ unit }&appid={ key }"
    else:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ city }&units={ unit }&appid={ key }"

    data = requests.get(url).json()

    return data

# Function to call information of saved cities
def savedCities():
    cities = City.query.all()   # Lists all cities
    weatherList = [] # Array to contain weather data for each city

    # For loop to define information into a dictionary for each city
    for city in cities:
        data = weatherData(city.name, "weather")

        weather = {
            "city" : data["name"],
            "country" : data["sys"]["country"],
            "temperature" : round(data["main"]["temp"]),
            "feels_like" : round(data["main"]["feels_like"]),
            "description" : data["weather"][0]["description"],
            "icon" : data["weather"][0]["icon"],
        }

        weatherList.append(weather) # Adding dictionary entry to array

    return weatherList

def addCity():
    addCity = request.form.get("cityAdd")

    # If city is already saved, input an error message
    if addCity:
        existedCity = City.query.filter_by(name = addCity).first()
        
        # If a city is not saved, save the city in the database
        if not existedCity:
            newCityData = weatherData(addCity, "weather")

            if newCityData["cod"] == 200:
                newCity = City(name = addCity)
                db.session.add(newCity)
                db.session.commit()
                return f"{ newCity.name } has been saved"
            else:
                return "City does not exist"  
        else:
            return "City has already been added"

# Function to delete citiy from saved cities
def delCity(name):
    removeCity = City.query.filter_by(name = name).first()
    db.session.delete(removeCity)
    db.session.commit()

    return f"{ removeCity.name } has been unsaved"

# Default page
@app.route("/")
def indexGet():
    db.create_all()
    weatherList = savedCities() # Calls saved cities
    return render_template("weather.html", weatherList = weatherList) # Connects and sends script information to HTML file

# Checking and displaying information when search is made
@app.route("/", methods = ["POST"]) # Checks for POST submission
def indexSearch():
    errorMessage = ""
    hold = ""
    city = request.form.get("city") # Gets name of city from input in HTML file
    cityAdd = request.form.get("cityAdd") # Gets name of cityAdd from input in HTML file
    cityDel = request.form.get("cityDel") # Gets name of cityDel from input in HTML file
    citySelect = request.form.get("citySelect") # Gets name of citySelect from input in HTML file

    # If city button is pressed, cityAdd exists and city is added
    if cityAdd:
        hold = addCity()
        city = cityAdd # To retain previous displayed city

    # If delete saved city button is pressed, cityDel exists and city is removed from saved city database
    if cityDel:
        hold = delCity(cityDel)
        city = request.form.get("keepCity") # Gets name of cityAdd from input in HTML file
        print(city)
        
        if city == None:
            return render_template("weather.html")

    # If saved city is selected, citySelect exists and the selected city is searched for
    if citySelect:
        city = citySelect
    
    weatherList = savedCities() # Calls saved cities
    weatherInfo = []

    # If search bar is empty
    if city == "":
        return render_template("weather.html")

    data = weatherData(city, "weather") # Request data for a particular city
    newCity = City(name = city) # Create a City object for that particular city
    
    # Organizing Information of City
    if data["cod"] == 200:

        weather = {
            # Main Information
            "city" : data["name"],
            "country" : data["sys"]["country"],
            "temperature" : round(data["main"]["temp"]),
            "feelsLike" : round(data["main"]["feels_like"]),
            "description" : data["weather"][0]["description"],
            "icon" : data["weather"][0]["icon"],
            "background" : data["weather"][0]["main"],

            # Other Information
            "tempMin" : round(data["main"]["temp_min"]),
            "tempMax" : round(data["main"]["temp_max"]),
            "humidity" : data["main"]["humidity"],
            "wind" : data["wind"]["speed"],
            "sunrise" : time.strftime("%H:%M %p", time.localtime(data["sys"]["sunrise"] - data["timezone"])),
            "sunset" : time.strftime("%H:%M %p", time.localtime(data["sys"]["sunset"] - data["timezone"]))
        }

        backgroundImages = {
            "Clear" : "https://wallpaperaccess.com/full/626893.jpg",
            "Clouds": "https://wallpaperaccess.com/full/1462210.jpg",
            "Rain": "https://wallpapercave.com/wp/kQpFYUU.jpg",
            "Thunderstorm": "https://wallpaperaccess.com/full/1563468.jpg",
            "Drizzle": "https://wallpaperaccess.com/full/1540005.jpg",
            "Snow": "https://wallpapercave.com/wp/wp8077043.jpg",
            "Atmosphere": {
                "mist": "https://wallpaper.dog/large/20449220.jpg",
                "fog": "https://wallpaper.dog/large/20449220.jpg",
                "sand": "https://wallpaperaccess.com/full/4305301.jpg",
                "sand/ dust whirls": "https://wallpaperaccess.com/full/4305301.jpg",
                "Smoke": "https://wallpaperaccess.com/full/128756.jpg",
                "Haze": "https://wallpaperaccess.com/full/128756.jpg",
                "volcanic ash": "https://wallpaperaccess.com/full/128756.jpg",
                "tornado" : "https://wallpaperaccess.com/full/452152.jpg",
                "squalls" : "https://wallpaperaccess.com/full/452152.jpg"
            }
        }

        weatherInfo.append(weather) # Adding dictionary entry to array

        # Setting background image based on state of weather
        image = backgroundImages.get(weather["background"], "")

        if weather["background"] == "Atmosphere":
            image = backgroundImages["Atmosphere"].get(weather["description"], "")

        print(weather["background"])
        print(image)
        print("hi")
            
        weatherBackground = f'<style>html {{background: url("{ image }");-webkit-background-size: cover; -moz-background-size: cover; -o-background-size: cover; background-size: cover;}}</style>'

        # Checks if rain and snow information are available and adds to weather information if it is
        try:
            weather.update({ "rain" : data["rain"]["1h"] })
        except KeyError:
            weather.update({ "rain" : "N/A" })
        
        try:
            weather.update({ "snow" : data["snow"]["1h"] })
        except KeyError:
            weather.update({ "snow" : "N/A" })
    else:
        errorMessage = "City does not exist" # Sending error message that city does not exist

    # 5 Day Forecast
    forecast = weatherData(city, "forecast") # Requesting forecast Information
    forecastInfo = []

    if int(forecast["cod"]) == 200:
        forecastData = forecast["list"]

        # Sending data for each day
        for day in forecastData:

            # Formatting date
            parseDate = datetime.datetime.strptime(day["dt_txt"], "%Y-%m-%d %H:%M:%S")
            stringDate = parseDate.strftime("%A, %B %d")
            dayOfWeek, monthDay = stringDate.split(", ")
            timePM = parseDate.strftime("%H:%M %p")

            if(timePM == "12:00 PM"):
                forecasted = {
                    "dayOfWeek" : dayOfWeek,
                    "monthDay" : monthDay,
                    "description" : day["weather"][0]["description"],
                    "temperature" : round(day["main"]["temp"]),
                    "icon" : day["weather"][0]["icon"]
                }
                forecastInfo.append(forecasted)

    else:
        errorMessage = "Forecast is not available" # Sending error message that forecast is not available

    notification = "" 

    # To indicate to notification if there is error
    if errorMessage:
        notification = "notificationError"
    elif cityAdd:
        errorMessage = hold
        notification = "notificationSave"
    elif cityDel:
        errorMessage = hold
        notification = "notificationUnsave"
    else:
        notification = "notificationSuccess"

    unhide = True # Unhides notification and forecast card

    # Connects and sends script information to HTML file
    return render_template("weather.html", 
        weatherInfo = weatherInfo, 
        weatherList = weatherList, 
        weatherBackground = weatherBackground,
        forecastInfo = forecastInfo, 
        unhide = unhide,
        errorMessage = errorMessage,
        notification = notification)

# Sets up link to see page
if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug = True, port = 5000)