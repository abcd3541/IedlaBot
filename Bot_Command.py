from flask import Flask, jsonify, request
import subprocess, time, os, threading, requests, psutil,io
from PIL import Image, ImageDraw
import customtkinter as ctk
from dotenv import dotenv_values
from datetime import datetime

app = Flask(__name__)
Webhook_key = "iedla@iedla"
current_script_dir = os.path.dirname(os.path.abspath(__file__))
main_bot_path = os.path.join(current_script_dir, "main_bot.py")
python_executable = "C:\\ProgramData\\anaconda3\\python.exe"
toggle = f'"{python_executable}" "{main_bot_path}"'

custom_font = "calibri"
Bot_bool = False
process = None
keys = dotenv_values('keys.env')
bot_token = keys.get('Key')
circular_image = None
image_bool = False
bot_user = "N/A"
bot_key = "N/A"

def ping():
    BOT_API_URL = "http://127.0.0.1:5001/bot_latency"
    try:
        response = requests.get(BOT_API_URL, timeout=2)
        response.raise_for_status()
        data = response.json()
        raw_latency = data.get('latency', 'Error')

        try:
            final_ping_int = int(raw_latency)
            if final_ping_int > 0 and not image_bool:
                bot_id_val = get_bot_id()
                if bot_id_val:
                    pfp(bot_id_val, bot_token, bot_user)
            return final_ping_int
        except ValueError:
            print(f"Warning: Latency value '{raw_latency}' is not an integer. Returning string.")
            return str(raw_latency)

    except requests.exceptions.ConnectionError:
        return 'Offline'
    except requests.exceptions.Timeout:
        return 'Timeout'
    except Exception as e:
        print(f"Error fetching bot latency: {e}")
        return 'Error'


def get_bot_id() -> str | None:
    global bot_user
    global bot_key
    retries = 5
    for i in range(retries):
        try:
            response = requests.get("http://127.0.0.1:5001/bot_id", timeout=5)
            response.raise_for_status()
            data = response.json()
            bot_id = data.get('bot_id')
            bot_user_name = data.get('bot_user')
            if bot_id and bot_user_name:
                bot_key = bot_id
                bot_user = bot_user_name
                return bot_id
            else:
                print(f"Attempt {i+1}: Bot ID or User not found in response.")
        except requests.exceptions.ConnectionError as e:
            print(f"Attempt {i+1}/{retries}: Could not connect to bot API")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                print(f"Attempt {i+1}/{retries}: Bot API not ready. ")
            else:
                print(f"Attempt {i+1}/{retries}: HTTP error fetching")
        except Exception as e:
            print(f"Attempt {i+1}/{retries}: Unexpected error fetching bot ID")
        time.sleep(2)
    print("Failed to get bot ID after multiple retries.")
    return None

def pfp(bot_id: str, bot_token: str, user: str) -> str | None:
    global image_bool

    user_api_url = f"https://discord.com/api/v10/users/{bot_id}"
    headers = {
        "Authorization": f"Bot {bot_token}"
    }

    try:
        response = requests.get(user_api_url, headers=headers, timeout=5)
        response.raise_for_status()
        user_data = response.json()

        avatar_hash = user_data.get('avatar')
        if avatar_hash:
            image_format = "gif" if avatar_hash.startswith('a_') else "png"
            base_pfp_url = f"https://cdn.discordapp.com/avatars/{bot_id}/{avatar_hash}.{image_format}"
        else:
            discriminator = user_data.get('discriminator')
            default_avatar_index = int(discriminator) % 5 if discriminator and discriminator != '0' else 0
            base_pfp_url = f"https://cdn.discordapp.com/embed/avatars/{default_avatar_index}.png"

        final_pfp_url = f"{base_pfp_url}?size=64"
        result_image = url_to_image(final_pfp_url)
        if result_image:
            image_bool = True
            print(f"PFP URL fetched and processed: {final_pfp_url}")
            return final_pfp_url
        else:
            print(f"Failed to process image from URL: {final_pfp_url}")
            return None

    except requests.exceptions.ConnectionError:
        print("PFP: Connection Error")
        return "Connection Error"
    except requests.exceptions.Timeout:
        print("PFP: Timeout Error")
        return "Timeout Error"
    except requests.exceptions.HTTPError as e:
        print(f"PFP: HTTP Error: {e.response.status_code} - {e.response.text}")
        return f"HTTP Error: {e.response.status_code}"
    except Exception as e:
        print(f"PFP: An unexpected error occurred: {e}")
        return f"Error: {e}"


def create_circular_image(image_source, output_size: int = 64) -> Image.Image:
    try:
        if isinstance(image_source, str):
            img = Image.open(image_source).convert("RGBA")
        elif isinstance(image_source, io.BytesIO):
            img = Image.open(image_source).convert("RGBA")
        elif isinstance(image_source, Image.Image):
            img = image_source.convert("RGBA")
        else:
            raise ValueError("image_source must be a file path (str), io.BytesIO object, or PIL.Image.Image object.")
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_source}")
        img = Image.new('RGBA', (output_size, output_size), color = 'gray')
        d = ImageDraw.Draw(img)
        d.text((10, output_size // 2 - 10), "Not Found", fill='red')
        return img
    except Exception as e:
        print(f"Error opening image from source {image_source}: {e}")
        img = Image.new('RGBA', (output_size, output_size), color = 'pink')
        d = ImageDraw.Draw(img)
        d.text((10, output_size // 2 - 10), "Error", fill='black')
        return img

    width, height = img.size
    if width != height:
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (width + min_dim) / 2
        img = img.crop((left, top, right, bottom))

    img = img.resize((output_size, output_size), Image.LANCZOS)

    mask = Image.new('L', (output_size, output_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, output_size, output_size), fill=255)

    circular_img = Image.new('RGBA', (output_size, output_size), (0, 0, 0, 0))
    circular_img.paste(img, (0, 0), mask)

    return circular_img

def url_to_image(image_url):
    global circular_image
    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        image_data_bytes = response.content
    except requests.exceptions.RequestException as e:
        print(f"url_to_image: Request Exception getting image data from {image_url}: {e}")
        return None
    except Exception as e:
        print(f"url_to_image: Error fetching image data from {image_url}: {e}")
        return None

    try:
        bot_image = Image.open(io.BytesIO(image_data_bytes))
        circular_image = create_circular_image(bot_image)
        return circular_image
    except Exception as e:
        print(f"url_to_image: Error opening image for {image_url}: {e}")
        return None

def turn_on_bot_process():
    global process
    global Bot_bool
    if Bot_bool:
        print("Bot process already running.")
        return

    print("Turning on bot...")
    command = toggle
    print(f"Command to execute: {command}")
    creationflags = 0
    if os.name == 'nt':
        creationflags = subprocess.CREATE_NO_WINDOW

    try:
        process = subprocess.Popen(command, shell=False, creationflags=creationflags,text=True)
        print(f"Started main_bot.py with PID: {process.pid}")
        Bot_bool = True

        time.sleep(4)

        if process.poll() is not None:
            print(f"main_bot.py exited with code {process.returncode} after starting.")
            Bot_bool = False
            return

        for _ in range(5):
            test_latency = ping()
            if test_latency != 'Offline' and test_latency != 'Timeout' and test_latency != 'Error' and test_latency != 'Waiting':
                print(f"Initial ping latency: {test_latency}")
                break
            time.sleep(2)
        else:
            print("Warning: Bot API did not become responsive after multiple pings.")

        Bot_bool = True
        print("Bot process started successfully and appears to be running.")
        return

    except Exception as e:
        print(f"Failed to turn on bot: {e}")
        Bot_bool = False
        return

def kill_bot_process():
    global Bot_bool
    global process
    global image_bool

    if process is None or process.poll() is not None:
        print("Bot process is not active or has already stopped.")
        Bot_bool = False
        image_bool = False
        return

    target_pid = process.pid

    print(f"Attempting to kill main_bot.py with PID: {target_pid}")
    try:
        if psutil.pid_exists(target_pid):
            process.terminate()
            time.sleep(2)

            if process.poll() is None:
                print(f"Process {target_pid} did not terminate gracefully, attempting .kill().")
                process.kill()
                time.sleep(2)

            if process.poll() is None:
                print(f"Failed to kill process {target_pid} after multiple attempts.")
                Bot_bool = True
                return
            else:
                print(f"Bot process {target_pid} killed successfully.")
                Bot_bool = False
                image_bool = False
        else:
            print(f"Process with PID {target_pid} does not exist (already gone).")
            Bot_bool = False
            image_bool = False

    except PermissionError:
        print(f"Permission denied to kill process {target_pid}. Run Bot_Command.py as administrator?")
        Bot_bool = True
    except Exception as e:
        print(f"Failed to kill bot process {target_pid}: {e}")
        Bot_bool = True
    finally:
        Bot_bool = (process.poll() is None)


@app.route('/webhook', methods=['POST'])
def webhook():
    request_header = request.headers.get('Auth_Key')
    if request_header != Webhook_key:
        return jsonify({'error': 'invalid auth key'})

    data = request.json
    if data is None or 'action' not in data:
        return jsonify({'error': 'no action requested'})

    API_request = data['action']

    if API_request == 'restart':
        kill_bot_process()
        turn_on_bot_process()
        return jsonify({'status': 'restarting'})

    elif API_request == 'stop':
        kill_bot_process()
        return jsonify({'status': 'stopping'})

    else:
        return jsonify({'error': 'invalid action'})


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bot Control")
        self.geometry("480x320")
        self.attributes('-fullscreen', False)
        self.bind("<\>",self.enter_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

        self.time_date_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="gray20")
        self.time_date_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")
        self.time_date_frame.grid_rowconfigure(0, weight=2)
        self.time_date_frame.grid_rowconfigure(1, weight=1)
        self.time_date_frame.grid_rowconfigure(2, weight=1)
        self.time_date_frame.grid_rowconfigure(3, weight=0)
        self.time_date_frame.grid_columnconfigure(0, weight=1)

        self.time_label = ctk.CTkLabel(self.time_date_frame, text="", font=ctk.CTkFont(family=custom_font, size=40, weight="bold"))
        self.time_label.grid(row=1, column=0, padx=20, pady=(20, 0), sticky="s")

        self.date_label = ctk.CTkLabel(self.time_date_frame, text="", font=ctk.CTkFont(family=custom_font, size=20))
        self.date_label.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="n")

        self.status_frame = ctk.CTkFrame(self.time_date_frame, corner_radius=15, fg_color="#FFEF00")
        self.status_frame.grid(row=3, column=0, padx=0, pady=5, sticky="nsew")
        self.status_frame.grid_rowconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self.status_frame, text="Checking status...",font=ctk.CTkFont(family=custom_font, size=20,weight='bold'))
        self.status_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.latency_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="gray20")
        self.latency_frame.grid(row=1, column=2, padx=10, pady=5, sticky="se")
        self.latency_frame.grid_rowconfigure(0, weight=1)
        self.latency_frame.grid_columnconfigure(0, weight=1)

        self.ping_label = ctk.CTkLabel(self.latency_frame, text="", font=ctk.CTkFont(family=custom_font, size=14),width=95, height=30)
        self.ping_label.grid(row=0, column=0, padx=10, pady=5,)

        self.toggles_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="gray20")
        self.toggles_frame.grid(row=1, column=0, columnspan=2, padx=8, pady=5, sticky="s")
        self.toggles_frame.grid_rowconfigure(0, weight=0)
        self.toggles_frame.grid_columnconfigure(0, weight=1)
        self.toggles_frame.grid_columnconfigure(1, weight=1)
        self.toggles_frame.grid_columnconfigure(2, weight=1)

        self.on_button = ctk.CTkButton(self.toggles_frame, text='Toggle On', fg_color="royal blue",
                                       font=ctk.CTkFont(family=custom_font, size=12), command=self.toggle_on,width=95, height=30)
        self.on_button.grid(row=0, column=0, padx=5, pady=5)

        self.off_button = ctk.CTkButton(self.toggles_frame, text='Toggle Off', fg_color="royal blue",
                font=ctk.CTkFont(family=custom_font, size=12), command=self.toggle_off,width=95, height=30)
        self.off_button.grid(row=0, column=1, padx=5, pady=5)

        self.exit_button = ctk.CTkButton(self.toggles_frame, text='Exit', fg_color="royal blue",
                font=ctk.CTkFont(family=custom_font, size=12), command=self.toggle_exit,width=95, height=30)
        self.exit_button.grid(row=0, column=2, padx=5, pady=5)
        self.update_time()
        self.discord_ping()
        self.update_bot_status_display()

        self.bot_info_frame = ctk.CTkFrame(self.time_date_frame, corner_radius=15, fg_color="gray18")
        self.bot_avatar_label = ctk.CTkLabel(self.bot_info_frame, text=" ")
        self.bot_user_label = ctk.CTkLabel(self.bot_info_frame, text="", font=ctk.CTkFont(family=custom_font, weight="bold" ,size=18))
        self.bot_id_label = ctk.CTkLabel(self.bot_info_frame, text="", font=ctk.CTkFont(family=custom_font, size=10))

        self.bot_info_frame.columnconfigure(0, weight=0)
        self.bot_info_frame.columnconfigure(1, weight=1)
        self.bot_info_frame.columnconfigure(2, weight=1)


    def update_bot_status_display(self):
        global Bot_bool
        if Bot_bool:
            self.status_label.configure(text="Online", text_color="white")
            self.status_frame.configure(fg_color="#2de069")
        else:
            self.status_label.configure(text="Offline", text_color="white")
            self.status_frame.configure(fg_color="#e10531")
        self.after(5000, self.update_bot_status_display)

    def toggle_on(self):
        def run_on_thread():
            bot_startup_thread = threading.Thread(target=turn_on_bot_process)
            bot_startup_thread.start()
            bot_startup_thread.join()

            self.after(0, self.update_bot_status_display)
            self.after(1000, self._update_bot_info_gui)

        threading.Thread(target=run_on_thread, daemon=True).start()

    def _update_bot_info_gui(self):
        global circular_image
        global bot_user
        global bot_key
        global image_bool

        if Bot_bool and circular_image and bot_user != "N/A" and bot_key != "N/A" and image_bool:
            self.bot_info_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
            self.bot_avatar = ctk.CTkImage(dark_image=circular_image,size=(40,40))
            self.bot_avatar_label.configure(image=self.bot_avatar, text="")
            self.bot_avatar_label.grid(row=0, column=0, padx=2.5, pady=5, sticky="nsew")

            self.bot_user_label.configure(text=bot_user)
            self.bot_user_label.grid(row=0, column=1, padx=4, pady=0,sticky="w")

            self.bot_id_label.configure(text="ID: "+bot_key)
            self.bot_id_label.grid(row=0, column=2, padx=8, pady=0,sticky="es")
        else:
            print("Bot info not fully ready for GUI update. Retrying in 2 seconds...")
            self.after(2000, self._update_bot_info_gui)

    def toggle_off(self):
        def run_off_thread():
            kill_bot_process()
            self.after(0, self.update_bot_status_display)
            self.after(0, self._clear_bot_info_gui)
        threading.Thread(target=run_off_thread, daemon=True).start()

    def _clear_bot_info_gui(self):
        self.bot_info_frame.grid_forget()
        self.bot_avatar_label.grid_forget()
        self.bot_user_label.grid_forget()
        self.bot_id_label.grid_forget()
        global circular_image, bot_user, bot_key, image_bool
        circular_image = None
        bot_user = "N/A"
        bot_key = "N/A"
        image_bool = False


    def toggle_exit(self):
        kill_bot_process()
        exit()


    def update_time(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%A, %B %d, %Y")

        self.time_label.configure(text=current_time)
        self.date_label.configure(text=current_date)

        self.after(1000, self.update_time)

    def discord_ping(self):
        latency = ping()
        self.ping_label.configure(text="Ping: " + str(latency))
        self.after(10000, self.discord_ping)

    def exit_fullscreen(self, event=None):
        self.attributes('-fullscreen', False)
    def enter_fullscreen(self, event=None):
        self.attributes('-fullscreen', True)


def start_flask():
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        print("Flask initialized")
    except Exception as error:
        print(f'Flask execution error due to {error}')

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    gui_app = App()
    gui_app.mainloop()

    kill_bot_process()