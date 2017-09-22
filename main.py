# ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #

# Import #

import json
import random
import re
import os
import math
import discord
import asyncio


# Global Constants #


ATH = ["ATHLETICS", "ATH"]
DEX = ["DEXTERITY", "DEX"]
CHR = ["CHARISMA", "CHR"]
ACA = ["ACADEMICS", "ACA"]
SAV = ["SAVVY", "SAV"]
STATS_ALIASES = {"ATH": ATH, "DEX": DEX, "CHR": CHR, "ACA":  ACA, "SAV": SAV}

REQ_STATS = "Which stats are related to this roll? Separate with commas. \n"
REQ_CHARS = "Which character is rolling? \n"
REQ_ACTOR = "Please provide a "
SAVED = "Databank updated, for whatever reason it needed updating!"

SUCCESS_VALUES = 4
FAILURE_VALUES = 6
DICE_SIZE = 10
SUCCESS = 'S - '
FAILURE = 'F - '
AGAIN = 'A - '
NEW_LINE = '\n'


# Global Vars #


escape_value = '!'
focused_actor = {"NAME": "", "ATHLETICS": 0, "DEXTERITY": 0, "CHARISMA": 0, "ACADEMICS":  0, "SAVVY": 0}
client = discord.Client()
app_token = "MzUzMTEzODg4Nzg0NjQ2MTQ0.DIunqw.tTJF2f3cDXSYXOcMdXMCETDqrLA"


# Error Messages #


EXTRA_ARGS = "It appears you attempted to use more than the required args. This command wants "
INV_ARG = "I don't recognize the keyword "
REPEAT_ARG = "You've already used the keyword "
INV_FORM = "It seems this is an invalid format. Try again."
LT_ZERO = "A stat can't be less than 0. And, let's be fair, do you really want it to be?"
GT_FIFT = "A stat can't be greater than 15. And that's already obnoxiously high as it is."
REPEAT = "Could you repeat the command?"
ESCAPE = "Escaping command..."


# Regexes #


non_numeric = '[^0-9]'
non_alphabetic = '[^a-zA-Z]'


# Events #


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):

    # List of commands.
    fc = "!forecast"
    nr = "!newactor"
    lr = "!listactors"
    sl = "!skillroll"
    hp = "!help"
    db = "!debug"
    commands = [fc, nr, lr, sl, hp, db]

    # # # # # # !forecast command # # # # # #

    if message.content.startswith(fc):
        # Format: [dice_pool, forecast_successes]
        args = message.content.split(',')

        # Check to make sure they didn't try to screw things up.
        if len(args) > 3:
            return await s(message, EXTRA_ARGS + '2')

        # Filter out non-numeric data
        for i in range(0, 2):
            args[i] = re.sub(non_numeric, '', args[i])

        return await s(message, percent(calc_success(int(args[0]), int(args[1]))))

    # # # # # # !newactor command # # # # # #

    if message.content.startswith(nr):
        # Format: <Type Command>

        # Ask for stat values.
        for field in focused_actor:

            input_not_recorded = True

            # Loop to not have to repeat the command over and over if an input is wrong.
            while input_not_recorded:

                # Ask user for the actor's field.
                await s(message, REQ_ACTOR + field + " value:")
                rsp = await client.wait_for_message(author=message.author)

                # Escape command early.
                if rsp.content == escape_value:
                    await s(message, ESCAPE)
                    return

                # List of checks to make sure their input makes sense.
                elif field != "NAME" and is_int(rsp.content):
                    stat_val = int(rsp.content)
                    non_neg = stat_val > -1
                    lt_fift = stat_val < 15

                    # Inform the user that -1 or less might be a bit low.
                    if not non_neg:
                        await s(message, LT_ZERO)

                    # Inform the user that 16 or more is too high.
                    if not lt_fift:
                        await s(message, GT_FIFT)

                    # User got it right, make sure to break this loop.
                    if non_neg and lt_fift:
                        focused_actor[field] = rsp.content
                        input_not_recorded = False

                elif field == "NAME":
                    # Store the name of the character.
                    focused_actor[field] = rsp.content
                    input_not_recorded = False

                elif field != "NAME" and not is_int(rsp.content):
                    await s(message, INV_FORM)

        # Make file if it doesn't exist.
        f = open("actors.txt", "a")
        f.close()

        # Pull JSON file for updating.
        with open("actors.txt", "r") as fin:
            if os.stat("actors.txt").st_size > 0:
                actors = json.load(fin)
            else:
                actors = {}

        # TODO: Make sure you can't write over characters unless you're the GM.

        # Append actor to file.
        actors[focused_actor["NAME"]] = focused_actor

        # Update character file.
        with open("actors.txt", "w") as fout:
            json.dump(actors, fout, indent=1)

        return await s(message, SAVED)

    # # # # # # !listactors command # # # # # #

    if message.content.startswith(lr):
        # Format: <Type Command>

        # Make file if it doesn't exist.
        f = open("actors.txt", "a")
        f.close()

        # Pull JSON file for reading.
        with open("actors.txt", "r") as fin:
            if os.stat("actors.txt").st_size > 0:
                actors = json.load(fin)
            else:
                actors = {}

        # Concatenate all names.
        all_names = ""

        for name in actors:
            all_names += name + '\n'

        return await s(message, all_names)

    # # # # # # !skillroll command # # # # # #

    if message.content.startswith(sl):
        # Format: <Type Command>

        async def format_command(command_info, stats_array, expected_vars):
            improperly_formatted = True

            while improperly_formatted:
                # Assume properly formatted until otherwise noted.
                improperly_formatted = False

                # Escape command early.
                if command_info == escape_value:
                    return await s(message, ESCAPE)

                # Check to make sure they didn't try to screw things up.
                if len(stats_array) > 3:
                    improperly_formatted = True
                    await s(message, EXTRA_ARGS + expected_vars +" or less")

                # Filter out non-alphabetic data
                for j in range(len(stats_array)):
                    stats_array[j] = re.sub(non_alphabetic, '', stats_array[j])

        # Ask for stats involved in roll.
        await s(message, REQ_STATS)
        rsp = await client.wait_for_message(author=message.author)
        stats = rsp.content.split(',')
        await format_command(rsp.content, stats, 2)

        # Make sure that values are acceptable
        i = 0
        used_stat = []

        # For each possible name for a stat, check that the names the user input are valid.
        while i < len(stats):
            still_inv = True
            for stat in STATS_ALIASES:
                for alias in STATS_ALIASES[stat]:
                    if alias.lower() == stats[i].lower() and used_stat != stat:
                        still_inv = False
                        used_stat = stat
                    elif alias.lower() == stats[i].lower() and used_stat == stat:
                        await s(message, REPEAT_ARG + stats[i] + "! " + REPEAT)
                        still_inv = False
                        i = 0
                        used_stat = []
                        rsp = await client.wait_for_message(author=message.author)
                        stats = rsp.content.split(',')
                        await format_command(rsp.content, stats, 2)
                        break
            if still_inv:
                await s(message, INV_ARG + stats[i] + "! " + REPEAT)
                i = 0
                used_stat = []
                rsp = await client.wait_for_message(author=message.author)
                stats = rsp.content.split(',')
                await format_command(rsp.content, stats, 2)
            else:
                i += 1

        # TODO: Find the related character.

        # TODO: Ask for any modifications to the scenario.

        # TODO: Complete the roll.

        # TODO: Format the roll string.

        return await client.send_message(message.channel, stats)

    # # # # # # !help command # # # # # #

    if message.content.startswith(hp):

        all_commands = "Commands are currently as follows: \n\n"

        for command in commands:
            all_commands += command + '\n'

        # TODO: Add support for explaining what commands do.

        return await s(message, all_commands)

    # # # # # # !debug command # # # # # #

    if message.content.startswith(db):
        # Format: <relative>
        return await s(message, "I'm not testing anything right now")


# Methods #

def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def s(message, arg):
    """Syntactical candy"""
    return client.send_message(message.channel, arg)


def calc_success(dice_pool, success_forecast):
    """Returns the likelihood of success for a given pool of dice and expected number of successes"""

    # TODO: Account for '10 Again' rule

    return (math.pow(SUCCESS_VALUES, success_forecast)
           * math.pow(FAILURE_VALUES, (dice_pool - success_forecast))
           * combination(dice_pool, success_forecast)
           / math.pow(DICE_SIZE, dice_pool))


def percent(val):
    """Converts a number into a percentage"""
    percent_val = val * 100
    percent_str = str(percent_val) + '%'
    return percent_str


def combination(dice_pool, success_forecast):
    """Returns the combinitorics definition of a combination"""
    return (factorial(dice_pool)
            / (factorial(success_forecast)
            * factorial(dice_pool - success_forecast)))


def factorial(value):
    """Returns the factorial"""
    return value * factorial(value - 1) if value - 1 > 0 else 1


def branching_module(dice_pool, successes, forecast, ten_agains=0, succ_set=[]):
    """Helper Function for me to simulate the branching properties of ten again"""
    # String to represent the simulation...
    branches = ''

    # If first call (tens == 0), simulate normal dice roll.
    if ten_agains == 0:
        # This would represent solving the problem normally.
        for _ in range(successes):
            branches += SUCCESS
        for _ in range(dice_pool - successes):
            branches += FAILURE
        branches = branches[:-2] + NEW_LINE

    # <Under what circumstances does it recurse?> #

    # If there's a ten-again set to resolve...
    if ten_agains > 0:

        # Track number of successes for recursive purposes.
        succ_set.append(successes)
        succ_set.append(ten_agains)

        for _ in range(ten_agains):
            branches += AGAIN
        for _ in range(successes):
            branches += SUCCESS
        for _ in range(dice_pool - successes - ten_agains):
            branches += FAILURE
        branches = branches[:-2]

        if forecast != sum(succ_set):
            # What conditions does this need to meet?
            # > The dice pool is now the number of ten-agains.
            # > The successes are complicated.
            # > > If I'm at ten-agains == dice_pool, then successes must be 0
            # > Ten-agains should reset at 0 unless...
            # > > If sum(success_set) + 1 != forecast, then ten-agains need to == 0
            branches += " : " + branching_module(ten_agains,
                                                 ten_agains if forecast == sum(succ_set) + ten_agains else 0,
                                                 forecast,
                                                 1,
                                                 succ_set)

        # What's our stopping condition:  Hitting a single success roll.

    # If there's still more ten-agains to resolve...
    if ten_agains < math.floor(successes / 2):
        # What conditions does this need to meet?
        # > The dice pool is the same.
        # > The successes are now down by two. This is because...
        # > > The ten-again accounts for at least 1 success.
        # > > If we were to include the ten-again in successes, we wouldn't properly decouple the new set.
        # > > Accounting for one more success: If we don't use the ten-again property, there's no point representing it.
        # > The ten-agains must increase to encompass all useful possibilities.
        branches += branching_module(dice_pool,
                                     successes - (ten_agains + 2),
                                     forecast,
                                     ten_agains + 1,
                                     succ_set)

    return branches


def add_actor(name, ath, dex, chr, acd, sav):
    """A function to store a JSON entry of a character"""


def skill_check(first, second, actor, **mods):
    """A function that takes skill types, character and mods, rolls that many die, then returns a formatted string."""
    # TODO: Find a way to store characters.

def skill_calc(*mods):
    """A function that takes two skill values and modifiers, adds them together, then rolls that many die."""
    succ = 0;
    pool = 0;

    # Add all mods together.
    for mod in mods:
        pool += mod

    # Roll the proper number of die.
    for _ in range(pool):
        val = roll_die()

        while val == DICE_SIZE:
            succ += 1
            val = roll_die()

        if val > FAILURE_VALUES:
            succ += 1

    return succ


def roll_die():
    return random.randint(1, DICE_SIZE)


# Code #


client.run(app_token)
