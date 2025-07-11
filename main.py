import discord
from discord.ext import commands
import wavelink
import os

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 및 명령어 동기화 완료!")
    if not wavelink.Pool.nodes:
        node = wavelink.Node(
            host='my-lavalink-app-production.up.railway.app',  # 배포한 Lavalink 주소!
            port=2333,
            password='youshallnotpass',
            https=False
        )
        await wavelink.Pool.connect(nodes=[node], client=bot)
    print("🎶 Lavalink 연결 성공")

@bot.tree.command(name="재생", description="유튜브 링크 또는 검색어로 노래 재생")
async def play(interaction: discord.Interaction, 검색어: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("먼저 음성 채널에 들어가 주세요!", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    player = await wavelink.Pool.get_node().get_player(channel.guild)
    if not player.is_connected():
        await player.connect(channel.id)
    tracks = await wavelink.Pool.get_node().search(검색어)
    if not tracks or not tracks.tracks:
        await interaction.response.send_message("노래를 찾지 못했어요!", ephemeral=True)
        return

    track = tracks.tracks[0]
    await player.play(track)
    await interaction.response.send_message(f"🎶 {track.info['title']} 재생 중!")

@bot.tree.command(name="정지", description="노래 정지")
async def stop(interaction: discord.Interaction):
    player = await wavelink.Pool.get_node().get_player(interaction.guild)
    if player and player.is_playing:
        await player.stop()
        await interaction.response.send_message("⏹️ 정지했어요!")
    else:
        await interaction.response.send_message("재생 중인 곡이 없어요.", ephemeral=True)

bot.run(TOKEN)
