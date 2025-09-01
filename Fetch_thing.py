import requests, base64
from bs4 import BeautifulSoup
thingy = '123'
keycode = "Sus"

url = "https://iedla.cloud/"+thingy+"iedla_keys.html"
url2 = "https://iedla.cloud/"+thingy+"iedla_keys1.html"
Gemini_Key = "https://iedla.cloud/Gem_key.html"
Weather_Key = "https://iedla.cloud/Weather_Key.html"

def get_iedla_keys1():
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(strip=True)
        return text
    except requests.exceptions.RequestException as e:
        print(f"Could not get the page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
def get_iedla_keys2():
    try:
        response2 = requests.get(url2)
        response2.raise_for_status()

        soup2 = BeautifulSoup(response2.text, 'html.parser')
        text2 = soup2.get_text(strip=True)
        return text2


    except requests.exceptions.RequestException as e:
        print(f"Could not get the page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
def get_gem_key():
    try:
        response = requests.get(Gemini_Key)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(strip=True)
        bite_text = text.encode('utf-8')
        bite_text = base64.b64decode(bite_text)
        plain_text = bite_text.decode('utf-8')
        secret = 'wjw'
        final = plain_text+secret
        return final


    except requests.exceptions.RequestException as e:
        print(f"Could not get the page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
def get_Weather_key():
    try:
        response = requests.get(Weather_Key)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(strip=True)
        bite_text = text.encode('utf-8')
        bite_text = base64.b64decode(bite_text)
        plain_text = bite_text.decode('utf-8')
        return plain_text
    except requests.exceptions.RequestException as e:
        print(f"Could not get the page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
def get_bot_token():
    Token = get_iedla_keys1()+get_iedla_keys2()+keycode
    print(Token)
    return Token