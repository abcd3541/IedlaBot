import discord, random,asyncio,logging,requests,json,re,math,threading,time
from flask import Flask ,jsonify
from Supporting_stuff import reset_his, auto_loader_freak, Json_storage, weather_thing, weather_forecast, \
    freak_api_req, Exit, bot_restart_now,kill_my_bot,todo_lst, get_todolst,\
    add_task, save_todo, del_task, uncen_reset_his
from boblox_fetch import main
from discord import app_commands
from discord.ext import commands


from dotenv import dotenv_values
keys = dotenv_values('keys.env')
Bot_Token = keys.get('Key')
Weather_API = keys.get('WeatherKey')
cookie = keys.get('Roblox_Cookie')
venice_key = keys.get('Venice_Key')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
loopy = False
Freak = False
seek = False
gemini = False
Mssg_His = reset_his()
uncen_Mssg_His = uncen_reset_his()
Dictionary_storage = "Dictionary_storage.json"
bot_api_app = Flask(__name__)
API_PORT = 5001


supported_countries = [
    'HK','SG','GB',
    'FR','DE','JP',
    'IN','AU','KR',
    'NL','US','PL'
]

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

Json_storage(Mssg_His,)
Mssg_His = auto_loader_freak(Mssg_His)
current_bot_latency = 'Waiting'

@bot.event
async def on_ready():
    global target_id
    global target_user
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Discord python version: {discord.__version__}')

    try:
        await bot.tree.sync()
        print('Application commands synced.')
    except Exception as e:
        print(f'Failed to sync application commands: {e}')

    global current_bot_latency
    current_bot_latency = round(bot.latency * 1000)
    target_id = bot.user.id
    target_user = bot.user
    update_latency_task.start()


from discord.ext import tasks

@tasks.loop(seconds=10)
async def update_latency_task():
    global current_bot_latency
    if hasattr(bot, 'latency') and bot.latency is not None and not math.isinf(bot.latency) and not math.isnan(bot.latency):
        current_bot_latency = round(bot.latency * 1000)
    else:
        current_bot_latency = 'Offline'

@bot_api_app.route('/bot_latency', methods=['GET'])
def get_bot_latency_route():
    latency = current_bot_latency
    if latency == 'Waiting':
        return jsonify({'latency': latency, 'status': 'Bot not ready'}), 200
    elif latency == -1:
        return jsonify({'latency': latency, 'status': 'Latency infinite/invalid'}), 200
    else:
        return jsonify({'latency': latency, 'status': 'OK'}), 200

@bot_api_app.route('/bot_id', methods=['GET'])
def get_bot_id_route():
    if target_id is None or target_user is None:
        return jsonify({'error': 'Bot ID not yet available', 'status': 'Bot not ready'}), 503
    return jsonify({'bot_id': str(target_id), 'bot_user' : str(target_user),'status': 'OK'}), 200


#instant react
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    target_ptv_user_id = 993302485244592238
    if 'ptv' in message.content.lower() and message.author.id == target_ptv_user_id:
        ptv_rng = random.randint(1,10)
        if ptv_rng == 4 :
            await message.channel.send('cringe')

    if 'kys now' in message.content.lower():
        user = message.author
        await message.channel.send(f'SYBAU {user.mention}')

    if '67' in message.content.lower():
        user = message.author
        await message.channel.send(f"GTFO {user.mention}",delete_after=10)
        await message.delete()


    content = message.content.lower()
    if (
            "2025/8/29 6:07" in content or
            "2025/8/29" in content or
            "29/8/2025" in content or
            "29/8/" in content or
            "6:07" in content or
            "607" in content or
            "607 incident" in content
    ):
        if message.author is bot.user:
            return
        try:
            await message.delete()
        except discord.Forbidden:
            await message.channel.send("no perms.")

    await bot.process_commands(message)


#! commands
@bot.command()
async def knock(ctx: commands.Context):
    await ctx.send('Bing Bong!')

@bot.command()
async def latency(ctx: commands.Context):
    await ctx.send(f'Latency is {round(bot.latency * 1000)}ms')

@bot.command()
async def hello(ctx: commands.Context):
    await ctx.send('Hi!')

@bot.command(name='lobotomize', help='clears memory')
async def lobotomize(ctx: commands.Context):
    reset_his()
    try:
        with open(Dictionary_storage, "w") as f:
            json.dump(Mssg_His, f)
        await ctx.send('lobotomized :wilted_rose:')
    except FileNotFoundError:
        await ctx.send("file gone.")

@bot.command(name='restart', help='restarts the bot')
async def bot_restart(ctx: commands.Context):
    await ctx.send('Restarting...')
    await ctx.send(bot_restart_now())


@bot.command(name='kill', help='stops the bot')
async def kill_bot(ctx: commands.Context):
    if ctx.author.id == 731417760927711232:
        await ctx.send('Stopping...')
        print(kill_my_bot())
    else:
        await ctx.send('Not iedla, no perms.')


@bot.command(name='server', help='finds Japan, Singapore, and Hong Kong Roblox servers e.g., !server "gameid" SG')
async def server(ctx: commands.Context, game_id: int, region: str):

    if region not in supported_countries:
        await ctx.send(f"Region not supported. Supported regions are: {supported_countries}")
        return

    await ctx.send(
        f"Searching for Japan, Singapore, or Hong Kong servers for game ID `{game_id}` with Region `{region}`... This might take a moment.")

    try:
        servers_returned = await main(cookie, game_id, region)
    except Exception as e:
        print(f"Error in finding servers: {e}")
        await ctx.send(
            f"An unexpected error occurred while fetching server data. Please try again later. Error: {e}")
        return

    if servers_returned:
        ctx.send(servers_returned)

    else:
        await ctx.send(f"No Japan, Singapore, or Hong Kong servers found for game ID `{game_id}` with the current filters.")




@bot.command(name='purge', help='Deletes a specified number of messages. Usage: !purge number')
@commands.has_permissions(manage_messages=True)
async def purge_messages(ctx: commands.Context, amount: int):

    user = ctx.author
    roles_with_perms = []
    for role in user.roles:
        if role.permissions.manage_messages:
            if amount <= 0:
                await ctx.send("Please specify a number greater than 0.", delete_after=5)
                return
            try:
                deleted = await ctx.channel.purge(limit=amount + 1)

                confirmation_message = await ctx.send(f"Successfully deleted {len(deleted) - 1} messages. (Excluding command)",
                                                      delete_after=5)
            except discord.Forbidden:
                await ctx.send("I don't have the necessary permissions to delete messages. Please grant me 'Manage Messages'.",
                               delete_after=10)
            except discord.HTTPException as e:
                await ctx.send(f"An error occurred while deleting messages: {e}", delete_after=10)
            except Exception as e:
                await ctx.send(f"An unexpected error occurred: {e}", delete_after=10)
        else:
            await ctx.send("You Dont have Perms for this action.", delete_after=10)




@bot.command(name='roleuser', help='Gives a role to a user.')
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role:
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("You don't have permissions for that, lil bro.")
            return
        if role >= ctx.guild.me.top_role:
            await ctx.send(f"No perms gang. {role.name} is too high up. :broken_heart:")
            return

        if role in member.roles:
            await ctx.send(f"{member.mention} already has the role {role.name}, you might be slow.")
        else:
            try:
                await member.add_roles(role)
                await ctx.send(f"Done gangalang, the role '{role.name}' has been given to {member.mention}.")
            except discord.Forbidden:
                await ctx.send("I don't have permissions for that for some reason.")
    else:
        await ctx.send(f"'{role_name}' not found. Look for a better one.")



@bot.command(name='freakseek', help='seek the freak')
async def freakseek(ctx):
    global Freak
    if Freak == True:
        await ctx.send("A convo is already active.",delete_after=10)
        return
    Freak = True
    await ctx.send("Summoning the Freak, this may take a moment")
    def check(m):
        return m.channel == ctx.channel and m.author != bot.user
    while True:
        try:
            message = await bot.wait_for('message', check=check, timeout=240)
            decoded_message = message.content.strip()
            user_disname = message.author.name
            if decoded_message.lower() == 'exit':
                Freak = False
                Exit(Mssg_His,is_gemini_history=False,freakseek=True)
                await ctx.send("Convo ended :broken_heart:")
                break

            Mssg_His.append({"role": "user", "content": f"{user_disname}: {decoded_message}"})
            model_response_text = await bot.loop.run_in_executor(
                None,
                lambda: freak_api_req(Mssg_His)
            )
            Mssg_His.append({"role": "assistant", "content": model_response_text})

            await ctx.send(model_response_text)
        except asyncio.TimeoutError:
            Freak = False
            Exit(Mssg_His, is_gemini_history=False,freakseek=True)
            await ctx.send("No one responded in time yall slow af.")
            break
        except Exception as e:
            Freak = False
            await ctx.send("Something went wrong so i died")
            print(e)
            Exit(Mssg_His, is_gemini_history=False,freakseek=True)
            break


@bot.command(name = 'todo', help='a todo list fuck you expect')
async def todo(ctx):
    lst_user = ctx.message.author
    lst_info = get_todolst(lst_user)
    await ctx.send(embed=todo_lst(lst_info,lst_user))

@bot.command(name='addtask',help='add a task')
async def addtask(ctx,task:str):
    lst_user = ctx.message.author
    lst_info = get_todolst(lst_user)
    await ctx.send(add_task(task,lst_info))
    await ctx.send(embed=todo_lst(lst_info, lst_user))
    save_todo(lst_info, lst_user)

@bot.command(name='savetasks',help='save tasks')
async def savetasks(ctx):
    lst_user = ctx.message.author
    lst_info = get_todolst(lst_user)
    await ctx.send(save_todo(lst_info,lst_user))
    await ctx.send(embed=todo_lst(lst_info, lst_user))
    save_todo(lst_info, lst_user)

@bot.command(name='deletetask',help='delete a task')
async def deltask(ctx):
    lst_user = ctx.message.author
    lst_info = get_todolst(lst_user)
    await ctx.send(del_task(lst_user))
    await ctx.send(embed=todo_lst(lst_info, lst_user))
    lst_info = []
    save_todo(lst_info, lst_user)

@bot.command(name='helpcourt',help='more info on courts')
async def helpcourt(ctx):
    await ctx.send('Usage: !court Crime defendant lawyer prosecutor. 3 phases, Defendent -> Prosecutor -> Defendant')


logger = logging.getLogger('court_bot')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename='court_session.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(console_handler)


@bot.command(name='court', help='sets up a court system. !help court for more info')
@commands.has_role('certified Judgeman')
async def court_command(ctx, Crime: str, defendant: discord.Member, lawyer: discord.Member, prosecutor: discord.Member):

    court_starter = ctx.author

    logger.info(f"Court command initiated by {ctx.author.display_name} ({ctx.author.id}) "
                f"in guild '{ctx.guild.name}' ({ctx.guild.id}), channel '{ctx.channel.name}' ({ctx.channel.id}).")
    logger.info(f"Crime: '{Crime}', Defendant: {defendant.display_name} ({defendant.id}), "
                f"Lawyer: {lawyer.display_name} ({lawyer.id}), Prosecutor: {prosecutor.display_name} ({prosecutor.id}).")

    defendant_role = discord.utils.get(ctx.guild.roles, name='Defendant')
    lawyer_role = discord.utils.get(ctx.guild.roles, name='Lawyer')
    prosecutor_role = discord.utils.get(ctx.guild.roles, name='Prosecutor')

    if not all([defendant_role, lawyer_role, prosecutor_role]):
        await ctx.send("One or more required roles (Defendant, Lawyer, Prosecutor) do not exist. Please create them.")
        logger.error("Missing required court roles.")
        return

    async def remove_court_roles():
        try:
            if defendant_role and defendant_role in defendant.roles:
                await defendant.remove_roles(defendant_role)
                logger.info(f"Removed {defendant_role.name} from {defendant.display_name}.")
            if lawyer_role and lawyer_role in lawyer.roles:
                await lawyer.remove_roles(lawyer_role)
                logger.info(f"Removed {lawyer_role.name} from {lawyer.display_name}.")
            if prosecutor_role and prosecutor_role in prosecutor.roles:
                await prosecutor.remove_roles(prosecutor_role)
                logger.info(f"Removed {prosecutor_role.name} from {prosecutor.display_name}.")
            await ctx.send("Court roles removed.")
            logger.info(f"Bot sent: 'Court roles removed.' to channel {ctx.channel.id}")
        except discord.Forbidden:
            await ctx.send("I don't have permissions to remove some roles. Please check my role hierarchy.")
            logger.error(f"Failed to remove roles due to permissions in channel {ctx.channel.id}.")
        except Exception as e:
            await ctx.send(f"An error occurred while removing roles: {e}")
            logger.error(f"An unexpected error occurred while removing roles in channel {ctx.channel.id}: {e}")

    try:
        await defendant.add_roles(defendant_role)
        await lawyer.add_roles(lawyer_role)
        await prosecutor.add_roles(prosecutor_role)
        await ctx.send(f"Roles assigned: {defendant.mention} as Defendant, {lawyer.mention} as Lawyer, {prosecutor.mention} as Prosecutor.")
        logger.info(f"Roles assigned: Defendant={defendant.display_name}, Lawyer={lawyer.display_name}, Prosecutor={prosecutor.display_name}.")
    except discord.Forbidden:
        await ctx.send("I don't have permissions to add roles. Please check my role hierarchy.")
        logger.error(f"Failed to add roles due to permissions in channel {ctx.channel.id}.")
        return

    asyncio.create_task(
        court_session_logic(ctx, Crime, defendant, lawyer, prosecutor, court_starter, remove_court_roles)
    )
    await ctx.send("Court session initiated in the background!")
    logger.info(f"Bot sent: 'Court session initiated in the background!' to channel {ctx.channel.id}")


async def court_session_logic(ctx, Crime, defendant, lawyer, prosecutor, court_starter, remove_court_roles_func):
    logger.info(f"Court session logic started for crime '{Crime}' in channel {ctx.channel.id}.")

    ai_message_history = []

    ai_message_history.append({"role": "system", "content": f"You are an impartial judge. A court session is taking place for the crime of '{Crime}'. "
                                                          f"The defendant is {defendant.display_name}, the lawyer is {lawyer.display_name}, and the prosecutor is {prosecutor.display_name}. "
                                                          f"Your task is to listen to the arguments and provide a verdict of 'Guilty' or 'Innocent' at the end. "
                                                          f"Before stating the verdict, you MUST provide a concise explanation of your reasoning. "
                                                          f"Your response should be structured as: 'Reasoning: [Your explanation here]\nVerdict: [Guilty/Innocent]'."})
    ai_message_history.append({"role": "assistant", "content": f"Court session for '{Crime}' has begun."})


    async def send_and_record(content: str, role: str = "assistant"):
        await ctx.send(content)
        ai_message_history.append({"role": role, "content": content})
        logger.info(f"Bot sent: '{content}' to channel {ctx.channel.id}")

    def court_channel_message_check(message: discord.Message):
        return message.channel == ctx.channel and not message.author.bot

    await send_and_record(f"{defendant.mention} is being brought to court for the crime of '{Crime}'")
    await asyncio.sleep(0.5)
    await send_and_record(f"{defendant.mention}'s lawyer will be {lawyer.mention} and the prosecutor will be {prosecutor.mention}")
    await asyncio.sleep(0.5)
    await send_and_record("The defendant will now appeal on why they shouldn't get the death penalty")
    await asyncio.sleep(0.5)
    await send_and_record("The judge can end/skip this phase by saying 'endphase' ")
    await asyncio.sleep(0.5)
    await send_and_record("The max time is 5 minutes per phase")

    async def run_phase(phase_name: str, timeout_seconds: int):
        await send_and_record(f"--- {phase_name} ---")

        end_phase_triggered = False
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout_seconds:
            try:
                message = await bot.wait_for(
                    'message',
                    check=court_channel_message_check,
                    timeout=max(0.1, timeout_seconds - (asyncio.get_event_loop().time() - start_time))
                )

                mapped_role = "user"
                sender_name = message.author.display_name

                if message.author.id == defendant.id:
                    content_for_ai = f"Defendant ({sender_name}): {message.content}"
                elif message.author.id == lawyer.id:
                    content_for_ai = f"Lawyer ({sender_name}): {message.content}"
                elif message.author.id == prosecutor.id:
                    content_for_ai = f"Prosecutor ({sender_name}): {message.content}"
                elif message.author.id == court_starter.id:
                    content_for_ai = f"Human Judge ({sender_name}): {message.content}"
                else:
                    content_for_ai = f"Spectator ({sender_name}): {message.content}"

                ai_message_history.append({
                    "role": mapped_role,
                    "content": content_for_ai
                })
                logger.info(f"COURT_MESSAGE [{message.author.display_name} ({message.author.id})]: {message.content}")


                if message.author.id == court_starter.id and message.content.lower() == 'endphase':
                    end_phase_triggered = True
                    logger.info(f"Judge ({court_starter.display_name}) triggered 'endphase' for {phase_name}.")
                    break

            except asyncio.TimeoutError:
                logger.warning(f"{phase_name} timed out waiting for a message.")
                break

            except Exception as e:
                logger.error(f"Error during {phase_name} message collection: {e}")
                break

        if not end_phase_triggered:
            await send_and_record(f"{phase_name} timed out. Moving On.")
        else:
            await send_and_record(f"{phase_name} ended by judge. Moving to next phase.")
        return end_phase_triggered

    await run_phase("Phase 1: Defendant Appeal", 300)
    await run_phase("Phase 2: Prosecutor Time", 300)
    await run_phase("Phase 3: Defense Rebuttal", 300)

    await send_and_record("All phases concluded. Consulting AI for verdict...")
    logger.info("All phases concluded. Preparing to send message history to AI for verdict.")

    ai_final_verdict = "Undetermined (AI Error)"
    ai_reasoning = "No reasoning provided by AI."
    try:
        ai_response_full = await judge_api_req(ai_message_history)
        logger.info(f"AI raw full response: '{ai_response_full}'")

        reasoning_match = re.search(r"Reasoning:\s*(.*?)\nVerdict:\s*(Guilty|Innocent)", ai_response_full, re.IGNORECASE | re.DOTALL)

        if reasoning_match:
            ai_reasoning = reasoning_match.group(1).strip()
            ai_verdict_processed = reasoning_match.group(2).strip().lower()

            if "guilty" in ai_verdict_processed:
                ai_final_verdict = "Guilty"
            elif "innocent" in ai_verdict_processed:
                ai_final_verdict = "Innocent"
            else:
                logger.error(f"AI verdict part unclear after regex match: '{reasoning_match.group(2)}'. Full response: '{ai_response_full}'")
                ai_final_verdict = "Undetermined (AI verdict part unclear)"
        else:
            logger.error(f"AI response did not match expected 'Reasoning:\\nVerdict:' format. Raw response: '{ai_response_full}'")
            ai_reasoning = "AI response format was unexpected."
            ai_final_verdict = "Undetermined (AI format error)"

        if ai_final_verdict.startswith("Undetermined") or ai_final_verdict.startswith("Error"):
            await send_and_record(f"AI's Verdict: **{ai_final_verdict.capitalize()}** :robot:\nReasoning: {ai_reasoning}")
        else:
            await send_and_record(f"AI's Verdict: **{ai_final_verdict.capitalize()}** :robot:\n\n**Reasoning:** {ai_reasoning}")

        logger.info(f"AI provided verdict: '{ai_final_verdict}' with reasoning: '{ai_reasoning}'.")

    except Exception as e:
        await send_and_record(f"An error occurred while getting AI verdict: {e}. Asking human judge for final verdict.")
        logger.error(f"Error calling AI for verdict: {e}")
        ai_final_verdict = "Error (Human Judge Required)"
        ai_reasoning = f"Error during AI call: {e}"

    if ai_final_verdict.startswith("Undetermined") or ai_final_verdict.startswith("Error"):
        await send_and_record("AI verdict was unclear or failed. Waiting for Human Judge to provide final verdict: 'Guilty' or 'Innocent'")
        try:
            verdict_message = await bot.wait_for(
                'message',
                check=lambda m: m.author.id == court_starter.id and m.channel == ctx.channel and m.content.lower() in ['guilty', 'innocent'],
                timeout=200
            )
            human_final_verdict = verdict_message.content.lower()
            await send_and_record(f"Human Judge's Final Verdict: **{human_final_verdict.capitalize()}** :wilted_rose:")
            logger.info(f"Human Judge ({court_starter.display_name}) issued final verdict: '{human_final_verdict.capitalize()}'.")
            final_verdict_to_use = human_final_verdict
        except asyncio.TimeoutError:
            await send_and_record("Human Judge did not provide a final verdict in time. Court session ending without a verdict.")
            logger.warning(f"Human Judge ({court_starter.display_name}) timed out on final verdict. Court session ending.")
            await remove_court_roles_func()
            return
    else:
        final_verdict_to_use = ai_final_verdict

    await send_and_record("Sentencing will now be discussed :broken_heart:")
    logger.info(f"Sentencing discussion initiated for verdict: '{final_verdict_to_use}'.")

    await send_and_record("Closing court.")
    logger.info(f"Court roles removal initiated for crime '{Crime}'.")
    await remove_court_roles_func()


async def judge_api_req(court_log: list) -> str:
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {venice_key}"
    }
    payload_dict = {
        "model": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "messages": court_log,
        "temperature": 0.1,
        "max_tokens": 250
    }

    try:
        result = await asyncio.to_thread(
            requests.post,
            api_url,
            headers=header,
            json=payload_dict,
            timeout=60
        )
        result.raise_for_status()
        response_data = result.json()
        ai_response_text = "No text generated by the model."
        if 'choices' in response_data and len(response_data['choices']) > 0:
            if 'message' in response_data['choices'][0] and 'content' in response_data['choices'][0]['message']:
                ai_response_text = response_data['choices'][0]['message']['content']
                ai_response_text = re.sub(r'<think>.*?</think>', '', ai_response_text, flags=re.DOTALL)
                ai_response_text = ai_response_text.strip()
        return ai_response_text
    except requests.exceptions.RequestException as e:
        return f"Undetermined (API request error) {e}"
    except Exception as e:
        return f"Undetermined (Unexpected error) {e}"













@bot.tree.command(name="weather", description="weather NOW")
@app_commands.describe(city="The name of the CITY (e.g., London, New York)")
async def current_weather_command(interaction: discord.Interaction, city: str):
    await interaction.response.defer()
    result = weather_thing(city,Weather_API)
    await interaction.followup.send(result)

@bot.tree.command(name="weather_forcast", description="Weather LATER")
@app_commands.describe(city="The name of the CITY (e.g., London, New York)")
async def weather_forcast_command(interaction: discord.Interaction, city: str):
    await interaction.response.defer()
    result = weather_forecast(city,Weather_API)
    await interaction.followup.send(result)

def toggle_on():
    return "python main_bot.py"

def run_bot_api():
    try:
        print(f"Bot API: Attempting to start Flask API on port {API_PORT}...")
        bot_api_app.run(host='127.0.0.1', port=API_PORT, debug=False, use_reloader=False)
        print(f"Bot API: Flask API on port {API_PORT} stopped.")
    except Exception as e:
        print(f"Bot API: Failed to start Flask API: {e}")


if __name__ == '__main__':
    api_thread = threading.Thread(target=run_bot_api)
    api_thread.daemon = True
    api_thread.start()
    time.sleep(2)
    print("Attempting to run Discord bot...")
    try:
        bot.run(Bot_Token)
    except Exception as e:
        print(f"Failed to start Discord bot: {e}")
