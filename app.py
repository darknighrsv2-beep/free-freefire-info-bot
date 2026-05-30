import os
import discord
from discord.ext import commands
import requests
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# CONFIGURACIÓN DE INTENTS (Esto es lo que faltaba y causaba el error)
intents = discord.Intents.default()
intents.message_content = True  # Permite al bot leer el contenido de los mensajes

# Inicialización del Bot con los intents corregidos
bot = commands.Bot(command_prefix='!', description="Bot de Info Free Fire", intents=intents)

# Configuración del servidor Web (Flask) para Render / Railway
app = Flask('')

@app.route('/')
def home():
    return "¡El bot está vivo y funcionando!"

def run():
    # Render asigna automáticamente un puerto, si no usa el 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# EVENTOS DEL BOT DE DISCORD
@bot.event
def on_ready():
    print(f'=== CONFIGURACIÓN EXITOSA ===')
    print(f'Conectado como: {bot.user.name}')
    print(f'ID del Bot: {bot.user.id}')
    print(f'=============================')

# COMANDO !info [UID]
@bot.command()
def info(ctx, uid: str = None):
    if uid is None:
        await ctx.send("❌ **Error:** Por favor, proporciona un UID de Free Fire. Ejemplo: `!info 12345678`滑")
        return

    await ctx.send(f"🔍 Buscando información para el UID: `{uid}`... Por favor, espera.")

    # API externa que utiliza el repositorio para obtener los datos de Free Fire
    url = f"https://freefireapi.com.br/api/search?id={uid}&lang=es"

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Construcción del mensaje incrustado (Embed) con los datos corregidos
            embed = discord.Embed(
                title=f"📊 Información de Cuenta - Free Fire", 
                color=discord.Color.orange()
            )
            embed.add_field(name="👤 Nombre en juego", value=data.get('name', 'No encontrado'), inline=True)
            embed.add_field(name="🆔 UID", value=uid, inline=True)
            embed.add_field(name="📈 Nivel", value=data.get('level', 'N/A'), inline=True)
            embed.add_field(name="🏆 Rango BR", value=data.get('rank', 'No encontrado'), inline=True)
            embed.add_field(name="👥 Clan", value=data.get('clan_name', 'Sin Clan'), inline=True)
            embed.add_field(name="🌍 Región", value=data.get('region', 'N/A'), inline=True)
            
            embed.set_footer(text="BooyahBot • Información en tiempo real")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ No se encontró información para ese UID o la API está caída temporalmente.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la API: {e}")
        await ctx.send("⚠️ Hubo un error al conectar con el servidor de Free Fire. Inténtalo más tarde.")

# ENCENDER EL BOT Y EL SERVIDOR WEB
if __name__ == "__main__":
    # Inicia el servidor web en segundo plano
    keep_alive()
    
    # Obtiene el Token secreto desde el archivo .env
    token = os.getenv('TOKEN')
    
    if token:
        bot.run(token)
    else:
        print("❌ ERROR CRÍTICO: No se encontró la variable 'TOKEN' en el archivo .env")
