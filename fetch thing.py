import requests, base64
from bs4 import BeautifulSoup

url = 'https://iedla.cloud/iedla_keys.html'
def get_iedla_keys():
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(strip=True)
        bite_text = text.encode('utf-8')
        bite_text = base64.b64decode(bite_text)
        plain_text = bite_text.decode('utf-8')
        print(plain_text)

    except requests.exceptions.RequestException as e:
        print(f"Could not get the page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
get_iedla_keys()