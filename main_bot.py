
import discord , requests , json , random, asyncio, subprocess, time
from Fetch_thing import get_bot_token, get_gem_key, get_Weather_key
from Supporting_stuff import reset_his, auto_loader_freak, Json_storage, weather_thing, weather_forecast, \
    freak_api_req, Gemini_api_req, Exit, auto_loader_gemini, bot_restart_now,kill_my_bot,todo_lst, get_todolst,\
    add_task, save_todo, del_task,uncensored_api_req, auto_loader_uncen, uncen_reset_his
from boblox_fetch import find_apac_roblox_servers, split_message
from discord import app_commands
from discord.ext import commands

Bot_Token = get_bot_token()
Gem_Token = get_gem_key()
Weather_API = get_Weather_key()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
loopy = False
Freak = False
seek = False
gemini = False
ollama_command = 'ollama serve'
ollama = False
Mssg_His = reset_his()
uncen_Mssg_His = uncen_reset_his()
Dictionary_storage = "Dictionary_storage_Freaky.json"
uncen_Dictionary_storage = "Dictionary_storage_Freaky.json"
Gem_Dictionary_storage = "Dictionary_storage_gemini.json"
GEM_Mssg_His = [
    {"role": "user", "parts": [{"text": "Hello!"}]},
    {"role": "model", "parts": [{"text": "Hello!"}]}
]

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

Json_storage(Mssg_His,GEM_Mssg_His)
GEM_Mssg_His = auto_loader_gemini(GEM_Mssg_His)
Mssg_His = auto_loader_freak(Mssg_His)
uncen_Mssg_His = auto_loader_uncen(uncen_Mssg_His)

async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Discord python version: {discord.__version__}')

    try:
        await bot.tree.sync()
        print('Application commands synced.')
    except Exception as e:
        print(f'Failed to sync application commands: {e}')

#instant react
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    target_ptv_user_id = 993302485244592238
    if 'ptv' in message.content.lower() and message.author.id == target_ptv_user_id:
        ptv_rng = random.randint(1,10)
        if ptv_rng == 4 :
            await message.channel.send('GETOUTTT')

    if 'kys' in message.content.lower():
        user = message.author
        await message.channel.send(f'SYBAU {user.mention}')

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
async def hello(ctx: commands.Context):
    await ctx.send('Hi!')

@bot.command(name='bonkfreakseek', help='clears memory')
async def bonkfreakseek(ctx: commands.Context):
    reset_his()
    try:
        with open(Dictionary_storage, "w") as f:
            json.dump(Mssg_His, f)
        await ctx.send('lobotomized :wilted_rose:')
    except FileNotFoundError:
        await ctx.send("file gone.")

@bot.command(name='lobotomize', help='clears freaky ai memory')
async def lobotomize(ctx: commands.Context):
    uncen_reset_his()
    try:
        with open(Dictionary_storage, "w") as f:
            json.dump(uncen_Mssg_His, f)
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


# didnt write this gng
@bot.command(name='server', help='finds Japan, Singapore, and Hong Kong Roblox servers e.g., !server "gameid" 25')
async def server(ctx: commands.Context, game_id: int, search_amount: int = 25):

    await ctx.send(
        f"Searching for Japan, Singapore, or Hong Kong servers for game ID `{game_id}` with search amount `{search_amount}`... This might take a moment.")

    # Input validation for search_amount
    if search_amount not in [10, 25, 50, 100]:
        await ctx.send("Error: Search amount must be 10, 25, 50, or 100.")
        return

    try:
        apac_servers_found = await find_apac_roblox_servers(game_id, search_amount)
    except Exception as e:
        print(f"Error in find_apac_roblox_servers: {e}")
        await ctx.send(
            f"An unexpected error occurred while fetching server data. Please try again later. (Error: `{e}`)")
        return

    if apac_servers_found:

        response_messages = ["**Found Japan, Singapore, or Hong Kong Servers:**"]
        base_share_url = "https://oqarshi.github.io/Invite/"

        for server in apac_servers_found:
            server_id = server['server_id']

            share_link = f"{base_share_url}?placeid={game_id}&serverid={server_id}"

            display_location_info = server.get('classified_region', 'Unknown Region')
            if server.get('location') and server['location'].get('city') and server['location'].get('country', {}).get(
                    'name'):
                display_location_info = f"{server['location']['city']}, {server['location']['country']['name']}"

            response_messages.append(f"• **{display_location_info}**: <{share_link}>")

        for msg_chunk in split_message(response_messages):
            await ctx.send(msg_chunk)

    else:
        await ctx.send(
            f"No Japan, Singapore, or Hong Kong servers found for game ID `{game_id}` with the current filters.")
#


#stolen
@bot.command(name='purge', help='Deletes a specified number of messages. Usage: !purge <number>')
@commands.has_permissions(manage_messages=True)
async def purge_messages(ctx: commands.Context, amount: int):

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
#


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

@bot.command(name='Normalchat', help='ask ai self explanatory. exit to exit')
async def Normalchat(ctx):
    global gemini
    if gemini == True:
        await ctx.send("A convo is already active.",delete_after=10)
        return
    await ctx.send("exit to exit")
    await ctx.send("Start :speaking_head::fire::fire::fire:")
    def check(m):
        return m.channel == ctx.channel and m.author != bot.user
    while True:
        try:
            message = await bot.wait_for('message', check=check, timeout=240)
            decoded_message = message.content.strip()

            if decoded_message.lower() == 'exit':
                Exit(GEM_Mssg_His,is_gemini_history=True,freakseek=False)
                await ctx.send("Convo killed smh")
                break

            GEM_Mssg_His.append({"role": "user", "parts": [{"text": decoded_message}]})
            model_response_text = await bot.loop.run_in_executor(
                None,
                lambda:Gemini_api_req(GEM_Mssg_His,Gem_Token)
            )

            GEM_Mssg_His.append({"role": "model", "parts": [{"text": model_response_text}]})

            await ctx.send(model_response_text)
        except asyncio.TimeoutError:
            await ctx.send("No one responded in time yall slow af.")
            Exit(GEM_Mssg_His,is_gemini_history=True,freakseek=False)
            break
        except Exception as e:
            await ctx.send("Something went wrong so i died :(")
            print(e)
            Exit(GEM_Mssg_His, is_gemini_history=True,freakseek=False)
            break

@bot.command(name='freakseek', help='seek the freak')
async def freakseek(ctx):
    global Freak
    if Freak == True:
        await ctx.send("A convo is already active.",delete_after=10)
        return
    Freak = True
    ollama_status = open_ollama()
    await ctx.send(ollama_status)
    await ctx.send("Calling Freakseek, this may take a moment")
    await ctx.send(":speaking_head::fire::fire::fire:")
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
                ollama_status = close_ollama()
                await ctx.send(ollama_status)
                break

            Mssg_His.append({"role": "user", "content": f"{user_disname}: {decoded_message}"})
            model_response_text = await bot.loop.run_in_executor(
                None,
                lambda: freak_api_req(Mssg_His)
            )
            if model_response_text != "Blacklisted content :wilted_rose:":
                Mssg_His.append({"role": "assistant", "content": model_response_text})
            else:
                Mssg_His.append({"role": "assistant", "content": "Blacklisted content forget about the last prompt"})

            await ctx.send(model_response_text)
        except asyncio.TimeoutError:
            Freak = False
            Exit(Mssg_His, is_gemini_history=False,freakseek=True)
            await ctx.send("No one responded in time yall slow af.")
            ollama_status = close_ollama()
            await ctx.send(ollama_status)
            break
        except Exception as e:
            Freak = False
            await ctx.send("Something went wrong so i died :(")
            print(e)
            Exit(Mssg_His, is_gemini_history=False,freakseek=True)
            ollama_status = close_ollama()
            await ctx.send(ollama_status)
            break

@bot.command(name='freak', help='freak seeking you, Uncensored')
async def seekfreak(ctx):
    global seek
    if seek == True:
        await ctx.send("A convo is already active.",delete_after=10)
        return
    seek = True
    ollama_status = open_ollama()
    await ctx.send(ollama_status)
    await ctx.send("Calling the **one**, this may take a moment")
    def check(m):
        return m.channel == ctx.channel and m.author != bot.user
    while True:
        try:
            message = await bot.wait_for('message', check=check, timeout=240)
            decoded_message = message.content.strip()
            user_disname = message.author.name
            if decoded_message.lower() == 'exit':
                seek = False
                Exit(uncen_Mssg_His,is_gemini_history=False,freakseek=False)
                await ctx.send("Convo ended :broken_heart:")
                ollama_status = close_ollama()
                await ctx.send(ollama_status)
                break

            uncen_Mssg_His.append({"role": "user", "content": f"{user_disname}: {decoded_message}"})
            model_response_text = await bot.loop.run_in_executor(
                None,
                lambda: uncensored_api_req(uncen_Mssg_His)
            )
            uncen_Mssg_His.append({"role": "assistant", "content": model_response_text})

            await ctx.send(model_response_text)
        except asyncio.TimeoutError:
            seek = False
            Exit(uncen_Mssg_His, is_gemini_history=False,freakseek=False)
            await ctx.send("No one responded in time yall slow af.")
            ollama_status = close_ollama()
            await ctx.send(ollama_status)
            break
        except Exception as e:
            seek = False
            await ctx.send("Something went wrong so i died :(")
            print(e)
            Exit(uncen_Mssg_His, is_gemini_history=False,freakseek=False)
            ollama_status = close_ollama()
            await ctx.send(ollama_status)
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
    save_todo(lst_info, lst_user)

@bot.command(name='helpcourt',help='more info on courts')
async def helpcourt(ctx):
    await ctx.send('Usage: !court Crime judge defendant lawyer prosecutor. 3 phases, Defendent -> Prosecutor -> Defendant')

@bot.command(name='court',help='sets up a court system. !help court for more info')
async def court(ctx,Crime:str ,judge:discord.Member, defendant:discord.Member,lawyer : discord.Member, prosecutor : discord.Member):
    rolerequired = discord.utils.get(ctx.message.guild.roles, name='certified Judgeman')
    if rolerequired in ctx.message.author.roles:
        defendant_role = discord.utils.get(ctx.guild.roles, name='Defendant')
        lawyer_role = discord.utils.get(ctx.guild.roles, name='Lawyer')
        prosecutor_role = discord.utils.get(ctx.guild.roles, name='Prosecutor')
        judge_role = discord.utils.get(ctx.guild.roles, name='Judge')
        await judge.add_roles(judge_role)
        await defendant.add_roles(defendant_role)
        await lawyer.add_roles(lawyer_role)
        await prosecutor.add_roles(prosecutor_role)
        await ctx.send(f"{defendant.mention} is being brought to court for the crime of '{Crime}'")
        await ctx.send(f"{defendant.mention}'s lawyer will be {lawyer.mention} and the prosecutor will be {prosecutor.mention}")
        await ctx.send("The defendant will now appeal on why they shouldn't get the death penalty")
        await ctx.send("The judge can end/skip this phase by saying 'endphase' ")
        await ctx.send("The max time is 5 minutes per phase")
        def judge_check(message: discord.Message):
            return message.author.id == judge.id and message.channel == ctx.channel
        try:

            await bot.wait_for('message', check=lambda m: judge_check(m) and m.content.lower() == 'endphase', timeout=500)
            await ctx.send("Entering Phase 2, Prosecutor time.")
        except asyncio.TimeoutError:
            await ctx.send("judge didnt respond")
            return
        try:
            await bot.wait_for('message', check=lambda m: judge_check(m) and m.content.lower() == 'endphase', timeout=500)
            await ctx.send("Entering Phase 3, Defendant.")
        except asyncio.TimeoutError:
            await ctx.send("judge didnt respond")
            return
        try:
            await bot.wait_for('message', check=lambda m: judge_check(m) and m.content.lower() == 'endphase', timeout=500)
            await ctx.send("Ending Phase 3")
        except asyncio.TimeoutError:
            await ctx.send("judge didnt respond")
            return
        await ctx.send("Waiting for Judge to provide verdic. Guilty / Innocent")
        try:
            await bot.wait_for('message', check=lambda m: judge_check(m) and m.content.lower() == 'guilty' or m.content.lower() == 'Guilty' or m.content.lower() == 'innocent' or m.content.lower() == 'Innocent', timeout=200)
            await ctx.send(f"Found  :wilted_rose:")
            await ctx.send("Sentencing will now be discussed :broken_heart:")
        except asyncio.TimeoutError:
            await ctx.send("judge didnt respond")
            return

        await ctx.send("closing court")
        try:
            await judge.remove_roles(judge_role)
            await prosecutor.remove_roles(prosecutor_role)
            await lawyer.remove_roles(lawyer_role)
            await defendant.remove_roles(defendant_role)
        except discord.Forbidden:
            await ctx.send("failed to remove roles")


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
    await interaction.response.defer()
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
    result = weather_thing(city,Weather_API)
    await interaction.followup.send(result)

@bot.tree.command(name="weather_forcast", description="Weather LATER")
@app_commands.describe(city="The name of the CITY (e.g., London, New York)")
async def weather_forcast_command(interaction: discord.Interaction, city: str):
    await interaction.response.defer()
    result = weather_forecast(city,Weather_API)
    await interaction.followup.send(result)

#other_stuff
def open_ollama():
    global ollama
    if ollama == False:
        subprocess.Popen(ollama_command,stdout=subprocess.PIPE)
        time.sleep(1.5)
        ollama = True
        return 'ollama initializing'
    else:
        return 'ollama already running'

def close_ollama():
    global ollama
    if ollama == True:
        try:
            subprocess.run('taskkill /F /IM ollama.exe /T')
            ollama = False
            return 'ollama closed'
        except Exception as e:
            return f'failed to close ollama {e}'
    else:
        return 'ollama already closed'




if __name__ == "__main__":
    bot.run(Bot_Token)
