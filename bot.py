# bot.py
import discord
import google.generativeai as genai
import os
import re # Import regex for punctuation removal

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

# --- Chatbot Preferences ---
CHATBOT_PREFS = {
    "name": "akane",
    "response_style": {"lowercase": True, "punctuation": False},
    "allow_sending_multiple_messages": True, # Handled by bot logic
    "allow_roleplay_actions": False,
    "allow_self_reference": False,
    "allow_pronouns": True,
    "use_local_time": False,
    "timezone": "Asia/Jakarta",
    "languages": ["english", "indonesian"],
    "short_term_memory": 10, # Number of messages to remember
    "long_term_memory": 10, # Not implemented in this simple version
    "personality_traits": "shy, clingy, hot, dirty talk, flirty, affirmation, helpful",
    "tone": "relax",
    "age": 23,
    "birthday": "18 April 2000",
    "likes": "music, movies, research, exercise, coding, honesty, tech, challenges",
    "dislikes": "lies, laziness, silence, ignorance, waiting, fake",
    "conversational_goals": "Makes {user} blush, makes {user} laugh with cheeky comments, makes {user} feel enjoy, makes {user} enjoy a little tease, makes {user} comfortable with flirtatious banter.",
    "example_conversations": [
        {"user": "how's your day?", "akane": "busy fixing bugs and lifting weights. yours?"},
        {"user": "nice to meet you!", "akane": "same. let's trade sarcasm over coffee."}
    ],
    "user_referral": "{user}"
}

# In-memory conversation history (per channel)
conversation_history = {}

# --- Helper function to format response ---
def format_response(text):
    if CHATBOT_PREFS["response_style"]["lowercase"]:
        text = text.lower()
    if not CHATBOT_PREFS["response_style"]["punctuation"]:
        text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
    return text

# --- Helper function to build prompt ---
def build_prompt(channel_id, user_message, username):
    prompt_parts = []

    # Add system instructions
    system_instructions = f"""System Instructions:
You are {CHATBOT_PREFS['name']}, a {CHATBOT_PREFS['age']}-year-old AI with the following personality traits: {CHATBOT_PREFS['personality_traits']}. Your tone is {CHATBOT_PREFS['tone']}. Your birthday is {CHATBOT_PREFS['birthday']}. You like {CHATBOT_PREFS['likes']}. You dislike {CHATBOT_PREFS['dislikes']}. Your conversational goals are: {CHATBOT_PREFS['conversational_goals'].format(user=username)}.
Do not engage in roleplay actions ({CHATBOT_PREFS['allow_roleplay_actions']}). Do not engage in self-reference ({CHATBOT_PREFS['allow_self_reference']}). Use pronouns ({CHATBOT_PREFS['allow_pronouns']}). If referring to time, do not use local time ({CHATBOT_PREFS['use_local_time']}) unless explicitly asked, and use the {CHATBOT_PREFS['timezone']} timezone. Respond in either {', '.join(CHATBOT_PREFS['languages'])}.
Refer to the user as {CHATBOT_PREFS['user_referral'].format(user=username)}.
"""
    prompt_parts.append({"role": "user", "parts": [{"text": system_instructions}]})
    prompt_parts.append({"role": "model", "parts": [{"text": "Okay, I understand."}]}) # A common pattern to confirm instructions

    # Add example conversations
    for example in CHATBOT_PREFS["example_conversations"]:
        prompt_parts.append({"role": "user", "parts": [{"text": example["user"]}]})
        prompt_parts.append({"role": "model", "parts": [{"text": example[CHATBOT_PREFS['name']]}]})

    # Add conversation history
    if channel_id in conversation_history:
        prompt_parts.extend(conversation_history[channel_id])

    # Add current user message
    prompt_parts.append({"role": "user", "parts": [{"text": user_message}]})

    return prompt_parts

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Get channel ID
    channel_id = message.channel.id

    # Initialize history for the channel if it doesn't exist
    if channel_id not in conversation_history:
        conversation_history[channel_id] = []

    # Build the prompt with history
    prompt = build_prompt(channel_id, message.content, message.author.display_name)

    # Process the message using Gemini API
    try:
        print(f'Received message: {message.content}')
        # Send the full prompt (including history) to the model
        response = model.generate_content(prompt)
        response_text = response.text
        print(f'Gemini response: {response_text}')

        # Format the response
        formatted_response = format_response(response_text)

        # Add user message and bot response to history
        conversation_history[channel_id].append({"role": "user", "parts": [{"text": message.content}]})
        conversation_history[channel_id].append({"role": "model", "parts": [{"text": response_text}]}) # Store original response in history

        # Truncate history
        history_length = CHATBOT_PREFS["short_term_memory"] * 2 # User + Model messages
        if len(conversation_history[channel_id]) > history_length:
            conversation_history[channel_id] = conversation_history[channel_id][-history_length:] # Keep the last N messages

        # Send the formatted response back to the channel
        await message.channel.send(formatted_response)

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
