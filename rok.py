import discord
import os
from discord.ext import commands

# Render veya sunucu ortamından TOKEN'ı alıyoruz
TOKEN = os.environ.get('DISCORD_TOKEN')

# Sunucundaki ID'ler
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

# 1. Kayıt Modalı (İsim Girişi)
class NicknameModal(discord.ui.Modal, title='RoK Kayıt Sistemi'):
    oyuncu_ismi = discord.ui.TextInput(
        label='Oyun içi isminiz nedir?', 
        style=discord.TextStyle.short, 
        placeholder='Örn: Kaan', 
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # İsmi güncelle
        try:
            await interaction.user.edit(nick=str(self.oyuncu_ismi))
            await interaction.response.send_message(
                f"Memnun olduk {self.oyuncu_ismi}! Şimdi birlik türünü/türlerini seç:", 
                view=RoleSelectView(), 
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message("İsmini değiştiremiyorum (Yetkim yok). Lütfen rol hiyerarşisini kontrol et.", ephemeral=True)

# 2. Birlik Seçim Menüsü
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
        guild = interaction.guild
        user = interaction.user
        
        # Mevcut birlik rollerini temizle (isteğe bağlı, eskisini silsin istiyorsan)
        for role_id in ROLE_IDS.values():
            role = guild.get_role(role_id)
            if role in user.roles:
                await user.remove_roles(role)
        
        # Yeni seçilenleri ekle
        for role_name in select.values:
            role = guild.get_role(ROLE_IDS[role_name])
            if role:
                await user.add_roles(role)
        
        await interaction.response.send_message("Kayıt tamamlandı! Birlik rollerin güncellendi.", ephemeral=True)

# 3. Komut
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user} başarıyla başlatıldı ve komutlar senkronize edildi.')

@bot.tree.command(name="kayit", description="RoK kayıt işlemini başlatır")
async def kayit(interaction: discord.Interaction):
    # RoK rolü kontrolü
    rok_rol = interaction.guild.get_role(ROK_ROL_ID)
    if not rok_rol or rok_rol not in interaction.user.roles:
        await interaction.response.send_message("Bu komutu kullanmak için 'RoK' rolüne sahip olmalısınız.", ephemeral=True)
        return

    await interaction.response.send_modal(NicknameModal())

bot.run(TOKEN)