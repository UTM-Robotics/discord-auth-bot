''' 
Auth bot
'''
# External imports
import asyncio
import os
import re
from discord import Client
from discord import Intents
from dotenv import load_dotenv

# Internal imports
from CodeGenerator import CodeGenerator
from EmailService import EmailService
# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
GUILD = os.getenv('DISCORD_GUILD')
VERIFICATION_CHANNEL = os.getenv('VERIFICATION_CHANNEL')
VERIFICATED_ROLE_NAME = os.getenv('VERIFICATED_ROLE_NAME')
BANNED_CHANNEL = os.getenv('BANNED_CHANNEL')
VERIFIED_CHANNEL = os.getenv('VERIFIED_CHANNEL')
EMAIL_SUBJECT = "Deerfield Village Discord Verification"

# Set required intents.
intents = Intents.default()
intents.typing = False
intents.members = True

# Constants
CODE_LENGTH = 8


#Globals
current_guild = None
verification_channel = None
verification_role = None
banned_channel = None
verified_channel = None

HELP_MESSAGE = """
Hey, welcome to Deerfield Village :wave:!

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

client = Client(intents=intents)

@client.event
async def on_ready():

    print(f'{client.user} has connected to Discord!')
    global verification_channel
    global verification_role
    global current_guild
    global banned_channel
    global verified_channel

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
    # Load Verification channel
    for channel in current_guild.channels:
        if channel.name == VERIFICATION_CHANNEL:
            verification_channel = channel
            break
    if verification_channel == None:
        print(f"Required verification channel {VERIFICATION_CHANNEL} not found.")
        exit(-1)
    # Load Banned users channel
    for channel in current_guild.channels:
        if channel.name == BANNED_CHANNEL:
            banned_channel = channel
            break
    if banned_channel == None:
        print(f"Required banned channel {BANNED_CHANNEL} not found.")
        exit(-1)
    # Load verified users channel
    for channel in current_guild.channels:
        if channel.name == VERIFIED_CHANNEL:
            verified_channel = channel
            break
    if verified_channel == None:
        print(f"Required verified channel {VERIFIED_CHANNEL} not found.")
        exit(-1)
    print(
        f'{client.user} is mapped to the following channels:\n'
        f'{verification_channel.name}(id: {verification_channel.id}) and \n'
        f'{banned_channel.name}(id: {banned_channel.id} and \n'
        f'{verified_channel.name}(id: {verified_channel.id})'
    )
    #load verification role
    for role in current_guild.roles:
        if role.name == VERIFICATED_ROLE_NAME:
            verification_role = role
            break

    if verification_role == None:
        print(f"Required verification role {VERIFICATED_ROLE_NAME} not found.")
        exit(-1)
    print(
        f'{client.user} is mapped to the following verification role:\n'
        f'{verification_role.name}(id: {verification_role.id})'
    )

# When a member joins the designated server.
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.send(
        f'Hi {member.name}, welcome to the Deerfield Village Discord Server!\n' +
        'If you are a University of Toronto Student, please' +
        " authenticate via email by messaging me `!auth your-uoft-email`." + \
        " If not, please message a Staff member with your school email!" +
        " See you soon!"
    )

# When a server member messages Herald.
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    member = message.author
    if not message.guild:
        print(f"--------Message received from: {message.author.name}--------\n")
        print("Received in guild: " +  str(message.guild))
        if validate_command_prefix(message.content, "!auth"):
            print("User called !auth")

            # Check first if user already has participant role
            split_message = message.content.split(" ")
            if len(split_message) == 2 and "@" in split_message[1] \
                and len(split_message[1]) <= 254:
                email = split_message[1]
                # Validate email
                if is_valid_email(email) and await is_free_email(member, email):
                    print("Valid email used: " + email)
                    gen = CodeGenerator(code_length=CODE_LENGTH)
                    code = gen.generate()
                    print("Code generated:" +  code)
                    emailService = EmailService(EMAIL_USERNAME,EMAIL_PASSWORD)
                    status = emailService.sendmail(receiver=email,
                        subject=EMAIL_SUBJECT,
                        #TODO: Format this into a constant
                        body=f"Welcome to Deerfield Village, {member.name}! \
                        Your verification code is: {code}"
                        )
                    if status:
                        print("Email sent")
                        await send_verification_log(code, email, member)
                        await send_verification_confirmation(member)
                    else:
                        print("FAILURE: Could not send email")
                        await invalid_email_callback(member)
                else:
                    #TODO Please submit a valid uoft email address.
                    print("Invalid email from: " + member.name)
            else:
                await invalid_command_callback(member)
        elif validate_command_prefix(message.content, "!code"):
            split_message = message.content.split(" ")
            if len(split_message) == 2:
                code=split_message[1]
                if await does_code_match(code, member):
                    await grant_verification_role(member)
                    print("Granted role to : " + member.name)
                    await role_granted_callback(member)
                else:
                    print("Invalid verification code from: " + member.name)
                    await invalid_verification_code_callback(member)
            else:
                print("Invalid verification code command from: " + member.name)
                await invalid_command_callback(member)

        elif validate_command_prefix(message.content,  "!help"):
            await member.send(
                HELP_MESSAGE
            )
        else:
            await invalid_command_callback(member)

@client.event
#when a user is banned
async def on_member_ban(guild, user):
    global verified_channel
    messages = await verified_channel.history(limit=20000).flatten()
    for message in messages:
        parsed = message.content.split(", ")
        email = parsed[0]
        id = parsed[2]
        if id == str(user.id):
            await send_banned_log(email, user)
            print("user: " + str(user.name) + " was banned from the server, the email: " + str(
                email) + " was added to ban list")
            await message.delete()
            break
    return

@client.event
#when a user is unbanned
async def on_member_unban(guild, user):
    global banned_channel
    messages = await banned_channel.history(limit=20000).flatten()
    for message in messages:
        parsed = message.content.split(", ")
        email = parsed[0]
        id = parsed[2]
        if id == str(user.id):
            print("user: " + str(user.name) + " was unbanned from the server, the email: " + str(
                email) + " was removed from the ban list")
            await message.delete()
            break
    return


async def grant_verification_role(user):
    global current_guild
    member = current_guild.get_member(user.id)
    await member.add_roles(verification_role)


# check if code matches, if it does return the email of the verified user
async def does_code_match(code, member):
    global verification_channel
    messages = await verification_channel.history(limit=20000).flatten()
    for message in messages:
        parsed = message.content.split(", ")
        if len(parsed) <= 3:
            continue
        id = parsed[0]
        parsed_code = parsed[1]
        email = parsed[2]
        if id == str(member.id) and parsed_code == code:
            await send_verified_log(str(email), member)
            return True
    return False


# check if email has been banned or already in use
async def is_free_email(user, email):
    global banned_channel
    global verified_channel
    messages = await banned_channel.history(limit=20000).flatten()
    for message in messages:
        parsed = message.content.split(", ")
        if email == parsed[0]:
            await user.send("This email address has been banned from a previous account.")
            return False
    messages = await verified_channel.history(limit=20000).flatten()
    for message in messages:
        parsed = message.content.split(", ")
        if email == parsed[0]:
            await user.send("This email address is already in use, if you think this is an error please contact server admin")
            return False
    return True


async def send_verification_log(code, email, member):
    global verification_channel
    await verification_channel.send(f'{member.id}, {code}, {email}, {member.name}')


# send email and member name to verified channel
async def send_verified_log(email, member):
    global verified_channel
    await verified_channel.send(f'{email}, {member.name}, {member.id}')


# send banned user log to banned users channel
async def send_banned_log(email, member):
    global banned_channel
    await banned_channel.send(f'{email}, {member.name}, {member.id}')


async def role_granted_callback(member):
    await member.send(
        'Success! Have fun, be sure to check #schedule for the full event schedule!'
    )


async def send_verification_confirmation(member):
    await member.send(
        'Success! Check the above email(and spam) for a code, then respond here with`!code your-code` to verify!'
    )


async def invalid_command_callback(member):
    await member.send(
        'Invalid command, send "!help" for commands.'
    )


async def invalid_email_callback(member):
    await member.send(
        'Invalid email, please enter a valid UofT email.'
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
    if len(content) < len(prefix) or content[0:len(prefix)] != prefix:
        return False
    return True


def is_valid_email(email):
    valid_suffixes = ["mail.utoronto.ca", "utoronto.ca", "cs.toronto.edu"]
    for suffix in valid_suffixes:
        if re.search('^[A-Za-z0-9._%+-]+@' + suffix + '$', email):
            return True
    return False


client.run(TOKEN)
