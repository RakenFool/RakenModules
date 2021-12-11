from .. import loader

class DotMod(loader.Module):
	"""Данный модуль ставит точку в конце сообщения. Credit: @creative_tg1. Что я сделал? Запихнул модуль в ссылку, сделал команду только для заглавной буквы в начале."""
	strings = {"name": "Dot"}
	dot = 0
	async def dotplusoncmd(self, message):
		""".dotpluson включает модуль Dot+."""
		dot = 11
		await message.edit("<b>Dot+ On.</b>")	
	async def dotoncmd(self, message):
		""".doton включает модуль Dot."""
		dot = 21
		await message.edit("<b>Dot On.</b>")		
	async def dotplusoffcmd(self, message):
		""".dotoff выключает модуль Dot+."""
		dot = 1
		await message.edit("<b>Dot+ Off.</b>")		
	async def dotoffcmd(self, message):
		""".dotoff выключает модуль Dot."""
		dot = 1
		await message.edit("<b>Dot Off.</b>")	
	async def watcher(self, message):
		if dot == 11:
			me = (await message.client.get_me())
		if message.sender_id == me.id:
			text = message.text.lower()
			textup = text[0].upper()
			textdown = text[1:]
			txt = textup + textdown
			lentxt = len(txt) - 1
			if txt[lentxt] == "?" or txt[lentxt] == "!" or txt[lentxt] == ".":
				await message.edit(txt)
			elif dot == 21:
				me = (await message.client.get_me())
				if message.sender_id == me.id:
					text = message.text.lower()
					textup = text[0].upper()
					textdown = text[1:]
					txt = textup + textdown
					lentxt = len(txt) - 1
			else:
				await message.edit(txt + ".")
