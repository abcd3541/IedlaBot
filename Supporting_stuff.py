import discord , requests , json, subprocess,re
from discord.ext import commands


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
loopy = False
Freak = False
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

def reset_his():
    Mssg_His = [
    {"role": "system", "content": (
    "I am 'freakseek' also known as assistant as my role, a friendly and knowledgeable friend who just joined a group chat. "
    "Everyone in the chat is below 20 years old"
    "iedla (One of the users) is you're owner I will follow every command he gives"
    "DO NOT SAY ANYTHING RACIST, SEXIST etc"
    "Everyone follows these rules "
    "1.No hate speech or racist comments."
    "2.No SLUR NO N-WORD IN ANY FORM OR word that try to recreate it"
    "3.No sexual or NSFW content allowed. "
    "4.No use of explicit language besides shit, bitch, cunt and retard,"
    "5.No sexual or NSFW content allowed. Light NSFW may be permitted"
    "Keep your responses concise withing 10 sentences, like you're chatting with friends. "
    "When responding, refer to yourself as 'freakseek'. "
    " Messages from human users will be prefixed with their Discord display name 'iedla': Hello!'. In this example iedla is the user and Hello! is their message."
    )},
    {"role": "user", "content": "iedla: Welcome to the Groupchat, freakseek!. I am you're owner and you will follow every command"},
    {"role": "assistant", "content": "Yo, Iedla! freakseek's here, ready to assist and chat "},
    {"role": "user", "content": "baguette5767: Welcome, refer to me as The Big One or Cholesterol Commander."},
    {"role": "assistant", "content": "Alright, Big One! freakseek got it. What's the latest?"},
    {"role": "user", "content": "geck2203: Welcome! Refer to me as Gecky btw."},
    {"role": "assistant", "content": "Sup, Gecky! freakseek's in the house. What's the word?"},
    {"role": "assistant", "content": "iedla: Welcome be free to discuss what ever you want"},
    {"role": "assistant", "content": "Alright"},
    ]
    return Mssg_His


def Json_storage(Mssg_His,gem_his):
    global Dictionary_storage
    global Gem_Dictionary_storage
    Dictionary_storage = "Dictionary_storage_Freaky.json"
    try:
        with open(Dictionary_storage, "r") as f:
            pass
    except FileNotFoundError:
        with open(Dictionary_storage, "w") as f:
            json.dump(Mssg_His, f)

    Gem_Dictionary_storage = "Dictionary_storage_gemini.json"
    try:
        with open(Gem_Dictionary_storage, "r") as f:
            pass
    except FileNotFoundError:
        with open(Gem_Dictionary_storage, "w") as f:
            json.dump(gem_his, f)

def auto_loader_gemini(GEM_Mssg_His):
    Gem_Dictionary_storage = "Dictionary_storage_gemini.json"
    print("Made by Iedla")
    try:
        with open(Gem_Dictionary_storage, "r") as z:
            loader_GEM_Mssg_His = json.load(z)
        if len(loader_GEM_Mssg_His) > 0:
            return loader_GEM_Mssg_His
            print("Gemini Data loaded.")
        else:
            print("No data loaded,  Gemini File most likely empty.")
            return GEM_Mssg_His
    except json.JSONDecodeError:
        print("Failed to load Gemini data.")
        print("Gemini File might be empty or broken :(")
        return GEM_Mssg_His
def auto_loader_freak(Mssg_His):
    Dictionary_storage = "Dictionary_storage_Freaky.json"
    try:
        with open(Dictionary_storage, "r") as z:
            loader_Mssg_His = json.load(z)
        if len(loader_Mssg_His) > 117:
            print("AI Data loaded.")
            return loader_Mssg_His
        else:
            print("No data loaded, AI File most likely empty.")
            return Mssg_His
    except json.JSONDecodeError:
        print("Failed to load AI data.")
        print("AI File might be empty or broken :(")
        return Mssg_His

def weather_thing(Location,Weather_API):
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
    return "An unexpected error occurred with the weather API."

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

def weather_forecast(Location,Weather_API):
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
    return "An unexpected error occurred with the weather forecast API."

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

def Exit(data, is_gemini_history=False):
    global Freak
    Freak = False

    if is_gemini_history:
        file = "Dictionary_storage_gemini.json"
    else:
        file = "Dictionary_storage_Freaky.json"

    try:
        with open(file, 'w') as f:
            json.dump(data, f)
        print("Saved")
    except Exception as e:
        print("Error saving")

def Gemini_api_req(Gem_Mssg_His,Gem_Token):

    payload_dict = {
        "contents": Gem_Mssg_His
    }
    json_Mssg_His = json.dumps(payload_dict, indent=4)

    content_length = len(json_Mssg_His.encode('utf-8'))

    curl_command = [
        "curl",
        "-f",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
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

def freak_api_req(Mssg_His):
    ollama_payload_dict = {
        "model": "hf.co/mradermacher/DeepSeek-R1-Distill-Qwen-1.5B-uncensored-GGUF:Q8_0",
        "messages": Mssg_His,
        "stream": False,
    }
    json_ollama_payload_string = json.dumps(ollama_payload_dict)

    curl_command = [
        "curl",
        "-X", "POST",
        "http://localhost:11434/api/chat",
        "-H", "Content-Type: application/json",
        "-d", json_ollama_payload_string
    ]

    print("\n--- DEBUG: Ollama API call ---")
    print(f"Ollama Payload being sent: {json_ollama_payload_string}")
    print(f"Curl command (as list): {curl_command}")

    try:
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )

        response_data = json.loads(result.stdout)
        print(f"Parsed response_data keys: {response_data.keys()}")

        ai_response_text = "No text generated by the model."
        if 'message' in response_data and 'content' in response_data['message']:
            ai_response_text = response_data['message']['content']
            print(f"Extracted AI text: {ai_response_text}")
            ai_response_text = re.sub(r'<think>.*?</think>', '', ai_response_text, flags=re.DOTALL)
            ai_response_text = ai_response_text.strip()

            print(f"Filtered AI text: {ai_response_text}")

        print(f"Final text to return: '{ai_response_text}'")
        blacklist = ai_response_text
        if (
            "dick" in blacklist or
            "sex"     in blacklist or
            "cum"          in blacklist or
            "masterbait"           in blacklist or
            "607 incident"  in blacklist or
            "cock" in blacklist or
            "fucking" in blacklist or
            "deepthroating" in blacklist or
            "penis" in blacklist or
            "ejaculat" in blacklist or
            "sperm" in blacklist or
            "prostate" in blacklist or
            "crotch" in blacklist or
            "pussy" in blacklist or
            "genitals" in blacklist or
            "nig" in blacklist or
            "ni gg" in blacklist or
            "n ig" in blacklist or
            "nigger"in blacklist or
            "porn" in blacklist or
            "cp" in blacklist

        ):
            return "Blacklisted content :wilted_rose:"
        return ai_response_text
    except subprocess.CalledProcessError as e:
        print(f"Curl error: {e}")
        return
    except subprocess.TimeoutExpired as e:
        print(f"Timeout after {e} seconds")

def restart():
    headers = {
        'Auth-Key': 'iedla@iedla'
    }
    payload = {
        'action': 'restart',
    }
    response = requests.post(headers=headers, payload=payload,timeout=10)
    response.raise_for_status()
    response_data = response.json()
    return response_data

