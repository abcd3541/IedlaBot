import discord , requests , json , random, asyncio, subprocess,re
from Fetch_thing import get_bot_token, get_gem_key, get_Weather_key
from Supporting_stuff import reset_his, auto_loader_freak, auto_loader_gemini, Json_storage, weather_sorting, weather_thing, weather_forecast, \
    freak_api_req, Gemini_api_req, Exit, auto_loader_gemini
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
gemini = False
Mssg_His = reset_his()
Dictionary_storage = "Dictionary_storage_Freaky.json"
Gem_Dictionary_storage = "Dictionary_storage_gemini.json"
GEM_Mssg_His = [
    {"role": "user", "parts": [{"text": "Hello!"}]},
    {"role": "model", "parts": [{"text": "Hello!"}]}
]

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

Json_storage(Mssg_His,GEM_Mssg_His)
GEM_Mssg_His = auto_loader_gemini(GEM_Mssg_His)
Mssg_His = auto_loader_freak(Mssg_His)


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
        await ctx.send('Bonked :wilted_rose:')
    except FileNotFoundError:
        await ctx.send("file gone.")


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
                Exit(GEM_Mssg_His,is_gemini_history=True)
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
            Exit(GEM_Mssg_His,is_gemini_history=True)
            break
        except Exception as e:
            await ctx.send("Something went wrong so i died :(")
            print(e)
            Exit(GEM_Mssg_His, is_gemini_history=True)
            break

@bot.command(name='freakseek', help='freaky. exit to exit')
async def freakseek(ctx):
    global Freak
    if Freak == True:
        await ctx.send("A convo is already active.",delete_after=10)
        return
    Freak = True
    await ctx.send("Calling Freakseek")
    await ctx.send(":speaking_head::fire::fire::fire:")
    def check(m):
        return m.channel == ctx.channel and m.author != bot.user
    while True:
        try:
            message = await bot.wait_for('message', check=check, timeout=240)
            decoded_message = message.content.strip()
            user_disname = message.author.name
            if decoded_message.lower() == 'exit':
                Exit(Mssg_His,is_gemini_history=False)
                await ctx.send("Convo ended :broken_heart:")
                break

            Mssg_His.append({"role": "user", "content": f"{user_disname}: {decoded_message}"})
            model_response_text = await bot.loop.run_in_executor(
                None,
                lambda: freak_api_req(Mssg_His)
            )
            if model_response_text != "We do not appericiate this content":
                Mssg_His.append({"role": "assistant", "content": model_response_text})


            await ctx.send(model_response_text)
        except asyncio.TimeoutError:
            await ctx.send("No one responded in time yall slow af.")
            Exit(Mssg_His, is_gemini_history=False)
            break
        except Exception as e:
            await ctx.send("Something went wrong so i died :(")
            print(e)
            Exit(Mssg_His, is_gemini_history=False)
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



if __name__ == "__main__":
    bot.run(Bot_Token)
