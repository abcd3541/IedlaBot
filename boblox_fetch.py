import requests
import concurrent.futures
import functools
import time
import os
import geoip2.database
import json



boolmindmax = False
mindmaxfetchlink = "https://drive.usercontent.google.com/download?id=1hyZmPjGCzDixKY6HYzFPhoxodl29Elkm&export=download&authuser=0"
logofetch = "https://github.com/iedlaV2/Rosniffer-Downloads/releases/download/v0/logo.ico"
soundfetch = "https://github.com/iedlaV2/Rosniffer-Downloads/releases/download/v0/ding.mp3"


def down_db(mindmax_target_full_path):
    global boolmindmax
    global_mindmax_db_path = mindmax_target_full_path
    try:
        print(f"  Attempting to download GeoLite2 DB to: {global_mindmax_db_path}")
        response = requests.get(mindmaxfetchlink, stream=True, timeout=30)
        response.raise_for_status()
        with open(global_mindmax_db_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        boolmindmax = True
        print(f"  Downloaded GeoLite2 DB successfully to {global_mindmax_db_path}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  Failed to download GeoLite2 DB from {mindmaxfetchlink}: {e}")
        return False
    except Exception as e:
        print(f"  An unexpected error occurred during GeoLite2 DB download: {e}")
        return False

def mindmax_setup(db_path_for_setup):
    global boolmindmax
    global_mindmax_db_path = db_path_for_setup
    if not boolmindmax:
        try:
            if not os.path.exists(global_mindmax_db_path):
                print(f"  GeoLite2 database not found at {global_mindmax_db_path}. Attempting download...")
                os.makedirs(os.path.dirname(global_mindmax_db_path), exist_ok=True)
                if not down_db(global_mindmax_db_path):
                    print("  GeoLite2 database download failed during setup.")
                    return False
            else:
                boolmindmax = True
                print(f"  GeoLite2 database exists at {global_mindmax_db_path}.")
        except Exception as e:
            print(f"  GeoLite2 setup failed because of: {e}")
            return False
    print(f"  mindmax_setup returning {boolmindmax}")
    return boolmindmax

def mindmax_lookup(serverip: str) -> dict or None:
    global global_mindmax_db_path
    if not boolmindmax or not os.path.exists(global_mindmax_db_path):
        print("  GeoLite2 database not setup or found for lookup.")
        return None

    try:
        with geoip2.database.Reader(global_mindmax_db_path) as reader:
            response = reader.country(serverip)
            country_code = response.country.iso_code
            print(f"  GeoLite2 lookup for {serverip} returned country code: {country_code}")
            return {
                "country_code": country_code
            }
    except geoip2.errors.AddressNotFoundError:
        print(f"  GeoLite2: Address not found for {serverip}.")
        return None
    except Exception as e:
        print(f"  GeoLite2 lookup failed for {serverip} because of {e}")
        return None

def down_icon(target_full_path):
    try:
        print(f"  Attempting to download icon to: {target_full_path}")
        response = requests.get(logofetch, stream=True, timeout=30)
        response.raise_for_status()
        with open(target_full_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  Downloaded logo successfully to {target_full_path}.")
        return f"Downloaded logo successfully to {target_full_path}."
    except requests.exceptions.RequestException as e:
        print(f"  Failed to save logo to {target_full_path}: {e}")
        return f"Failed to save logo to {target_full_path}: {e}"
    except Exception as e:
        print(f"  An unexpected error occurred during logo download: {e}")
        return f"An unexpected error occurred during logo download: {e}"

def down_sound(target_full_path):
    try:
        print(f"  Attempting to download sound to: {target_full_path}")
        response = requests.get(soundfetch, stream=True, timeout=30)
        response.raise_for_status()
        with open(target_full_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  Downloaded sound successfully to {target_full_path}.")
        return f"Downloaded sound successfully to {target_full_path}."
    except requests.exceptions.RequestException as e:
        print(f"  Failed to download sound from {soundfetch}: {e}")
        return f"Failed to download sound from {soundfetch}: {e}"
    except Exception as e:
        print(f"  An unexpected error occurred during sound download: {e}")
        return f"An unexpected error occurred during sound download: {e}"

def fetch_serverid(place_id: int) -> list[str]:
    fetchurl = f"https://games.roblox.com/v1/games/{place_id}/servers/public"
    params = {
        "excludeFullGames": True,
        "sortOrder": 2,
        "limit": 50,
    }
    print(f"  Fetching server IDs for place_id: {place_id} from {fetchurl}")
    try:
        serverid_response = requests.get(fetchurl, params=params, timeout=10)
        serverid_response.raise_for_status()
        serverid_data = serverid_response.json()
        server_data = serverid_data.get('data', [])
        if not server_data:
            print(f"  No server data in response for place_id: {place_id}. Full response: {serverid_data}")
            return []
        exctracted_ids = [ids["id"] for ids in server_data]
        print(f"  Fetched {len(exctracted_ids)} server IDs for place_id: {place_id}. Sample: {exctracted_ids[:5]}")
        return exctracted_ids
    except requests.exceptions.RequestException as e:
        print(f"  Rate Limited or network error fetching server IDs for place_id {place_id}: {e}")
        return []
    except Exception as e:
        print(f"  Exception fetching server IDs for place_id {place_id}: {e}")
        return []

def req_server_data(place_id: int, gameid: str, rblxtoken: str) -> dict or None:
    geturl = "https://gamejoin.roblox.com/v1/join-game-instance"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Roblox/WinInet",
    }
    cookies = {
        ".ROBLOSECURITY": rblxtoken
    }
    payload = {
        "placeId": place_id,
        "gameId": gameid
    }

    location_data = {"country_code": "Unknown"}
    print(f"  Requesting join data for Game ID: {gameid} (Place ID: {place_id})")

    try:
        getresponse = requests.post(geturl, headers=headers, json=payload, cookies=cookies, timeout=10)
        print(f"  Join game instance status for {gameid}: {getresponse.status_code}")
        getresponse.raise_for_status()
        response = getresponse.json()
        print(f"  Join game instance full response for {gameid}: {response}")

        joinscript = response.get("joinScript")

        if joinscript:
            server_ip = None

            if 'UdmuxEndpoints' in joinscript and joinscript['UdmuxEndpoints']:
                server_ip = joinscript['UdmuxEndpoints'][0]['Address']
                print(f"  Found UdmuxEndpoints IP for {gameid}: {server_ip}")
            elif 'MachineAddress' in joinscript:
                server_ip = joinscript['MachineAddress']
                print(f"  Found MachineAddress IP for {gameid}: {server_ip}")

            if not server_ip:
                print(f"  No server IP found in joinScript for Game ID: {gameid}. JoinScript: {joinscript}")
                return None

            if boolmindmax:
                location_result = mindmax_lookup(server_ip)
                if location_result:
                    location_data = location_result
                    print(f"  Location data for {gameid} (IP: {server_ip}): {location_data}")
                else:
                    print(f"  Could not get detailed location for {server_ip} (Game ID: {gameid}) via GeoLite2. Using default.")

            return {
                "gameid": gameid,
                "location_data": location_data
            }
        else:
            roblox_message = response.get("message", "No specific message from Roblox.")
            print(
                f"  No joinScript found for Game ID: {gameid}. Roblox message: {roblox_message}. Full response: {response}")
            return None

    except requests.exceptions.HTTPError as e:
        print(f"  HTTP Error for Game ID. Response text: {e.response.text if e.response else 'N/A'}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  Network/Request Error for Game ID {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"  JSON Decode Error for Game ID ")
        return None
    except Exception as e:
        print(f"  Unexpected Error for Game ID")
        return None

def sorting_threading(place_id: int, gameidlist: list[str], rblxtoken: str) -> list[dict]:
    if not gameidlist:
        print("  No game IDs provided for sorting_threading.")
        time.sleep(10)
        return []
    start = time.time()
    print(f"  Starting sorting_threading for {len(gameidlist)} game IDs.")

    def threading_worker():
        threading_result = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            task = functools.partial(req_server_data, place_id, rblxtoken=rblxtoken)

            futures_map = {executor.submit(task, gameid): gameid for gameid in gameidlist}

            for future in concurrent.futures.as_completed(futures_map):
                original_gameid = futures_map[future]
                try:
                    server_data_dict = future.result()

                    if server_data_dict and isinstance(server_data_dict,dict) and 'gameid' in server_data_dict and 'location_data' in server_data_dict:
                        threading_result.append(server_data_dict)
                    else:
                        print(f"  Invalid or missing data for game ID {original_gameid}.")
                except Exception as e:
                    print(f"  Exception in processing for game ID {original_gameid}: {e}")
        return threading_result

    results = threading_worker()
    end = time.time()
    print(f"  Processed: {len(results)} servers in {end - start:.2f} seconds. Results: {results}")
    return results

def main(cookie, PlaceID, filter):
    cookietemp = cookie
    place_id_input = PlaceID
    db_path_for_main = 'GeoLite2-Country.mmdb'
    print(f"  main function called with PlaceID: {place_id_input}, Filter: {filter}")

    if not mindmax_setup(db_path_for_main):
        return("  GeoLite2 setup failed. Location lookups will not work. Returning False from main.")

    def search():
        gameid = fetch_serverid(place_id_input)

        final_servers = sorting_threading(place_id_input, gameid, cookietemp)

        found_filtered_servers = False
        if final_servers:
            for server in final_servers:
                id = server.get('gameid', 'N/A')
                location_info = server.get('location_data', {})
                country_code = location_info.get('country_code', 'N/A')
                print(f"  Checking server ID: {id}, Location: {country_code}")

                if country_code in filter:
                    base_share_url = "iedlav2.github.io/RoSniffer-Forwarder/"
                    share_link = f"{base_share_url}?placeid={place_id_input}&serverid={id}"
                    found_filtered_servers = True
                    link = share_link
                    return link

        if not found_filtered_servers:
            print(f"  No servers found in {filter}. Searching again in 10 seconds...")
            time.sleep(10)
            return search()

    returned = search()
    print(f"  main function returning: {returned}")
    return returned