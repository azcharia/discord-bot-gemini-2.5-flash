# bot.py
import discord
import google.generativeai as genai
import os

# Get API keys and tokens from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Choose the Gemini model
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

# Initialize Discord client with appropriate intents
intents = discord.Intents.default()
intents.message_content = True # Required to read message content
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Process the message using Gemini API
    try:
        print(f'Received message: {message.content}')
        response = model.generate_content(message.content)
        print(f'Gemini response: {response.text}')
        # Send the response back to the channel
        await message.channel.send(response.text)
    except Exception as e:
        print(f'An error occurred: {e}')
        await message.channel.send('Maaf, terjadi kesalahan saat memproses permintaan Anda.')

# Run the bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN environment variable not set.")
    elif not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
    else:
        client.run(DISCORD_TOKEN)
