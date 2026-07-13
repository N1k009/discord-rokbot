import discord
import os
from discord.ext import commands

TOKEN = os.environ.get('DISCORD_TOKEN')

ROK_ROL_ID = 1525779899745308712
ROLE_IDS = {
    "Infantry": 1526342009596547142,
    "Cavalry": 1526341870899298426,
    "Archery": 1526342056430141440,
    "Siege": 1526342109983014942
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class NicknameModal(discord.ui.Modal, title='RoK Kayıt Sistemi'):
    oyuncu_ismi = discord.ui.TextInput(label='Oyun içi isminiz nedir?', placeholder='Örn: Kaan', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.user.edit(nick=str(self.oyuncu_ismi))
        await interaction.response.send_message(f"İsminiz güncellendi! Birlik rolünüzü seçin:", view=RoleSelectView(), ephemeral=True)

class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Birlik türünü seç (Çoklu seçim yapabilirsin)",
        min_values=1, max_values=4,
        options=[
            discord.SelectOption(label="Infantry", value="Infantry"),
            discord.SelectOption(label="Cavalry", value="Cavalry"),
            discord.SelectOption(label="Archery", value="Archery"),
            discord.SelectOption(label="Siege", value="Siege"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        for role_id in ROLE_IDS.values():
            role = interaction.guild.get_role(role_id)
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
        for role_name in select.values:
            role = interaction.guild.get_role(ROLE_IDS[role_name])
            if role:
                await interaction.user.add_roles(role)
        await interaction.response.send_message("Kayıt tamamlandı!", ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} hazır!')

@bot.command(name="kayit")
async def kayit(ctx):
    # 1. Mesajı hemen sil
    await ctx.message.delete()
    
    # 2. RoK rolü kontrolü
    rok_rol = ctx.guild.get_role(ROK_ROL_ID)
    if rok_rol not in ctx.author.roles:
        await ctx.send("Bu komutu kullanmak için RoK rolüne sahip olmalısınız.", delete_after=5)
        return

    # 3. Modal göndermek için etkileşim gerekiyor (Slash komutunda olduğu gibi doğrudan modal açılmaz)
    # Prefix komutlarında modal açmak için özel bir yapı gerek. 
    # Bunun yerine kullanıcıya bir butonlu mesaj gönderelim, butona basınca modal açılsın.
    view = discord.ui.View()
    button = discord.ui.Button(label="Kaydı Başlat", style=discord.ButtonStyle.primary)
    
    async def button_callback(interaction: discord.Interaction):
        await interaction.response.send_modal(NicknameModal())
        
    button.callback = button_callback
    view.add_item(button)
    
    await ctx.send("Kayıt olmak için aşağıdaki butona basın:", view=view)

bot.run(TOKEN)
