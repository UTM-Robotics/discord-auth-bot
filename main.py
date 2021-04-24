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
EMAIL_USERNAME = os.getenv('EMAIL_PASSWORD')
EMAIL_PASSWORD = os.getenv('EMAIL_USERNAME')
GUILD = os.getenv('DISCORD_GUILD')
VERIFICATION_CHANNEL = os.getenv('VERIFICATION_CHANNEL')
VERIFICATED_ROLE_NAME = os.getenv('VERIFICATED_ROLE_NAME')

# Set required intents.
intents = Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
client = Client(intents=intents)

# Constants
CODE_LENGTH = 8


#Globals
current_guild = None
verification_channel = None
verifictation_role = None

HELP_MESSAGE = """
Hey, welcome to The Show :wave:!

Valid commands are `!help`, `!auth`, and `!code`.
    `!help` :
        Displays available commands
    `!auth your-uoft-email` : 
        Sends a verification email to your account.
        Once verification is complete, users are granted participant access to The Show.
    `!code your-verification-code` : 
        Given a valid code, grants the user the participant role.

Message me with any of the above commands.
"""


@client.event
async def on_ready():
    print()
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        if guild.name == GUILD:
            current_guild=guild
            break
    if current_guild == None:
        print(f"Required guild{GUILD} not found.")
        exit(-1)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    for channel in current_guild.channels:
        if channel.name == VERIFICATION_CHANNEL
            verification_channel = channel
            break

    if current_guild == None:
        print(f"Required verification channel {VERIFICATION_CHANNEL} not found.")
        exit(-1)
    role = get(current_guild.roles, name=VERIFICATED_ROLE_NAME)


# When a member joins the designated server.
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.send(
        f'Hi {member.name}, welcome to The Show Discord Server!\n' +
        'If you are a University of Toronto Student, please' +
        " authenticate via email by messaging me '!auth your-uoft-email'." + \
        " If not, please message a Staff member with your school email!" +
        " See you soon!"
    )

# When a server member messages Herald.
@client.event
async def on_message(message):
    print(f"--------Message received from: {message.author.name}--------\n")
    print(message.guild)
    member = message.author
    if not message.guild:
        if validate_command_prefix(message.content, "!auth"):
            print("User called !auth")

            # Check first if user already has participant role
            split_message = message.content.split(" ")
            if len(split_message) == 2 and "@" in split_message[1] \
                and len(split_message[1]) > 254:
                email = split_message[1]
                # Validate email
                if is_valid_email(email): #TODO and not_validated(member):
                    print("Valid email: " email )
                    code = CodeGenerator(code_length=CODE_LENGTH).generate()
                    print("Code generated:")
                    emailService = EmailService(EMAIL_USERNAME,EMAIL_PASSWORD)
                    status = emailService.sendmail(receiver=email, 
                        subject="The Show Discord Verification",
                        message=f"Welcome to the Show, {member.name}! 
                        Your verification code is: {code}"
                        )
                    if status:
                        await send_verification_log(code, email, member)
                    else:
                        await invalid_command_callback(member)
                else:
                    print("Invalid email from: " + member.name)
                    # Please submit a valid uoft email address.
            else:
                await invalid_command_callback(member)
        elif validate_command_prefix(message.content, "!code"):
            if len(split_message) == 2:
                code=split_message[1]
                # TODO
                if await does_code_match(code, member):
                    await grant_verification_role(member)
                    # Set role
                    #consume_code(member)
                else:
                    print("Invalid verification code from: " + member.name)
                    invalid_verification_code_callback(member)
            else:
                print("Invalid verification code command from: " + member.name)
                await invalid_command_callback(member)

        elif validate_command_prefix(message.content,  "!help"):
            await member.send(
                HELP_MESSAGE
            )
        else:
            await invalid_command_callback(member)

async def grant_verification_role(member):
    await member.add_roles(verifictation_role)
async def does_code_match(code, member):
    messages = await verification_channel.history(limit=20000).flatten()
    for message in messages:
        parsed = message.content.split(", ")
        id = parsed[0]
        code = parsed[1]
        if id == member.id and code == code:
            return True
    return False

async def send_verification_log(code, email, member):
    await verification_channel.send(f'{member.id}, {code}, {email}, {member.name}')

async def invalid_command_callback(member):
    await member.send(
        'Invalid command, send "!help" for commands.'
    )

async def invalid_verification_code_callback(member):
    await member.send(
        'Invalid verification code. Please check the correct code has been sent.'
    )

def validate_command_prefix(content, prefix):
    ''' Validates whether the content of a command's message 
        starts with the required prefix.
    '''
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
