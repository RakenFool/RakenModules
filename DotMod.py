from .. import loader

class DotMod(loader.Module):
	"""Данный модуль данный модуль делает первую букву сообщения заглавной. Credit: @creative_tg1. Что я сделал? Запихнул модуль в ссылку, сделал команду только для заглавной буквы в начале."""
	strings = {"name": "Dot"}
	dot = 0	
	async def dotplusoncmd(self, message):
		""".dotpluson включает модуль Dot+."""
		self.truefalse = True
		await message.edit("<b>Dot+ On.</b>")			
	async def dotplusoffcmd(self, message):
		""".dotoff выключает модуль Dot+."""
		self.truefalse = False
		await message.edit("<b>Dot+ Off.</b>")		
	async def watcher(self, message):
		if self.truefalse == True:			
			me = (await message.client.get_me())
			if message.sender_id == me.id:
				text = message.text.lower()
				txt = text[0].upper()
				await message.edit(txt)
