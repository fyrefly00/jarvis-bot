# bot.py: Master branch: testing edit
import os
import discord
from dotenv import load_dotenv
import requests
import json
import random
import time
import sqlite3
from discord.ext import commands

#Weather API token
TOKEN = "NzE0OTcwNzU2NjA1NTQyNDgx.Xs2egw.xjKqcAdP55okLQ7zm5nBGXMUzjY"


#Load the database
conn = sqlite3.connect('users.db')
c = conn.cursor()

#Uncomment to regen database
# c.execute('''CREATE TABLE data 
#                 (name text, balance real, vibes real)''')


# Bot commmands
bot = commands.Bot(command_prefix='!')

#Diagnostics
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='helloworld', help="Really? Do you actually need a description for what this does?")
async def helloworld(ctx):
    response = "Hello, world!"
    await ctx.send(response)

#Should be deprecated, hopefully
@bot.command(name='register', help='Registers account for lembas and vibes')
async def register(ctx):
    name = str(ctx.author.id)
    c.execute("INSERT INTO data VALUES (?,?,?)", (name, 10.0, 10.0))
    conn.commit()
    await ctx.send(name + "'s account registered!")


#Currency
@bot.command(name='balance', help='Prints current balance of lembas')
async def balance(ctx):
    t = (str(ctx.author.id),)
    c.execute('SELECT * FROM data WHERE name=?', t)
    result = c.fetchone()
    if result:
        output = "BALANCE: Lembas: " + str(result[1]) + " Vibes: " + str(result[2])
        await ctx.send(output)


#Leaderboard: scans all users and sorts by number of vibes
@bot.command(name='leaderboard', help="Prints vibe leaders")
async def leaderboard(ctx):
    c.execute('SELECT * FROM data')
    rank = []
    for row in c:
        rank.append([row[0], row[2]])
    rank = sorted(rank, key=lambda x: x[1], reverse=True)
    output = ""
    for count,item in enumerate(rank):
        # await ctx.fetch_user(item[0])
        user = bot.get_user(int(item[0]))
        output += str(count+1) + ": " + user.name + ": Vibes: " + str(item[1]) + "\n"
    await ctx.send("```" + output + "```")


# Needs to properly take IDs to not break on line 156
@bot.command(name='pay', help='Pay another user some lembas')
async def pay(ctx, user , val : int):
    # c.execute("UPDATE data SET balance = ? WHERE name = ?", (1000.0, str(ctx.author.id)))

    payer = str(ctx.author.id)
    c.execute('SELECT * FROM data WHERE name=? ', (payer,))
    payer_data = c.fetchone()
    if(val<=payer_data[1] and payer_data[1] > 0):
        payee =  bot.get_user(int(str(user)[3:len(user)-1]))
        c.execute('SELECT * FROM data WHERE name=? ', (str(payee.id),))
        if c:
            payee_data = c.fetchone()
            c.execute("UPDATE data SET balance = ? WHERE name = ?", (payee_data[1] + val, (str(payee.id))))
            c.execute("UPDATE data SET balance = ? WHERE name = ?", ( payer_data[1] - val, (str(ctx.author.id))))
            conn.commit()
            c.execute('SELECT * FROM data WHERE name=? ', (payer,))
            payer_data = c.fetchone()
            await ctx.send("Transfered " + str(val) + " lembas to " + payee.name)

#Vibe-checker: reuses active vibe-checker logic but with support for a specific user
@bot.command(name='vcheck', help='Vibe check another user')
async def vcheck(ctx, user):
    t = (str(bot.get_user(int(str(user)[3:len(user)-1])).id),)
    c.execute('SELECT * FROM data WHERE name=?', t)
    if c:
        result = c.fetchone()
        vibes = result[2]
        lembas= result[1]
        await ctx.channel.send("Vibe Check in Progress...")
        time.sleep(1)
        val = random.getrandbits(1)
        if val:
            await ctx.channel.send("Vibe Check Passed. Vibes Added.")
            vibes +=1
        else:
            await ctx.channel.send("Vibe Check Failed. Vibes Removed")
            vibes-=1
        c.execute("UPDATE data SET vibes = ? WHERE name = ?", (vibes, str(bot.get_user(int(str(user)[3:len(user)-1])).id)))
        conn.commit()
    else:
        await ctx.channel.send("Vibe Check in Progress...")
        time.sleep(1)
        val = random.getrandbits(1)
        if val:
            await ctx.channel.send("Vibe Check Passed. Vibes Added.")
            
        else:
            await ctx.channel.send("Vibe Check Failed. Vibes Removed")

#Wishing Well
@bot.command(name='wishingwell', help='Toss some lembas in to earn vibes. 5 Lembas = 1 Vibe')
async def wishingwell(ctx, value):
    payer = str(ctx.author.id)
    c.execute('SELECT * FROM data WHERE name=? ', (payer,))
    payer_data = c.fetchone()
    # c.execute("UPDATE data SET balance = ? WHERE name = ?", (100.0, str(ctx.author.id)))

    if int(value)  != 5:
        await ctx.channel.send("Please pay only 5 lembas")
        return
    if(int(value) <= payer_data[2]):
        winnings = float(int(random.choice(range(0, 3))))
        c.execute("UPDATE data SET vibes = ? WHERE name = ?", (winnings + payer_data[2], str(ctx.author.id)))
        c.execute("UPDATE data SET balance = ? WHERE name = ?", (payer_data[1] - 5, str(ctx.author.id)))
        conn.commit
        await ctx.channel.send("You recieved " + str(winnings) + " vibes!")
    else:
        await ctx.channel.send("Insuffecient Lembas!")
      

#Fun / Utils
@bot.command(name='weather', help='Enter the name of a city in the form !weather <city>')
async def weather(ctx, city):
    weather_key = "75bf0e2952a905a38b363afc6d605391"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + weather_key + "&q=" + city
    print(complete_url)
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404": 
        y = x["main"] 
        current_temperature = y["temp"] 
        z = x["weather"] 
        weather_description = z[0]["description"] 
        current_temperature = round((current_temperature * (9/5)) -459.67,2)
        await ctx.send("Weather in " + city + "\nTemperature: " + str(current_temperature) + "°F" + "\n Weather: " + str(weather_description))
    
    else: 
        print(" City Not Found ") 
        await ctx.send("Sorry boss... I'm not seeing that city in my database")


@bot.command(name='roll_dice', help='Simulates rolling dice. Enter <number of dice> and <number of sides>')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))    

@bot.command(name='8ball', help='Ask a question, get an answer. Simple as that')
async def eightball(ctx, question):
    RESPONSES = ["Absolutely!", "Not at all!", "Never!", "You can count on it!", "Hell no!", "Yes", "No", "For sure!", "You know it, boss =)", "HELL no", "Not too sure about that one, boss", "Can't say for sure", "I wouldn't count on it", "Nope"]
    if(question.strip() != ""):
        await ctx.channel.send(RESPONSES[int(random.choice(range(0, len(RESPONSES))))])



#Events
@bot.event
async def on_message(message):
    
    #Make sure the message author isn't the bot to prevent feedback loops
    if message.author == bot.user:
        return

    #Auto-register function (might be broken)
    c.execute("SELECT * FROM data WHERE name=?",(str(message.author.id),))
    if not c:
        c.execute("INSERT INTO data VALUES (?,?,?)", (str(message.author.id), 0.0, 0.0))
        conn.commit()
        await ctx.send(message.author.name + "'s account registered!")

    #Message searching sub-routine
    message_text = message.content.casefold()
    #Auto vibe-checker
    if "vibe" in message_text or "vibin" in message_text or "vibing" in message_text:
        
        #Checks if the user has an account from which to subtract vibes.
        t = (str(message.author.id),)
        c.execute('SELECT * FROM data WHERE name=?', t)
        if c:
            result = c.fetchone()
            vibes = result[2]
            lembas= result[1]
            await message.channel.send("Vibe Check in Progress...")
            time.sleep(1)
            val = random.getrandbits(1)
            if val:
                await message.channel.send("Vibe Check Passed. Vibes Added.")
                vibes +=1
            else:
                await message.channel.send("Vibe Check Failed. Vibes Removed")
                vibes-=1
            c.execute("UPDATE data SET vibes = ? WHERE name = ?", (vibes, str(message.author.id)))
            conn.commit()
        else:
            await message.channel.send("Vibe Check in Progress...")
            time.sleep(1)
            val = random.getrandbits(1)
            if val:
                await message.channel.send("Vibe Check Passed. Vibes Added.")
                
            else:
                await message.channel.send("Vibe Check Failed. Vibes Removed")

    await bot.process_commands(message)


bot.run(TOKEN)
conn.commit()
conn.close()

