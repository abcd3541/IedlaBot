from dotenv import dotenv_values

keys = dotenv_values('mykeys.env')
Token = keys.get('Key')
weather_key = keys.get('WeatherKey')
Gemini = keys.get('GeminiKey')

def get_gem_key():
    return Gemini
def get_Weather_key():
    return weather_key
def get_bot_token():
    print(Token)
    return Token