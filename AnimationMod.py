from .. import loader, utils
import asyncio
from asyncio import sleep

@loader.tds
class AnimationMod(loader.Module):
  strings = {"name": "AnimationMod"}
  
  async def client_ready(self, client, db):
    self.client = client
    
  @loader.owner
  async def heartcmd(self, message):
    args = utils.get_args_raw(message)
    try:
      args = int(args)
      for _ in range(args):
              for heart in ['❤️ㅤ', '️🧡ㅤ', '💛ㅤ', '💚ㅤ', '💙ㅤ', '💜ㅤ']:
                await message.edit(heart)
                await sleep(0.5)
    except ValueError:
      await message.edit("〰️ Не хватает аргументов.")
          
  @loader.owner
  async def clockcmd(self, message):
    args = utils.get_args_raw(message)
    try:
      args = int(args)
      for _ in range(args):
        for clock in ['🕛', '🕐', '🕑' ,'🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙']:
          await message.edit(clock)
          await sleep(0.3)    
    except ValueError:
      await message.edit("〰️ Не хватает аргументов.")
        
  @loader.owner
  async def mooncmd(self, message):
    args = utils.get_args_raw(message)
    try:
      args = int(args)
      for _ in range(args):
        for moon in ['🌕ㅤ', '🌖ㅤ', '🌗ㅤ', '🌘ㅤ', '🌑ㅤ' ,'🌒ㅤ', '🌓ㅤ', '🌔ㅤ']:
          await message.edit(moon)
          await sleep(0.3)
    except ValueError:
      await message.edit("〰️ Не хватает аргументов.")
  
  @loader.owner
  async def moonfcmd(self, message):
    """Используй .moonf <аргументы>"""
    args = utils.get_args_raw(message)
    try:
      args = int(args)
      for _ in range(args):
        for moonf in ['🌚ㅤ', '🌝ㅤ']:
          await message.edit(moonf)
          await sleep(0.5)
    except ValueError:
      await message.edit("〰️ Не хватает аргументов.")   
   
  @loader.owner
  async def mooncmd(self, message):
    args = utils.get_args_raw(message)
    try:
      args = int(args)
      for _ in range(args):
        for moon in ['🌕ㅤ', '🌖ㅤ', '🌗ㅤ', '🌘ㅤ', '🌑ㅤ' ,'🌒ㅤ', '🌓ㅤ', '🌔ㅤ']:
          await message.edit(moon)
          await sleep(0.3)
    except ValueError:
      await message.edit("〰️ Не хватает аргументов.")
  
  @loader.owner
  async def portalcmd(self, message):
    """Используй .portal <аргументы>"""
    args = utils.get_args_raw(message)
    try:
      args = int(args)
      for _ in range(args):
        for portal in ['🕳 \n \n \n 🕳', '🕳 \n 🎾 \n \n 🕳', '🕳 \n \n 🎾 \n 🕳']:
          await message.edit(portal)
          await sleep(0.1)
    except ValueError:
      await message.edit("〰️ Не хватает аргументов.")    
  
  @loader.owner
  async def soncmd(self, message):
    """Используй .son <аргументы>"""
    args = utils.get_args_raw(message)
    try:
      args = int(args)
      for _ in range(args):
        for son in ['\nㅤ \n ㅤ \n ㅤ \n 😴ㅤ', 'ㅤ\n ㅤ \n ㅤ   💤 \n 😴', 'ㅤ \n ㅤ \nㅤ        💤 \n \n 😴']:
          await message.edit(son)
          await sleep(0.1)
    except ValueError:
      await message.edit("〰️ Не хватает аргументов.")    
  
