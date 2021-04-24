''' 
Auth bot
'''
# External imports
import asyncio
import os
from discord import Client
from discord import Intents
from dotenv import load_dotenv

# Internal imports
import CodeGenerator

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


# Set required intents.
intents = Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
client = Client(intents=intents)

# Constants
CODE_LENGTH = 8



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

# When a member joins the designated server.
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to The Show Discord Server!\n' +
        'If you are a University of Toronto Student, please' +
        " authenticate via email by messaging me '!auth your-uoft-email'." + \
        " If not, please message a Staff member with your school email!" +
        " See you soon!"
    )

# When a server member messages Herald.
@client.event
async def on_message(message):
    print(message.guild)
    member = message.author
    if not message.guild:
        if validate_command_prefix(message.content, "!auth"):
            print(message.author.name)
            # Check first if user already has participant role
            split_message = message.content.split(" ")
            if len(split_message) == 2 and "@" in split_message[1]:
                email = split_message[1]
                if is_valid_email(email):
                    print("Valid email from: " + member.name)
                    code = CodeGenerator(code_length=CODE_LENGTH)
                    EmailService()
                else:
                    print("Invalid email from: " + member.name)
                    # Please submit a valid uoft email address.
        if validate_command_prefix(message.content, "!code"):
            if len(split_message) == 2:
                
        else:
            await invalid_command_callback(member)


async def invalid_command_callback(member):
    await member.create_dm()
    await member.dm_channel.send(
        'Invalid command.'
    )


def validate_command_prefix(content, prefix):
''' Validates whether the content of a command's message starts with the required prefix'''
    if not isinstance(content, str):
        return False
    if len(content) < len(prefix) or content[0:5] != prefix:
        return False
    return True


def is_valid_email(email):
    valid_suffixes = ["mail.utoronto.ca", "utoronto.ca"]
    for suffix in valid_suffixes:
        if re.search('^[A-Za-z0-9._%+-]+@' + email_domain + '$'):
            return True
    return False


client.run(TOKEN)
