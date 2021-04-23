''' 
Auth bot
'''
import asyncio
from discord import Client
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to The Show Discord Server!'+ \
        'If you are a University of Toronto Student, please' + \
        " authenticate via email by messaging me '!auth your-uoft-email'."
    )

@client.event
async def on_message(message):
    if not message.guild:
        if validate_email_command(message.content):
            print("asdas")
        else:
            await message.author.create_dm()
            await member.dm_channel.send(
                'Invalid command.'
            )

async def validate_email_command(content):
    prefix = "!auth"
    valid_suffixes = ["mail.utoronto.ca", "utoronto.ca"]
    if not isInstance(content,str):
        return False
    if len(content < len(prefix)) or content[0:5] != prefix:
        return False
    return True


client.run(TOKEN)