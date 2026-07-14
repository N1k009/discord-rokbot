import discord
import os
import asyncio
from discord.ext import commands
from keepalive import keep_alive

# Web sunucusunu başlat (Railway'in uyumamasını sağlar)
keep_alive()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- AYARLAR ---
ROK_ROL_ID = 1525779899745308712
ROLE_IDS = {
    "Infantry": 1526342009596547142,
    "Cavalry": 1526341870899298426,
    "Archery": 1526342056430141440,
    "Siege": 1526342109983014942
}
bekleme_listesi = {}

# --- MODAL VE VIEW (Kayıt Sistemi) ---
class NicknameModal(discord.ui.Modal, title='RoK Kayıt Sistemi'):
    oyuncu_ismi = discord.ui.TextInput(label='Oyun içi isminiz nedir?', style=discord.TextStyle.short, placeholder='Örn: Kaan', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.user.edit(nick=str(self.oyuncu_ismi))
            message = f"✅ İsminiz '{self.oyuncu_ismi}' olarak güncellendi! Birlik rolünüzü seçin:"
        except:
            message = "⚠️ İsminizi değiştiremedim (Yetki hatası). Yine de birlik rolünüzü seçebilirsiniz:"
        await interaction.response.send_message(message, view=RoleSelectView(), ephemeral=True)

class RoleSelectView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Birlik türünü seç (Çoklu seçim yapabilirsin)", min_values=1, max_values=4, options=[
        discord.SelectOption(label="Infantry", value="Infantry"),
        discord.SelectOption(label="Cavalry", value="Cavalry"),
        discord.SelectOption(label="Archery", value="Archery"),
        discord.SelectOption(label="Siege", value="Siege")
    ])
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        for role_id in ROLE_IDS.values():
            role = interaction.guild.get_role(role_id)
            if role in interaction.user.roles: await interaction.user.remove_roles(role)
        for role_name in select.values:
            role = interaction.guild.get_role(ROLE_IDS[role_name])
            if role: await interaction.user.add_roles(role)
        await interaction.response.send_message("Kayıt tamamlandı! Rolleriniz güncellendi.", ephemeral=True)

# --- GUARD (KORUMA) SİSTEMİ ---
async def bekleme_suresi(user_id):
    await asyncio.sleep(7200) # 2 saat
    if user_id in bekleme_listesi: del bekleme_listesi[user_id]

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Sunucu Korunuyor!"))
    print(f'{bot.user} başarıyla başlatıldı ve koruma aktif!')

@bot.event
async def on_member_remove(member):
    if member.id in bekleme_listesi: bekleme_listesi[member.id].cancel()
    bekleme_listesi[member.id] = asyncio.create_task(bekleme_suresi(member.id))

@bot.event
async def on_member_join(member):
    if member.id in bekleme_listesi:
        try:
            await member.send("Sunucuya tekrar girmek için 2 saatlik süren dolmadı.")
            await member.kick(reason="2 saatlik yeniden giriş kısıtlaması.")
        except: pass

# --- GİZLİ VE KALICI KAYIT KOMUTU ---
@bot.command()
@commands.has_permissions(administrator=True)
async def kayit(ctx):
    await ctx.message.delete() # Mesajı sildi, iz bırakmadı
    view = discord.ui.View()
    button = discord.ui.Button(label="Kaydı Başlat", style=discord.ButtonStyle.primary)
    
    async def button_callback(interaction: discord.Interaction):
        await interaction.response.send_modal(NicknameModal())
    
    button.callback = button_callback
    view.add_item(button)
    await ctx.send("Kayıt olmak için butona basın:", view=view)

bot.run(os.environ.get('DISCORD_TOKEN'))