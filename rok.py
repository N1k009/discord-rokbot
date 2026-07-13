import discord
import os
from discord.ext import commands

# Render üzerinden TOKEN'ı alıyoruz
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
intents.members = True  # İsim değiştirmek için zorunlu
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 1. İsim Giriş Modalı
class NicknameModal(discord.ui.Modal, title='RoK Kayıt Sistemi'):
    oyuncu_ismi = discord.ui.TextInput(label='Oyun içi isminiz nedir?', style=discord.TextStyle.short, placeholder='Örn: Kaan', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # Yetki hatası alsa bile çökmemesi için try-except bloğu
        try:
            await interaction.user.edit(nick=str(self.oyuncu_ismi))
            message = f"İsminiz {self.oyuncu_ismi} olarak güncellendi! Birlik rolünüzü seçin:"
        except discord.Forbidden:
            message = "İsmini değiştiremedim (Sunucu sahibi veya yetkili olduğun için). Yine de birlik rolünü seçebilirsin:"
            
        await interaction.response.send_message(message, view=RoleSelectView(), ephemeral=True)

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
        # Eskileri temizle ve yenileri ekle
        for role_id in ROLE_IDS.values():
            role = interaction.guild.get_role(role_id)
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
        
        for role_name in select.values:
            role = interaction.guild.get_role(ROLE_IDS[role_name])
            if role:
                await interaction.user.add_roles(role)
        
        await interaction.response.send_message("Kayıt tamamlandı! Rolleriniz güncellendi.", ephemeral=True)

# 3. Komut
@bot.event
async def on_ready():
    print(f'{bot.user} başarıyla başlatıldı!')

@bot.command(name="kayit")
async def kayit(ctx):
    # Mesajı sil
    await ctx.message.delete()
    
    # RoK rolü kontrolü
    rok_rol = ctx.guild.get_role(ROK_ROL_ID)
    if rok_rol not in ctx.author.roles:
        await ctx.send("Bu komutu kullanmak için RoK rolüne sahip olmalısınız.", delete_after=5)
        return

    # Kaydı başlat butonu
    view = discord.ui.View()
    button = discord.ui.Button(label="Kaydı Başlat", style=discord.ButtonStyle.primary)
    
    async def button_callback(interaction: discord.Interaction):
        await interaction.response.send_modal(NicknameModal())
        
    button.callback = button_callback
    view.add_item(button)
    
    await ctx.send("Kayıt olmak için butona basın:", view=view)

bot.run(TOKEN)
