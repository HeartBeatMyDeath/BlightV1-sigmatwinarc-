import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import random
import webserver

# Load environment variables
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Constants
ALLOWED_USER_ID = 1372549650225168436
STICKER_EMOJI = "<:stickerherta:1431751497435054093>"
IMAGE_URL = "https://i.imgur.com/r5erfnY.jpeg"

# Original server message IDs
GUILD_ID = 1431718345903702172

ALLIES_CHANNEL_ID = 1431742381048463390
ALLIES_MSG_ID = 1431996823316463730

ENEMIES_CHANNEL_ID = 1431742381048463390
ENEMIES_MSG_ID = 1431996824427696262

# In-memory DM message IDs
allies_dm_msg_id = {}
enemies_dm_msg_id = {}

# Weapons and Attunements
weapons = {
    1: "Dagger",
    2: "Fist",
    3: "Gun",
    4: "Rapier",
    5: "Twinblade",
    6: "Sword",
    7: "Rifle",
    8: "Club",
    9: "Greatsword",
    10: "Greataxe",
    11: "Greathammer",
    12: "Greatsword",
    13: "Greatcannon"
}

attunements = {
    21: "Attunementless",
    22: "Flamecharm",
    23: "Frostdraw",
    24: "Galebreath",
    25: "Bloodrend",
    26: "Ironsing",
    27: "Shadowcast",
    28: "Thundercall"
}

# Bot setup
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands synced and ready.")

bot = MyBot()

# -------------------
# Helper functions
# -------------------
def format_list_embed(title: str, items: list):
    if not items:
        description = "List is empty."
    else:
        description = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    return discord.Embed(title=title, description=description, color=0x9B59B6)

def extract_items_from_embed(embed: discord.Embed):
    if not embed or not embed.description or embed.description == "List is empty.":
        return []
    return [line.split(". ", 1)[1] for line in embed.description.split("\n")]

async def fetch_server_message(guild_id, channel_id, msg_id):
    guild = bot.get_guild(guild_id)
    if not guild:
        return None
    channel = guild.get_channel(channel_id)
    if not channel:
        return None
    try:
        msg = await channel.fetch_message(msg_id)
        return msg
    except:
        return None

async def get_allies_message(interaction: discord.Interaction):
    if interaction.guild:  # in guild, use original server message
        return await fetch_server_message(GUILD_ID, ALLIES_CHANNEL_ID, ALLIES_MSG_ID)
    else:  # DM context
        msg_id = allies_dm_msg_id.get(interaction.channel.id)
        if msg_id is None:
            return None
        return await interaction.channel.fetch_message(msg_id)

async def get_enemies_message(interaction: discord.Interaction):
    if interaction.guild:
        return await fetch_server_message(GUILD_ID, ENEMIES_CHANNEL_ID, ENEMIES_MSG_ID)
    else:
        msg_id = enemies_dm_msg_id.get(interaction.channel.id)
        if msg_id is None:
            return None
        return await interaction.channel.fetch_message(msg_id)

# -------------------
# Public Interface View
# -------------------
class InterfaceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Allies", style=discord.ButtonStyle.primary)
    async def allies_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await get_allies_message(interaction)
        if msg is None:
            await interaction.response.send_message("No Allies message found.", ephemeral=True)
            return
        await interaction.response.send_message(embed=msg.embeds[0], ephemeral=True)

    @discord.ui.button(label="Enemies", style=discord.ButtonStyle.danger)
    async def enemies_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await get_enemies_message(interaction)
        if msg is None:
            await interaction.response.send_message("No Enemies message found.", ephemeral=True)
            return
        await interaction.response.send_message(embed=msg.embeds[0], ephemeral=True)

    @discord.ui.button(label="Random Build", style=discord.ButtonStyle.secondary)
    async def random_build_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        weapon_choice = weapons[random.randint(1, 13)]
        attunement_choice = attunements[random.randint(21, 28)]
        embed = discord.Embed(
            title="🎲 Random Build",
            description=f"**Weapon:** {weapon_choice}\n**Attunement:** {attunement_choice}",
            color=0x9B59B6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# -------------------
# Private Modals
# -------------------
class AddAllyModal(discord.ui.Modal, title="Add Ally"):
    ally_name = discord.ui.TextInput(label="Ally Name")
    async def on_submit(self, interaction: discord.Interaction):
        msg = await get_allies_message(interaction)
        if msg is None:
            await interaction.response.send_message("No Allies message found.", ephemeral=True)
            return
        items = extract_items_from_embed(msg.embeds[0])
        items.append(self.ally_name.value)
        await msg.edit(embed=format_list_embed("Allies", items))
        await interaction.response.send_message(f"Added {self.ally_name.value} to Allies!", ephemeral=True)

class RemoveAllyModal(discord.ui.Modal, title="Remove Ally"):
    ally_name = discord.ui.TextInput(label="Ally Name")
    async def on_submit(self, interaction: discord.Interaction):
        msg = await get_allies_message(interaction)
        if msg is None:
            await interaction.response.send_message("No Allies message found.", ephemeral=True)
            return
        items = extract_items_from_embed(msg.embeds[0])
        if self.ally_name.value in items:
            items.remove(self.ally_name.value)
            await msg.edit(embed=format_list_embed("Allies", items))
            await interaction.response.send_message(f"Removed {self.ally_name.value} from Allies!", ephemeral=True)
        else:
            await interaction.response.send_message(f"{self.ally_name.value} not found in Allies.", ephemeral=True)

class AddEnemyModal(discord.ui.Modal, title="Add Enemy"):
    enemy_name = discord.ui.TextInput(label="Enemy Name")
    async def on_submit(self, interaction: discord.Interaction):
        msg = await get_enemies_message(interaction)
        if msg is None:
            await interaction.response.send_message("No Enemies message found.", ephemeral=True)
            return
        items = extract_items_from_embed(msg.embeds[0])
        items.append(self.enemy_name.value)
        await msg.edit(embed=format_list_embed("Enemies", items))
        await interaction.response.send_message(f"Added {self.enemy_name.value} to Enemies!", ephemeral=True)

class RemoveEnemyModal(discord.ui.Modal, title="Remove Enemy"):
    enemy_name = discord.ui.TextInput(label="Enemy Name")
    async def on_submit(self, interaction: discord.Interaction):
        msg = await get_enemies_message(interaction)
        if msg is None:
            await interaction.response.send_message("No Enemies message found.", ephemeral=True)
            return
        items = extract_items_from_embed(msg.embeds[0])
        if self.enemy_name.value in items:
            items.remove(self.enemy_name.value)
            await msg.edit(embed=format_list_embed("Enemies", items))
            await interaction.response.send_message(f"Removed {self.enemy_name.value} from Enemies!", ephemeral=True)
        else:
            await interaction.response.send_message(f"{self.enemy_name.value} not found in Enemies.", ephemeral=True)

# -------------------
# Private View
# -------------------
class PrivateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Add Ally", style=discord.ButtonStyle.primary)
    async def add_ally_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddAllyModal())

    @discord.ui.button(label="Remove Ally", style=discord.ButtonStyle.secondary)
    async def remove_ally_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RemoveAllyModal())

    @discord.ui.button(label="Add Enemy", style=discord.ButtonStyle.danger)
    async def add_enemy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddEnemyModal())

    @discord.ui.button(label="Remove Enemy", style=discord.ButtonStyle.secondary)
    async def remove_enemy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RemoveEnemyModal())

# -------------------
# Slash Commands
# -------------------
@bot.tree.command(name="interface", description="Show the BlightV1 interface with Allies/Enemies.")
async def interface(interaction: discord.Interaction):
    embed = discord.Embed(
        title=f"Welcome! {STICKER_EMOJI}",
        description="**Interface of BlightV1.**\nDM **lunaciaaaaa** for problems.",
        color=0x9B59B6
    )
    embed.set_image(url=IMAGE_URL)
    view = InterfaceView()
    await interaction.response.send_message(embed=embed, view=view)

    # DM: create Allies/Enemies messages if not exist
    if not interaction.guild:
        if interaction.channel.id not in allies_dm_msg_id:
            allies_msg = await interaction.channel.send(embed=format_list_embed("Allies", []))
            allies_dm_msg_id[interaction.channel.id] = allies_msg.id
        if interaction.channel.id not in enemies_dm_msg_id:
            enemies_msg = await interaction.channel.send(embed=format_list_embed("Enemies", []))
            enemies_dm_msg_id[interaction.channel.id] = enemies_msg.id

@bot.tree.command(name="private_interface", description="Show the private BlightV1 interface (restricted).")
async def private_interface(interaction: discord.Interaction):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("🚫 You are not authorized to use this command.", ephemeral=True)
        return
    embed = discord.Embed(
        title=f"Welcome author! {STICKER_EMOJI}",
        description="**BlightV1 is ready to edit.**",
        color=0x9B59B6
    )
    embed.set_image(url=IMAGE_URL)
    view = PrivateView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# -------------------
# Run Bot
# -------------------
webserver.keep_alive()
bot.run(token)



