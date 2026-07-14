import discord
import os
import asyncio
from discord.ext import commands
from flask import Flask
from threading import Thread

# Flask (Web sunucusu - 7/24 aktif tutar)
app = Flask('')
@app.route('/')
def home(): return "Bot aktif!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# Intentler
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Ayarlar
ROK_ROL_ID = 1525779899745308712
ROLE_IDS = {
    "Infantry": 1526342009596547142,
    "Cavalry": 1526341870899298426,
    "Archery": 1526342056430141440,
    "Siege": 1526342109983014942
}
bekleme_listesi = {}

# Modal ve Select Menüsü
class RoleSelectView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Birlik seç", min_values=1, max_values=4, options=[
        discord.SelectOption(label="Infantry", value="Infantry"),
        discord.SelectOption(label="Cavalry", value="Cavalry"),
        discord.SelectOption(label="Archery", value="Archery"),
        discord.SelectOption(label="Siege", value="Siege")
    ])
    async def select_callback(self, i: discord.Interaction, select: discord.ui.Select):
        for role_id in ROLE_IDS.values():
            role = i.guild.get_role(role_id)
            if role in i.user.roles: await i.user.remove_roles(role)
        for val in select.values:
            role = i.guild.get_role(ROLE_IDS[val])
            if role: await i.user.add_roles(role)
        await i.response.send_message("Kayıt tamamlandı!", ephemeral=True)

class NicknameModal(discord.ui.Modal, title='RoK Kayıt Sistemi'):
    isim = discord.ui.TextInput(label='Oyun içi isminiz?', required=True)
    async def on_submit(self, i: discord.Interaction):
        await i.response.send_message("Birlik seçin:", view=RoleSelectView(), ephemeral=True)
        try: await i.user.edit(nick=str(self.isim))
        except: pass

# Bot Eventleri
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Sunucu Korunuyor!"))
    print(f'{bot.user} aktif!')

@bot.event
async def on_member_remove(m):
    bekleme_listesi[m.id] = asyncio.create_task(asyncio.sleep(7200))

@bot.event
async def on_member_join(m):
    if m.id in bekleme_listesi:
        try: await m.kick(reason="2 saat kuralı.")
        except: pass

# Komut
@bot.command()
@commands.has_permissions(administrator=True)
async def kayit(ctx):
    await ctx.message.delete()
    view = discord.ui.View(timeout=None)
    btn = discord.ui.Button(label="Kaydı Başlat", style=discord.ButtonStyle.primary)
    
    # En stabil yöntem: doğrudan modal'a bağlama
    async def btn_callback(i: discord.Interaction):
        await i.response.send_modal(NicknameModal())
        
    btn.callback = btn_callback
    view.add_item(btn)
    await ctx.send("Kayıt olmak için butona basın:", view=view)

bot.run(os.environ.get('DISCORD_TOKEN'))
