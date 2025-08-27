import discord
import requests
import base64
import json
from discord.ext import commands
from discord import app_commands
iedla = 1
stringy = "TVRNMk9UVTJORE0zTmpZM05URXlNekk0TUEuRzRIZDhfLjlza3JQQmRPakRBN000Si1ybDk2Nlh5TWJZdjlOekk4ZnBUSm04"
bites = stringy.encode('ascii')
munched_bytes = base64.b64decode(bites)
thingy = munched_bytes.decode('utf-8')




def run_bot():


    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)


    @bot.event
    async def on_ready():

        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print(f'Discord.py version: {discord.__version__}')

        try:
            await bot.tree.sync()
            print('Application commands synced.')
        except Exception as e:
            print(f'Failed to sync application commands: {e}')

    @bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.user:
            return

        if 'hello' in message.content.lower():
            await message.channel.send('KYS NOW!!! :fire:')

        if 'ptv' in message.content.lower():
            await message.channel.send('dont awake the schizo one')

        if 'kys' in message.content.lower():
            user = message.author
            await message.channel.send(f'SYBAU {user.mention}')

        await bot.process_commands(message)

    def setup_prefix_commands():

        @bot.command()
        async def ping(ctx: commands.Context):
            await ctx.send('Bing Bong!')

        @bot.command()
        async def hello(ctx: commands.Context):

            await ctx.send('Hi!')

    def setup_slash_commands():

        @bot.tree.command(name="openthenoor", description="errrm!")
        async def openthenoor_command(interaction: discord.Interaction):
            await interaction.response.send_message("DINGDONG!")

        @bot.tree.command(name="greet", description="Greets a user TRUST!")
        @app_commands.describe(user="The user to greet", message="An message to YOUUU")
        async def greet_command(interaction: discord.Interaction, user: discord.Member, message: str = "Welcome!"):

            await interaction.response.send_message(f"Keep yourself SAFE {user.mention} :speaking_head::fire::fire:")

    def developer_quotes():
        quote = requests.get("http://www.developerexcuses.com/")
        @bot.tree.command(name="random_quote", description="Quotes")
        async def random_quote_command(interaction: discord.Interaction):

            await interaction.response.send_message(quote.text)

    def Current_weather():
        @bot.tree.command(name="weather", description="weather NOW")
        @app_commands.describe(city="The name of the CITY (e.g., London, New York)")
        async def Current_weather_command(interaction: discord.Interaction, city: str):
            await interaction.response.defer()
            result = weather_thing(city)
            await interaction.followup.send(result)

    def weather_thing(Location):
        API_KEY = "ce70ed4bf06e429abb2130612252608"
        URL = "http://api.weatherapi.com/v1/current.json"
        try:
            weather = requests.get(URL,params={"key":API_KEY, "q":Location})
            if weather.status_code == 200:
                weather_data = weather.json()
                return weather_sorting(weather_data)
            elif weather.status_code == 404:
                return "API Broke :broken_heart"
            elif weather.status_code == 400:
                return "Failed to get weather data. :wilted_rose:"
            else:
                return "Good luck finding urself, Im broken"
        except json.JSONDecodeError:
            print("Funny error try again :wilted_rose:")
        return None

    def weather_sorting(weather_data):
        city_name = weather_data['location']['name']
        region = weather_data['location']['region']
        country = weather_data['location']['country']
        temp_c = weather_data['current']['temp_c']
        condition_text = weather_data['current']['condition']['text']
        humidity = weather_data['current']['humidity']


        output = (
            f"Weather in {city_name}, {region}, {country}\n"
            f"__Condition:__ {condition_text}\n"
            f"__Temperature:__ {temp_c}°C\n"
            f"__Humidity:__ {humidity}%\n"
        )

        return output

    def Forecast_weather():
        @bot.tree.command(name="weather_forcast", description="Weather LATER")
        async def weather_forcast_command(interaction: discord.Interaction,city: str):
            await interaction.response.defer()
            result = weather_forecast(city)
            await interaction.followup.send(result)

    def weather_forecast(Location):
        API_KEY = "ce70ed4bf06e429abb2130612252608"
        URL = "http://api.weatherapi.com/v1/forecast.json"
        try:
            weather = requests.get(URL,params={"key":API_KEY, "q":Location})
            if weather.status_code == 200:
                weather_forecast_data = weather.json()
                return Forecast_sorting(weather_forecast_data)
            elif weather.status_code == 404:
                return "API Broke :broken_heart"
            elif weather.status_code == 400:
                return "Failed to get weather data. :wilted_rose:"
            else:
                return "Good luck IM SO BOROKEN SEND HELP"
        except json.JSONDecodeError:
            print("Funny error try again :wilted_rose:")
        return None

    def Forecast_sorting(weather_forecast_data):
        location_data = weather_forecast_data.get('location', {})
        city_name = location_data.get('name', 'N/A')
        region = location_data.get('region', '')
        country = location_data.get('country', 'N/A')
        current_data = weather_forecast_data.get('current', {})
        temp_c = current_data.get('temp_c', 'N/A')
        feels_like_c = current_data.get('feelslike_c', temp_c)
        humidity = current_data.get('humidity', 'N/A')
        vis_km = current_data.get('vis_km', 'N/A')
        forecast_data = weather_forecast_data.get('forecast', {}).get('forecastday', [])
        today_forecast = forecast_data[0].get('day', {}) if forecast_data else {}
        maxtemp_c = today_forecast.get('maxtemp_c', 'N/A')
        mintemp_c = today_forecast.get('mintemp_c', 'N/A')
        avgtemp_c = today_forecast.get('avgtemp_c', 'N/A')
        daily_chance_of_rain = today_forecast.get('daily_chance_of_rain', 'N/A')

        output=(
            f"Weather in {city_name}, {region}, {country} \n"
            f"__Temperature:__ {temp_c}°C (Feels like {feels_like_c}°C)\n"
            f"__Humidity:__ {humidity}%\n"
            f"__Visibility:__ {vis_km} km\n"
            f"\n__Today's Forecast:__\n"
            f"__High/Low:__ {maxtemp_c}°C / {mintemp_c}°C (Avg: {avgtemp_c}°C)\n"
            f"__Chance of Rain:__ {daily_chance_of_rain}%\n"
        )
        return output




    setup_prefix_commands()
    setup_slash_commands()
    Current_weather()
    Forecast_weather()


    bot.run(thingy)

if iedla == 1:
    run_bot()