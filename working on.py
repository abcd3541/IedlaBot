import requests


def weather_thing(Location):
    API_KEY = "ce70ed4bf06e429abb2130612252608"
    URL = "http://api.weatherapi.com/v1/forecast.json"
    try:
        weather = requests.get(URL, params={"key": API_KEY, "q": Location})
        if weather.status_code == 200:
            weather_data = weather.json()
            return weather_data
        elif weather.status_code == 404:
            return "API Broke :broken_heart"
        elif weather.status_code == 400:
            return "Failed to get weather data. :wilted_rose:"
        else:
            return "Good luck solving"
    except json.JSONDecodeError:
        print("Funny error try again :wilted_rose:")
    return None

print(f"{weather_thing(Location='New York')}\n")