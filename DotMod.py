from .. import loader

class DotMod(loader.Module):
	"""Данный модуль данный модуль делает первую букву сообщения заглавной. Credit: @creative_tg1. Что я сделал? Запихнул модуль в ссылку, сделал команду только для заглавной буквы в начале."""
	strings = {"name": "Dot"}
	
	async def dotplusoncmd(self, message):
		""".doton включает модуль Dot."""
		self.truefalse = True
		await message.edit("<b>Dot On.</b>")			
	async def dotoffcmd(self, message):
		""".dotoff выключает модуль Dot."""
		self.truefalse = False
		await message.edit("<b>Dot Off.</b>")		
	async def watcher(self, message):
		if self.truefalse == True:			
			me = (await message.client.get_me())
			if message.sender_id == me.id:
				text = message.text.lower()
				textup = text[0].upper()
				textdown = text[1:]
				txt = textup + textdown
				lentxt = len(txt) - 1
				await message.edit(txt)
					
				
