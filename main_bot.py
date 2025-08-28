import discord , requests , json , random, asyncio, subprocess
from Fetch_thing import get_bot_token, get_gem_key, get_Weather_key
from discord import app_commands
from discord.ext import commands


Bot_Token = get_bot_token()
Gem_Token = get_gem_key()
Weather_API = get_Weather_key()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
loopy = False
Mssg_His = [
    {"role": "user", "parts": [{"text": "Hello!"}]},
    {"role": "model", "parts": [{"text": "Hello!"}]}
]

Dictionary_storage = "Dictionary_storage.json"
try:
    with open(Dictionary_storage, "r") as f:
        pass
except FileNotFoundError:
    with open(Dictionary_storage, "w") as f:
        json.dump([], f)
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

def auto_loader():
    global Mssg_His
    print("Made by Iedla")
    try:
        with open(Dictionary_storage, "r") as z:
            Mssg_His = json.load(z)
        if len(Mssg_His) > 0:
            print("Data loaded.")
        else:
            print("No data loaded, File most likely empty.")
    except json.JSONDecodeError:
        print("Failed to load data.")
        print("File might be empty or broken :(")
auto_loader()
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Discord python version: {discord.__version__}')

    try:
        await bot.tree.sync()
        print('Application commands synced.')
    except Exception as e:
        print(f'Failed to sync application commands: {e}')

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    target_ptv_user_id = 993302485244592238
    if 'ptv' in message.content.lower() and message.author.id == target_ptv_user_id:
        ptv_rng = random.randint(1,12)
        if ptv_rng == 4 or ptv_rng == 5 or ptv_rng == 6 or ptv_rng == 7:
            await message.channel.send('GETOUTTT')

    if 'kys' in message.content.lower():
        user = message.author
        await message.channel.send(f'SYBAU {user.mention}')

    await bot.process_commands(message)

#! commands
@bot.command()
async def knock(ctx: commands.Context):
    await ctx.send('Bing Bong!')

@bot.command()
async def sendhelp(ctx: commands.Context):
    await ctx.send('Commands: !sendhelp, !ping, !hello, !freakmode/AI Mode. + other / commands')

@bot.command()
async def hello(ctx: commands.Context):
    await ctx.send('Hi!')

@bot.command(name='roleuser', help='Gives a role to a user.')
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role:
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("You don't have permissions for that, lil bro.")
            return
        if role >= ctx.guild.me.top_role:
            await ctx.send(f"No perms gang. '{role.name}' is too high up. :broken_heart:")
            return

        if role in member.roles:
            await ctx.send(f"{member.mention} already has the role '{role.name}', you might be slow.")
        else:
            try:
                await member.add_roles(role)
                await ctx.send(f"Done gangalang, the role '{role.name}' has been given to {member.mention}.")
            except discord.Forbidden:
                await ctx.send("I don't have permissions for that for some reason.")
    else:
        await ctx.send(f"'{role_name}' not found. Look for a better one.")


@bot.command(name='freakmode', help='freak ai mode self explanatory. exit to exit')
async def freakmode(ctx):
    await ctx.send("exit to exit")
    await ctx.send("Start :speaking_head::fire::fire::fire:")
    def check(m):
        return m.channel == ctx.channel and m.author != bot.user
    while True:
        try:
            message = await bot.wait_for('message', check=check, timeout=240)
            decoded_message = message.content.strip()

            if decoded_message.lower() == 'exit':
                Exit(Mssg_His)
                await ctx.send("Convo killed smh")
                break

            Mssg_His.append({"role": "user", "parts": [{"text": decoded_message}]})
            model_response_text = await bot.loop.run_in_executor(
                None,
                api_req
            )

            Mssg_His.append({"role": "model", "parts": [{"text": model_response_text}]})

            await ctx.send(model_response_text)
        except asyncio.TimeoutError:
            await ctx.send("No one responded in time yall slow af.")
            break
        except Exception as e:
            await ctx.send("Something went wrong so i died :(")
            break

#Slash Commands
@bot.tree.command(name="openthenoor", description="errrm!")
async def openthenoor_command(interaction: discord.Interaction):
    await interaction.response.send_message("DINGDONG!")

@bot.tree.command(name="greet", description="Greets a user TRUST!")
@app_commands.describe(user="The user to greet", message="An message to YOUUU")
async def greet_command(interaction: discord.Interaction, user: discord.Member, message: str = "Welcome!"):
    await interaction.response.send_message(f"Keep yourself SAFE {user.mention} :speaking_head::fire::fire:")

@bot.tree.command(name="random_quote", description="Quotes")
async def random_quote_command(interaction: discord.Interaction):
    await interaction.response.defer() # Defer the response as API call might take time
    quote_res = requests.get("https://zenquotes.io/api/random")
    data = quote_res.json()
    if len(data) > 0:
        quote = data[0].get("q")
        author = data[0].get("a")
        await interaction.followup.send(f"{quote}   **{author}**")
    else:
        await interaction.followup.send("Could not fetch a quote at this time.")

@bot.tree.command(name="weather", description="weather NOW")
@app_commands.describe(city="The name of the CITY (e.g., London, New York)")
async def current_weather_command(interaction: discord.Interaction, city: str):
    await interaction.response.defer()
    result = weather_thing(city) # weather_thing is a synchronous function, so it's okay to call directly
    await interaction.followup.send(result)

@bot.tree.command(name="weather_forcast", description="Weather LATER")
@app_commands.describe(city="The name of the CITY (e.g., London, New York)")
async def weather_forcast_command(interaction: discord.Interaction, city: str):
    await interaction.response.defer()
    result = weather_forecast(city)
    await interaction.followup.send(result)

# support functions
def weather_thing(Location):
    URL = "http://api.weatherapi.com/v1/current.json"
    try:
        weather = requests.get(URL,params={"key":Weather_API, "q":Location})
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
    return "An unexpected error occurred with the weather API." # Return a string in case of error

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

def weather_forecast(Location):
    URL = "http://api.weatherapi.com/v1/forecast.json"
    try:
        weather = requests.get(URL,params={"key":Weather_API, "q":Location})
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
    return "An unexpected error occurred with the weather forecast API." # Return a string in case of error

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

def Exit(data):
    with open(Dictionary_storage, 'w') as f:
        json.dump(data, f)

def api_req():
    global Mssg_His
    payload_dict = {
        "contents": Mssg_His
    }
    json_Mssg_His = json.dumps(payload_dict, indent=4)

    content_length = len(json_Mssg_His.encode('utf-8'))

    curl_command = [
        "curl",
        "-f",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "-H", "Content-Type: application/json",
        "-H", f"X-goog-api-key: {Gem_Token}",
        "-H", f"Content-Length: {content_length}",
        "-X", "POST",
        "-d", json_Mssg_His
    ]

    print("\n--- DEBUG: api_req call ---")
    print(f"Payload being sent: {json_Mssg_His}")
    print(f"Curl command (as list): {curl_command}")

    try:
        result = subprocess.run(
            curl_command,
            input=json_Mssg_His,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Curl stdout: {result.stdout.strip()}")
        print(f"Curl stderr: {result.stderr.strip()}")

        response_data = json.loads(result.stdout)
        print(f"Parsed response_data keys: {response_data.keys()}")

        ai_response_text = "No text generated by the model."
        if 'candidates' in response_data and response_data['candidates']:
            print("Found 'candidates' key.")
            first_candidate = response_data['candidates'][0]
            if 'content' in first_candidate and 'parts' in first_candidate['content']:
                print("Found 'content' and 'parts' keys.")
                for part in first_candidate['content']['parts']:
                    if 'text' in part:
                        ai_response_text = part['text']
                        print(f"Extracted AI text: {ai_response_text}")
                        break
        print(f"Final text to return: '{ai_response_text}'")
        return ai_response_text

    except subprocess.CalledProcessError as e:
        print(f"--- ERROR: Curl command failed ---")
        print(f"Return code: {e.returncode}")
        print(f"Stderr: {e.stderr.strip()}")
        print(f"Stdout: {e.stdout.strip()}")
        try:
            error_response = json.loads(e.stdout)
            error_message = error_response.get('error', {}).get('message', 'Unknown API error.')
            return f"AI API Error: {error_message}"
        except json.JSONDecodeError:
            return "AI API Error: Received non-JSON error response."
    except json.JSONDecodeError:
        print(f"--- ERROR: JSON Decode Failed (after successful curl exit) ---")
        print(f"Raw curl stdout: {result.stdout.strip() if 'result' in locals() else 'No stdout captured'}")
        return "The AI service returned an unreadable response."
    except FileNotFoundError:
        print(f"--- ERROR: Curl Not Found ---")
        return "curl gone :wilted_rose:."
    except Exception as e:
        print(f"--- ERROR: Unexpected Exception ---")
        print(f"Exception details: {e}")
        return "computer died."


if __name__ == "__main__":
    bot.run(Bot_Token)