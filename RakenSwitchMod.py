import logging
from .. import loader, utils
import telethon

logger = logging.getLogger(__name__)


async def register(cb):
	cb(KeyboardSwitcherMod())


@loader.tds
class KeyboardSwitcherMod(loader.Module):
	"""Зміна розкладки клавіатури в тексті"""
	strings = {
		"name": "RakenSwitchMod"}
	
async def switchuacmd(self, message):
	"""квіточки."""
	UaKeys = """'йцукенгшщзхїфівапролджєячсмитьбю.'"№;%:?ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄ/ЯЧСМИТЬБЮ,"""
	EnKeys = """`qwertyuiop[]asdfghjkl;'zxcvbnm,./~@#$%^&QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?"""

	if message.is_reply:
		reply = await message.get_reply_message()
		text = reply.raw_text
		if not text:
			await message.edit('Тут тексту нема...')
			return
		change = str.maketrans(UaKeys + EnKeys, EnKeys + UaKeys)
		text = str.translate(text, change)

		if message.sender_id != reply.sender_id:
			await message.edit(text)
		else:
			await message.delete()
			await reply.edit(text)

	else:
		text = utils.get_args_raw(message)
		if not text:
			await message.edit('Тут тексту нема...')
			return
		change = str.maketrans(UaKeys + EnKeys, EnKeys + UaKeys)
		text = str.translate(text, change)
		await message.edit(text)

async def switchrucmd(self, message):
	"""квіточки."""
	RuKeys = """'йцукенгшщзхъфывапролджэячсмитьбю.'"№;%:?ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"""
	EnKeys = """`qwertyuiop[]asdfghjkl;'zxcvbnm,./~@#$%^&QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?"""

	if message.is_reply:
		reply = await message.get_reply_message()
		text = reply.raw_text
		if not text:
			await message.edit('Тут текста нету...')
			return
		change = str.maketrans(RuKeys + EnKeys, EnKeys + RuKeys)
		text = str.translate(text, change)
		
		if message.sender_id != reply.sender_id:
			await message.edit(text)
		else:
			await message.delete()
			await reply.edit(text)

	else:
		text = utils.get_args_raw(message)
		if not text:
			await message.edit('Тут текста нету...')
			return
		change = str.maketrans(RuKeys + EnKeys, EnKeys + RuKeys)
		text = str.translate(text, change)
		await message.edit(text)
