import requests
import json
import time
import concurrent.futures
import functools
import asyncio
import geoip2.database
import os
# I DID NOT WRITE THIS
# im to retarded, I made the general logic then AI fucking made it 12 time better :[
# ill finish my version soon


# --- CONFIGURATION (You MUST fill these in) ---
ROBLOX_SECURITY_COOKIE = ""


IPINFO_API_KEY = "8f24cb1b4b585f"

GEOLITE2_DB_PATH = "GeoLite2-Country.mmdb"
GEOLITE2_READER = None


JAPAN_IP_PREFIXES = [
    "3.112.", "3.113.", "3.114.", "3.115.", "13.208.", "13.209.", "13.210.", "13.211.",
    "18.176.", "18.177.", "18.178.", "18.179.", "35.72.", "35.73.", "35.74.", "35.75.",
    "35.76.", "35.77.", "35.78.", "35.79.", "52.192.", "52.193.", "52.194.", "52.195.",
    "54.199.", "54.238.", "54.248.", "60.67.", "106.126.", "106.127.", "175.41.232.",
    "43.204.144.", "54.184.70.", "3.110.200.", "128.116.14.0",
]

SINGAPORE_IP_PREFIXES = [
    "3.0.", "3.1.", "3.2.", "3.3.", "13.228.", "13.229.", "13.250.", "18.136.",
    "18.137.", "18.138.", "18.139.", "35.240.", "52.220.", "52.221.", "52.74.",
    "52.76.", "52.77.", "54.169.", "54.179.", "54.251.", "54.252.", "54.253.", "54.254.",
    "128.116.6.0", "128.116.82.0", "128.116.83.0",
]

HONG_KONG_IP_PREFIXES = [
    "128.116.21.0", "128.116.22.0", "128.116.79.0", "3.88.", "3.89.", "3.90.",
    "13.210.", "13.211.", "52.68.", "52.69.",
]

# SERVER_REGIONS_BY_IP (Custom RoLocate mapping - primary lookup for granular cities)
SERVER_REGIONS_BY_IP = {
    "128.116.55.0": "SJC", "3.114.16.0": "NRT", "18.138.0.0": "SNG",
    "43.204.144.0": "BOM", "54.184.70.0": "NRT", "3.110.200.0": "NRT",
    "13.233.126.0": "BOM", "10.32.4.0": "SJC", "10.17.4.0": "SJC", "10.30.0.0": "SJC",
    "175.41.232.0": "ICN", "15.206.172.0": "BOM", "128.116.14.0": "NRT",
    "128.116.6.0": "SNG", "128.116.82.0": "SNG", "128.116.83.0": "SNG",
    "128.116.21.0": "HKG", "128.116.22.0": "HKG", "128.116.79.0": "HKG",
    "_locations": {
        "SJC": {"city": "San Jose", "country": {"name": "United States", "code": "US"}, "latitude": 37.3382,
                "longitude": -118.2437},
        "NRT": {"city": "Tokyo", "country": {"name": "Japan", "code": "JP"}, "latitude": 35.6762,
                "longitude": 139.6503},
        "SNG": {"city": "Singapore", "country": {"name": "Singapore", "code": "SG"}, "latitude": 1.3521,
                "longitude": 103.8198},
        "BOM": {"city": "Mumbai", "country": {"name": "India", "code": "IN"}, "latitude": 19.0760,
                "longitude": 72.8777},
        "ICN": {"city": "Seoul", "country": {"name": "South Korea", "code": "KR"}, "latitude": 37.5665,
                "longitude": 126.978},
        "HKG": {"city": "Hong Kong", "country": {"name": "Hong Kong", "code": "HK"}, "latitude": 22.3193,
                "longitude": 114.1694},
    }
}



def _initialize_maxmind_reader():
    global GEOLITE2_READER
    if GEOLITE2_READER is None:
        if not os.path.exists(GEOLITE2_DB_PATH):
            print(
                f"WARNING: GeoLite2 database file not found at '{GEOLITE2_DB_PATH}'. MaxMind lookups will be skipped.")
            GEOLITE2_READER = False
            return False
        try:
            GEOLITE2_READER = geoip2.database.Reader(GEOLITE2_DB_PATH)
            print(f"[DEBUG] GeoLite2 database loaded successfully from {GEOLITE2_DB_PATH}.")
        except Exception as e:
            print(
                f"WARNING: Error loading GeoLite2 database from '{GEOLITE2_DB_PATH}': {e}. MaxMind lookups will fail.")
            GEOLITE2_READER = False
    return GEOLITE2_READER


def _get_location_from_maxmind(ip_address: str) -> dict or None:
    reader = _initialize_maxmind_reader()
    if not reader or reader is False:
        return None
    try:
        response = reader.country(ip_address)
        country_name = response.country.name
        country_code = response.country.iso_code

        return {
            "city": None,
            "country": {"name": country_name, "code": country_code},
            "latitude": None,
            "longitude": None
        }
    except geoip2.errors.AddressNotFoundError:
        return None
    except Exception as e:
        print(f"[DEBUG] MaxMind: Error looking up IP {ip_address}: {e}")
        return None


def _get_location_from_ipinfo(ip_address: str) -> dict or None:
    if not IPINFO_API_KEY or IPINFO_API_KEY == "YOUR_IPINFO_API_KEY_HERE":
        return None

    api_url = f"https://ipinfo.io/{ip_address}?token={IPINFO_API_KEY}"

    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("bogon") or data.get("error"):
            return None

        city = data.get("city")
        country_name = data.get("country_name")
        country_code = data.get("country")
        loc_str = data.get("loc")
        latitude = None
        longitude = None
        if loc_str:
            lat_str, lon_str = loc_str.split(',')
            latitude = float(lat_str)
            longitude = float(lon_str)

        if all(x is not None for x in [city, country_name, country_code, latitude, longitude]):
            return {
                "city": city,
                "country": {"name": country_name, "code": country_code},
                "latitude": latitude,
                "longitude": longitude
            }
        else:
            return None

    except requests.exceptions.RequestException as e:
        pass
    except json.JSONDecodeError as e:
        pass
    except Exception as e:
        pass
    return None

def _classify_ip_region(ip_address):
    if any(ip_address.startswith(prefix) for prefix in JAPAN_IP_PREFIXES):
        return "Japan"
    if any(ip_address.startswith(prefix) for prefix in SINGAPORE_IP_PREFIXES):
        return "Singapore"
    if any(ip_address.startswith(prefix) for prefix in HONG_KONG_IP_PREFIXES):
        return "Hong Kong"
    return "Unknown"


def _find_best_matching_ip(ip_address, ip_map):
    if not ip_map: return None
    ip_keys = [key for key in ip_map.keys() if key != '_locations']

    if ip_address.startswith("128.116."):
        parts = ip_address.split('.')
        if len(parts) == 4:
            prefix_ip = f"{'.'.join(parts[:3])}.0"
            if prefix_ip in ip_keys: return prefix_ip
    parts = ip_address.split('.')
    if len(parts) >= 3:
        three_octets_prefix = ".".join(parts[:3]) + ".0"
        if three_octets_prefix in ip_keys: return three_octets_prefix

    if len(parts) >= 2:
        two_octets_prefix = ".".join(parts[:2]) + ".0.0"
        if two_octets_prefix in ip_keys: return two_octets_prefix

    return None


def _get_location_data_from_ip_map(ip_key, ip_map):
    if not ip_key or not ip_map or '_locations' not in ip_map: return None
    location_id = ip_map.get(ip_key)
    return ip_map['_locations'].get(location_id)


def _fetch_server_ids_from_roblox_api(game_id: int, search_limit: int) -> list:
    endpoint1 = f"https://games.roblox.com/v1/games/{game_id}/servers/public"
    params = {
        "excludeFullGames": "true",
        "sortOrder": 2,
        "limit": search_limit
    }
    headers = {"User-Agent": "Roblox/WinInet"}

    print(f"[DEBUG] Fetching initial server IDs for game `{game_id}` with limit `{search_limit}`...")
    try:
        response = requests.get(endpoint1, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        server_list_data = response.json()

        servers_data = server_list_data.get('data', [])
        if not servers_data:
            print(f"[DEBUG] No initial server data in response for game `{game_id}`.")
            return []

        extracted_ids = [server_dict["id"] for server_dict in servers_data]
        print(f"[DEBUG] Successfully extracted {len(extracted_ids)} server IDs.")
        return extracted_ids
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch initial server list for game ID `{game_id}`: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON decode error in initial server list response for game ID `{game_id}`: {e}")
        return []


def _fetch_and_process_single_server(game_id_val: int, current_server_id_str: str) -> dict or None:
    url = "https://gamejoin.roblox.com/v1/join-game-instance"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Roblox/WinInet",
    }
    cookies = {
        ".ROBLOSECURITY": ROBLOX_SECURITY_COOKIE
    }



    payload = {
        "placeId": int(game_id_val),
        "gameId": current_server_id_str
    }

    try:
        response = requests.post(url, headers=headers, json=payload, cookies=cookies, timeout=10)
        response.raise_for_status()
        response_data = response.json()

        join_script = response_data.get('joinScript')

        if join_script:
            server_address = None
            if 'UdmuxEndpoints' in join_script and join_script['UdmuxEndpoints']:
                server_address = join_script['UdmuxEndpoints'][0]['Address']
            elif 'MachineAddress' in join_script:
                server_address = join_script['MachineAddress']

            if server_address:
                location_data = None

                if SERVER_REGIONS_BY_IP and '_locations' in SERVER_REGIONS_BY_IP:
                    lookup_ip_key = _find_best_matching_ip(server_address, SERVER_REGIONS_BY_IP)
                    if lookup_ip_key:
                        location_data = SERVER_REGIONS_BY_IP['_locations'].get(SERVER_REGIONS_BY_IP.get(lookup_ip_key))

                if not location_data and GEOLITE2_READER and GEOLITE2_READER is not False:
                    maxmind_location = _get_location_from_maxmind(server_address)
                    if maxmind_location:
                        location_data = maxmind_location
                        print(f"[DEBUG] [{current_server_id_str}] MaxMind fallback used for IP: {server_address}")


                if not location_data and IPINFO_API_KEY and IPINFO_API_KEY != "8f24cb1b4b585f":
                    ipinfo_location = _get_location_from_ipinfo(server_address)
                    if ipinfo_location:
                        location_data = ipinfo_location
                        print(f"[DEBUG] [{current_server_id_str}] ipinfo.io fallback used for IP: {server_address}")

                ip_region_classification = "Unknown"
                if location_data and location_data.get('country', {}).get('name'):
                    country_name = location_data['country']['name']
                    if country_name == "Japan":
                        ip_region_classification = "Japan"
                    elif country_name == "Singapore":
                        ip_region_classification = "Singapore"
                    elif country_name == "Hong Kong":
                        ip_region_classification = "Hong Kong"
                    elif country_name == "United States":
                        ip_region_classification = "United States"
                    elif country_name == "India":
                        ip_region_classification = "India"
                    elif country_name == "South Korea":
                        ip_region_classification = "South Korea"
                    else:
                        ip_region_classification = _classify_ip_region(server_address)
                else:
                    ip_region_classification = _classify_ip_region(server_address)

                return {
                    "server_id": current_server_id_str,
                    "ip_address": server_address,
                    "location": location_data,
                    "classified_region": ip_region_classification
                }

    except requests.exceptions.RequestException as e:
        pass
    except Exception as e:
        pass
    return None


async def get_classified_servers_concurrently(game_id: int, server_ids_list: list, max_workers: int = 20) -> list:
    if not server_ids_list:
        print("No server IDs provided for concurrent lookup.")
        return []

    print(f"\n[DEBUG] Starting concurrent server details for game ID: {game_id} (using {max_workers} threads)")
    start_time = time.time()
    results = []

    def _run_concurrent_requests():
        thread_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            func = functools.partial(_fetch_and_process_single_server, game_id)

            futures = {executor.submit(func, server_id): server_id for server_id in server_ids_list}

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                server_id = futures[future]
                try:
                    server_data = future.result()
                    if server_data:
                        thread_results.append(server_data)
                except Exception as e:
                    print(f"  ERROR processing future for {server_id}: {e}")
        return thread_results

    final_results = await asyncio.to_thread(_run_concurrent_requests)

    end_time = time.time()
    print(
        f"[DEBUG] Finished concurrent server details for {len(server_ids_list)} servers. {len(final_results)} successful extractions in {end_time - start_time:.2f} seconds.")
    return final_results


def filter_classified_servers(server_classified_data: list, target_regions: list) -> list:
    filtered_servers = []
    print(f"\n[DEBUG] Filtering servers for classified regions: {', '.join(target_regions)}...")

    for server_info in server_classified_data:
        if not isinstance(server_info, dict):
            print(f"  - WARNING: Skipping non-dictionary item: {server_info} (Type: {type(server_info)})")
            continue

        classified_region = server_info.get('classified_region')
        if classified_region and classified_region in target_regions:
            filtered_servers.append(server_info)

    print(f"[DEBUG] Found {len(filtered_servers)} servers in {', '.join(target_regions)} via IP prefix matching.")
    return filtered_servers


def split_message(messages: list, chunk_size: int = 1900) -> list:
    current_chunk = ""
    chunks = []
    for msg in messages:
        if len(current_chunk) + len(msg) + 1 > chunk_size:
            chunks.append(current_chunk)
            current_chunk = msg
        else:
            if current_chunk:
                current_chunk += "\n" + msg
            else:
                current_chunk = msg
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


async def find_apac_roblox_servers(game_id: int, search_amount: int = 25) -> list:
    _initialize_maxmind_reader()

    if not ROBLOX_SECURITY_COOKIE or ROBLOX_SECURITY_COOKIE == "YOUR_ROBLOX_SECURITY_COOKIE_HERE":
        print("\n*** CRITICAL ERROR: ROBLOX_SECURITY_COOKIE is not set. Server finding will fail. ***")
        return []

    extracted_server_ids = _fetch_server_ids_from_roblox_api(game_id, search_amount)
    if not extracted_server_ids:
        print(f"No initial server IDs found for game ID `{game_id}`.")
        return []

    all_server_classified_data = await get_classified_servers_concurrently(game_id, extracted_server_ids)
    if not all_server_classified_data:
        print(f"Could not retrieve detailed information for any servers for game ID `{game_id}`.")
        return []

    target_regions = ['Japan', 'Singapore', 'Hong Kong']
    apac_servers = filter_classified_servers(all_server_classified_data, target_regions)

    return apac_servers


if __name__ == "__main__":
    _initialize_maxmind_reader()

    if ROBLOX_SECURITY_COOKIE == "YOUR_ROBLOX_SECURITY_COOKIE_HERE":
        print("\n*** WARNING: ROBLOX_SECURITY_COOKIE is not set. Test requests will likely fail. ***")
        print("             Please update ROBLOX_SECURITY_COOKIE in the roblox_server_finder.py file.")

    if IPINFO_API_KEY == "YOUR_IPINFO_API_KEY_HERE":
        print("\n*** WARNING: IPINFO_API_KEY is not set. ipinfo.io lookups will be skipped. ***")
        print("             If you intend to use ipinfo.io, get an API key and update the config.")

    if not SERVER_REGIONS_BY_IP or '_locations' not in SERVER_REGIONS_BY_IP:
        print(
            "\n*** WARNING: SERVER_REGIONS_BY_IP is not fully populated. Detailed location data might be missing. ***")
        print("             Please ensure this dictionary is comprehensive if detailed location is desired.")

    game_id_test = input("Enter game ID for test: ")
    search_amount_test = int(input("Enter search amount (10, 25, 50, 100): "))

    print("\n--- Running synchronous test for server finding ---")

    try:
        filtered_test_servers = asyncio.run(find_apac_roblox_servers(int(game_id_test), search_amount_test))

        print("\n--- APAC Servers Found (Test Run) ---")
        if filtered_test_servers:
            for server in filtered_test_servers:
                display_location = server.get('classified_region', 'Unknown')
                if server.get('location') and server['location'].get('city') and server['location'].get('country',
                                                                                                        {}).get('name'):
                    display_location = f"{server['location']['city']}, {server['location']['country']['name']}"
                print(f"Server ID: {server['server_id']}, IP: {server['ip_address']}, Region: {display_location}")
        else:
            print("No servers found in Japan, Singapore, or Hong Kong during test run.")
    except Exception as e:
        print(f"An error occurred during the test run: {e}")
