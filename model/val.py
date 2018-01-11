# ----------- Script by ReedRGale ----------- #
# Constant values used in the scripts. #


# Imports #


from discord.ext import commands


# Constants #


SUCCESS_VALUES = 4
FAILURE_VALUES = 6
DICE_SIZE = 10
WHITESPACE = [' ', '\n', '\t']


# Links #


T_URLS_STANDARD = ["https://image.ibb.co/fvgnxw/chrome_2017_12_02_01_44_59.png"]
T_URLS_WARNING = ["https://image.ibb.co/ciiTLG/chrome_2017_12_06_00_39_54.png"]
A_URLS_STANDARD = ["https://image.ibb.co/nhRWPb/chrome_2017_12_05_22_29_14.png"]
A_URLS_WARNING = ["https://image.ibb.co/nhRWPb/chrome_2017_12_05_22_29_14.png"]
GITHUB_URL = "https://github.com/ReedRGale/MissingBot"

# This is simply more relevant here.
AVATAR_STRING = "https://cdn.discordapp.com/avatars/{}/{}.jpg"


def p_avatar(tm):
    """Uses the TidyMessage to get context on the prompt of who's calling. Use that to get the avatar of the user."""
    return AVATAR_STRING.format(tm.prompt.author.id, tm.prompt.author.avatar)


def p_color(tm):
    return tm.prompt.author.color


# Variables #


calling = dict()
perms = dict()
bot = commands.Bot(command_prefix="~dd ", fetch_offline_members=True)


