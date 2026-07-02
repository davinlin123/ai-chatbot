from google import genai
import os
from google.genai import errors
import discord
from datetime import datetime
from google.genai import types

gemini_client = genai.Client(api_key=os.environ["API_KEY"])
token = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)


config = types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])

@discord_client.event
async def on_ready():
    print(f'Logged in as {discord_client.user}')
    
@discord_client.event
async def on_message(message):
    
    if message.author == discord_client.user:
        return
    
    try:
        async with message.channel.typing():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            question = message.content
            if "time" in question.lower() or "date" in question.lower():
                question = f"Current time: {now}\nUser: {message.content}"
                
            response = gemini_client.models.generate_content(model="gemini-2.5-flash",contents=question,config=config)
            await message.channel.send(response.text)
        
    except errors.ServerError as e:
        await message.channel.send(f"Gemini is currently busy, try again later. (error {e.code})")
        
    except errors.APIError as e:
        await message.channel.send(e.code)
        await message.channel.send(e.message)
        
discord_client.run(token)
