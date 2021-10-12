import logging
import io, inspect

from telethon.tl.functions.channels import JoinChannelRequest

from .. import loader, utils, main, security

logger = logging.getLogger(__name__)


@loader.tds
class HelpMod(loader.Module):
    """Помощь по командам юзербота"""
    strings = {"name": "RakenHelpMod",
               "bad_module": '<b>Ошибка: </b>❌ Модуля "<code>{}</code>" у тебя нет!',
               "single_mod_header": "<b>ℹ️ Информация об этом модуле</b> <i>{}</i>:\n",
               "single_cmd": "\n {}\n",
               "undoc_cmd": "😢 <b>Ошибка:</b> У меня нет инфы про этот модуль",
               "all_header": '💾Список твоих модулей: (их {} штук): \n\nℹ️ Для выполнения команды <code>.*ваша команда*</code>\n ',
               "mod_tmpl": '\n <a href="tg://user?id={}">👉</a> {}  ',
               "first_cmd_tmpl":"({}",
               "cmd_tmpl": ", {}",
               "raken": "raken"}

    @loader.unrestricted
    async def helpcmd(self, message):
        """.help [module]"""
        args = utils.get_args_raw(message)
        id = message.sender_id
        if args:
            module = None
            for mod in self.allmodules.modules:
                if mod.strings("name", message).lower() == args.lower():
                    module = mod
            if module is None:
                await utils.answer(message, self.strings("bad_module", message).format(args))
                return
            # Translate the format specification and the module separately
            try:
                name = module.strings("name", message)
            except KeyError:
                name = getattr(module, "name", "ERROR")
            reply = self.strings("single_mod_header", message).format(utils.escape_html(name),
                                                                      utils.escape_html((self.db.get(main.__name__,
                                                                                                     "command_prefix",
                                                                                                     False) or ".")[0]))
            if module.__doc__:
                reply += "\n"+"\n".join("  " + t for t in utils.escape_html(inspect.getdoc(module)).split("\n"))
            else:
                logger.warning("Module %s is missing docstring!", module)
            commands = {name: func for name, func in module.commands.items()
                        if await self.allmodules.check_security(message, func)}
            for name, fun in commands.items():
                reply += self.strings("single_cmd", message).format(name)
                if fun.__doc__:
                    reply += utils.escape_html("\n".join("  " + t for t in inspect.getdoc(fun).split("\n")))
                else:
                    reply += self.strings("undoc_cmd", message)
        else:
            count = 0
            for i in self.allmodules.modules:
                if len(i.commands) != 0:
                    count += 1
            reply = self.strings("all_header", message).format(count)
            
            for mod in self.allmodules.modules:
                if len(mod.commands) != 0:
                    try:
                        name = mod.strings("name", message)
                    except KeyError:
                        name = getattr(mod, "name", "ERROR")
                    reply += self.strings("mod_tmpl", message).format(id, name)
                    first = True
                    commands = [name for name, func in mod.commands.items()
                                if await self.allmodules.check_security(message, func)]
                    for cmd in commands:
                        if first:
                            reply += self.strings("first_cmd_tmpl", message).format(cmd)
                            first = False
                        else:
                            reply += self.strings("cmd_tmpl", message).format(cmd)
                    reply += ")"
        
        await utils.answer(message, reply)

    @loader.unrestricted
    async def rakenHelp(self, message):
        """RakenHelpMod """
        await (await self.client.get_messages(self.strings("mybot_tg", message), ids=118)).forward_to(message.to_id)
        await message.delete()
        await self.client(JoinChannelRequest(self.strings("mybot_tg", message)))
    
        
    async def client_ready(self, client, db):
        self.client = client
        self.is_bot = await client.is_bot()
        self.db = db

    async def mlcmd(self, message):
        """Вывести ссылку на модуль"""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit('<b>Ошибка ❌:</b> Отсутствуют аргументы')

        await message.edit('Ищем...')

        try:
            f = ' '.join([x.strings["name"] for x in self.allmodules.modules if args.lower() == x.strings["name"].lower()])
            r = inspect.getmodule(next(filter(lambda x: args.lower() == x.strings["name"].lower(), self.allmodules.modules)))
            link = str(r).split('(')[1].split(')')[0]
            if "http" not in link:
                text = f"Модуль {f}:"
            else:
                text = f"<a href=\"{link}\">📎 Ссылка</a> на модуль {f}: <code>{link}</code>"

            out = io.BytesIO(r.__loader__.data)
            out.name = f + ".py"
            out.seek(0)

            await message.respond(text, file=out)
            await message.delete()
        except:
            return await message.edit("<b>🤔 Неизвестная ошибка</b>")
