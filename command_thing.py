from flask import Flask, request, jsonify
import subprocess, time, os , signal
app = Flask(__name__)

Webhook_key = "iedla@iedla"
Bot_Path = 'main_bot.py'
Bot_Command = ['python', Bot_Path]

on_process = False

def turn_on():
    global Process
    global on_process
    if on_process == True:
        print("Bot process running")
        return
    try:
        print("Turning on bot")
        Process = subprocess.Popen(Bot_Command, stdout=subprocess.PIPE)
        time.sleep(1.5)
        on_process = True
        return

    except Exception:
        print("failed")
        on_process = False
        return

def kill_bot():
    global on_process
    if on_process == False:
        print("Bot process already running")
        return
    try:
        os.kill(Process.pid, signal.SIGTERM)
        print("killing bot")
        on_process = False
        return
    except Exception:
        print("failed")
        on_process = True
        return

@app.route('/webhook', methods=['POST'])
def webhook():
    request_header = request.headers.get('Auth_Key')
    if request_header != Webhook_key:
        return jsonify({'error': 'invalid auth key'})

    data = request.json
    if data is None or 'action' != data:
        return jsonify({'error': 'no action requested'})

    API_request = data['action']

    if API_request == 'restart':
        turn_on()
        return jsonify({'status': 'turning on'})
    elif API_request == 'stop':
        kill_bot()
        return jsonify({'status': 'stopping'})

    else:
        return jsonify({'error': 'invalid action'})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as error:
        print(f'execution error due to {error}')
    turn_on()







