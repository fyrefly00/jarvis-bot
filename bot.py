# bot.py
import os
import discord
from dotenv import load_dotenv
import requests
import json
import random
import time
import sqlite3
conn = sqlite3.connect('users.db')
# import shlex, subprocess
# import sys

load_dotenv()
TOKEN = "NzE0OTcwNzU2NjA1NTQyNDgx.Xs2egw.xjKqcAdP55okLQ7zm5nBGXMUzjY"


from discord.ext import commands

c = conn.cursor()
# c.execute('''CREATE TABLE data 
#                 (name text, balance real, vibes real)''')








# Bot commmands
bot = commands.Bot(command_prefix='!')
#command_prefix='!'

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='helloworld', help="Really? Do you actually need a description for what this does?")
async def helloworld(ctx):
    response = "Hello, world!"
    await ctx.send(response)


@bot.command(name='roll_dice', help='Simulates rolling dice. Enter <number of dice> and <number of sides>')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


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
        # print following values 
        # print("Weather in " + city + "\nTemperature: " + str(current_temperature) + "°F" + "\n Weather: " + str(weather_description)) 
        await ctx.send("Weather in " + city + "\nTemperature: " + str(current_temperature) + "°F" + "\n Weather: " + str(weather_description))
    
    else: 
        print(" City Not Found ") 
        await ctx.send("Sorry boss... I'm not seeing that city in my database")


@bot.event
async def on_message(message):
    # print("ID " +  str(message.author.id))
    # print(message.content.casefold()[0:10])
    if message.author == bot.user:
        # print("ignoring")
        # return
        return
        # await bot.process_commands(message)

    c.execute("SELECT * FROM data WHERE name=?",(str(message.author.id),))
    if not c:
        c.execute("INSERT INTO data VALUES (?,?,?)", (str(message.author.id), 0.0, 0.0))
        conn.commit()
        await ctx.send(message.author.name + "'s account registered!")

    message_text = message.content.casefold()
    if "vibe" in message_text or "vibin" in message_text or "vibing" in message_text:
        
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
            # c.execute("INSERT INTO data VALUES (?,?,?)", (name,lembas, vibes))
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




@bot.command(name='balance', help='Prints current balance of lembas')
async def balance(ctx):
    print("REALID" + str(ctx.author.id))
    # print(str(ctx.author))
    t = (str(ctx.author.id),)
    c.execute('SELECT * FROM data WHERE name=?', t)
    result = c.fetchone()
    if result:
        output = "BALANCE: Lembas: " + str(result[1]) + " Vibes: " + str(result[2])
        await ctx.send(output)


#Might be broken
@bot.command(name='leaderboard', help="Prints vibe leaders")
async def leaderboard(ctx):
    c.execute('SELECT * FROM data')
    rank = []
    for row in c:
        # print(row[2])
        rank.append([row[0], row[2]])
    rank = sorted(rank, key=lambda x: x[1], reverse=True)
    output = ""
    for count,item in enumerate(rank):
        # await ctx.fetch_user(item[0])
        user = bot.get_user(int(item[0]))
        print(user.name)
        # print(count)
        # print(item)
        output += str(count+1) + ": " + user.name + ": Vibes: " + str(item[1]) + "\n"
    await ctx.send("```" + output + "```")

@bot.command(name='register', help='Registers account for lembas and vibes')
async def register(ctx):
    name = str(ctx.author.id)

    
    c.execute("INSERT INTO data VALUES (?,?,?)", (name, 10.0, 10.0))
    conn.commit()
    await ctx.send(name + "'s account registered!")


# Needs to properly take IDs to not break on line 156
@bot.command(name='pay', help='Pay another user some lembas')
async def pay(ctx, user , val : int):
    payer = str(ctx.author.id)
    c.execute('SELECT * FROM data WHERE name=? ', (payer,))
    payer_data = c.fetchone()
    print(payer_data[1])
    if(val<=payer_data[1]):
        payee =  bot.get_user(int(str(user)[3:len(user)-1]))
        print(payee.name)
        c.execute('SELECT * FROM data WHERE name=? ', (str(payee.id),))
        if c:
            payee_data = c.fetchone()
            print(payee_data[1])
            print(str(payee.id))
            print (payee.id)
            print(ctx.author.id)
            print(str(ctx.author.id))
            new_balance = payee_data[1] + val 
            old_balance = payer_data[1] - val
            c.execute("UPDATE data SET balance = ? WHERE name = ?", (new_balance , str(payee.id)))
            # c.execute("UPDATE data SET vibes = ? WHERE name = ?", (vibes, str(message.author.id)))

            conn.commit()

            c.execute("UPDATE data SET balance = ? WHERE name = ?", (old_balance, str(ctx.author.id)))
            c.execute('SELECT * FROM data WHERE name=? ', (payer,))
            payer_data = c.fetchone()
            print("new balance" + str(payer_data[1]))
            await ctx.send("Transfered " + str(val) + " lembas to " + payee.name)

@bot.command(name='vcheck', help='Vibe check another user')
async def vcheck(ctx, user):
    t = (str(bot.get_user(int(str(user)[3:len(user)-1])).id),)
    c.execute('SELECT * FROM data WHERE name=?', t)
    if c:
        print("yes, c")
        print(t)
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
        # c.execute("INSERT INTO data VALUES (?,?,?)", (name,lembas, vibes))
        c.execute("UPDATE data SET vibes = ? WHERE name = ?", (vibes, str(bot.get_user(int(str(user)[3:len(user)-1])).id)))
        conn.commit()
        print("vibes updated")
    else:
        await ctx.channel.send("Vibe Check in Progress...")
        time.sleep(1)
        val = random.getrandbits(1)
        if val:
            await ctx.channel.send("Vibe Check Passed. Vibes Added.")
            
        else:
            await ctx.channel.send("Vibe Check Failed. Vibes Removed")

    
    
    # # user = str(user[1:])
    # # print(user.id)
    # t = (str(ctx.author.id),)
    # c.execute('SELECT * FROM data WHERE name=?', t)
    # payer_lembas = c.fetchone()[1]
    # if(payer_lembas >=val):
    #     payee = (user[2:])
    #     print(payee)
    #     c.execute('SELECT * FROM data WHERE name=?', (payee,))
    #     if c:
    #         payee_bal = c.fetchone()
    #         print(payee_bal)
    #         c.execute("UPDATE data SET vibes = ? WHERE name = ?", (payee_bal[2] + val, payee))
    #         c.execute("UPDATE data SET vibes = ? WHERE name = ?", (player_lembas - val , str(ctx.author)))
    #         await ctx.send("Transfered " + val + " lembas to " + user)
    #     else:
    #         await ctx.send("User " + user + " not found")
    # else:
    #     await ctx.send("Insuffecient lembas for this transaction")
    # conn.commit()





bot.run(TOKEN)
conn.commit()
conn.close()
# client.run(TOKEN)
