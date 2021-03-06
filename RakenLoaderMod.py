import logging
import importlib
import sys
import uuid
import asyncio
import urllib
import os
import re
import requests

from importlib.machinery import ModuleSpec
from importlib.abc import SourceLoader

from .. import loader, utils

logger = logging.getLogger(__name__)

VALID_URL = r"[-[\]_.~:/?#@!$&'()*+,;%<=>a-zA-Z0-9]+"
VALID_PIP_PACKAGES = re.compile(r"^\s*# requires:(?: ?)((?:{url} )*(?:{url}))\s*$".format(url=VALID_URL), re.MULTILINE)
USER_INSTALL = "PIP_TARGET" not in os.environ and "VIRTUAL_ENV" not in os.environ


class StringLoader(SourceLoader):  # pylint: disable=W0223 # False positive, implemented in SourceLoader
    """Load a python module/file from a string"""
    def __init__(self, data, origin):
        if isinstance(data, str):
            self.data = data.encode("utf-8")
        else:
            self.data = data
        self.origin = origin

    def get_code(self, fullname):
        source = self.get_source(fullname)
        if source is None:
            return None
        return compile(source, self.origin, "exec", dont_inherit=True)

    def get_filename(self, fullname):
        return self.origin

    def get_data(self, filename):  # pylint: disable=W0221,W0613
        # W0613 is not fixable, we are overriding
        # W0221 is a false positive assuming docs are correct
        return self.data


def unescape_percent(text):
    i = 0
    ln = len(text)
    is_handling_percent = False
    out = ""
    while i < ln:
        char = text[i]
        if char == "%" and not is_handling_percent:
            is_handling_percent = True
            i += 1
            continue
        if char == "d" and is_handling_percent:
            out += "."
            is_handling_percent = False
            i += 1
            continue
        out += char
        is_handling_percent = False
        i += 1
    return out


@loader.tds
class Loader(loader.Module):
    """Модуль для загрузки других модулей"""
    strings = {"name": "RakenLoaderMod",
               "repo_config_doc": "✅Полностью квалифицораванная ссылка из репо.",
               "avail_header": "<b>✅Доступен в официальном репо.</b>",
               "select_preset": "<b>❌Выберете пресет.</b>",
               "no_preset": "<b>❌Пресет не найден.с</b>",
               "preset_loaded": "<b>✅Пресет загружён.</b>",
               "no_module": "<b>❌Модуль недоступный в репо.</b>",
               "no_file": "<b>❌Файл не найден. </b>",
               "provide_module": "<b>❌Предоставьте модуль для загрузки.</b>",
               "bad_unicode": "<b>❌Неправильный формат юникода в модуле.</b>",
               "load_failed": "<b>❌ Ты опять ошибся. Чекай логи, чё сказать: </b> (<code> .logs error </code>)" ,
               "loaded": "<b>✅Модуль загружён. </b>",
               "no_class": "<b>❌Укажи какой модуль нужно выгрузить. </b>",
               "unloaded": "<b>✅Модуль выгружен. </b>",
               "not_unloaded": "<b>❌Модуль не выгружен. </b>",
               "requirements_failed": "<b>❌Загрузка потребностей не удалась.</b>",
               "requirements_installing": "<b>✅Загрузка потребностей...</b>",
               "requirements_restart": "<b>ℹ️Потребности загружены, но нужна перезагрузка.</b>"}

    def __init__(self):
        super().__init__()
        self.config = loader.ModuleConfig("MODULES_REPO",
                                          "https://gitlab.com/friendly-telegram/modules-repo/-/raw/master",
                                          lambda m: self.strings("repo_config_doc", m))

    @loader.owner
    async def dlmodcmd(self, message):
        """.dlmod <ссылка на модуль> - установить модуль"""
        args = utils.get_args(message)
        if args:
            if await self.download_and_install(args[0], message):
                self._db.set(__name__, "loaded_modules",
                             list(set(self._db.get(__name__, "loaded_modules", [])).union([args[0]])))
        else:
            text = utils.escape_html("\n".join(await self.get_repo_list("full")))
            await utils.answer(message, "<b>" + self.strings("avail_header", message)
                               + "</b>\n<code>" + text + "</code>")

    @loader.owner
    async def dlpresetcmd(self, message):
        """Set preset. Defaults to full"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("select_preset", message))
            return
        try:
            await self.get_repo_list(args[0])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                await utils.answer(message, self.strings("no_preset", message))
                return
            else:
                raise
        self._db.set(__name__, "chosen_preset", args[0])
        self._db.set(__name__, "loaded_modules", [])
        self._db.set(__name__, "unloaded_modules", [])
        await utils.answer(message, self.strings("preset_loaded", message))

    async def _get_modules_to_load(self):
        todo = await self.get_repo_list(self._db.get(__name__, "chosen_preset", None))
        todo = todo.difference(self._db.get(__name__, "unloaded_modules", []))
        todo.update(self._db.get(__name__, "loaded_modules", []))
        return todo

    async def get_repo_list(self, preset=None):
        if preset is None:
            preset = "minimal"
        r = await utils.run_sync(requests.get, self.config["MODULES_REPO"] + "/" + preset + ".txt")
        r.raise_for_status()
        return set(filter(lambda x: x, r.text.split("\n")))

    async def download_and_install(self, module_name, message=None):
        if urllib.parse.urlparse(module_name).netloc:
            url = module_name
        else:
            url = self.config["MODULES_REPO"] + "/" + module_name + ".py"
        r = await utils.run_sync(requests.get, url)
        if r.status_code == 404:
            if message is not None:
                await utils.answer(message, self.strings("no_module", message))
            return False
        r.raise_for_status()
        return await self.load_module(r.content.decode("utf-8"), message, module_name, url)

    @loader.owner
    async def loadmodcmd(self, message):
        """Loads the module file"""
        if message.file:
            msg = message
        else:
            msg = (await message.get_reply_message())
        if msg is None or msg.media is None:
            args = utils.get_args(message)
            if args:
                try:
                    path = args[0]
                    with open(path, "rb") as f:
                        doc = f.read()
                except FileNotFoundError:
                    await utils.answer(message, self.strings("no_file", message))
                    return
            else:
                await utils.answer(message, self.strings("provide_module", message))
                return
        else:
            path = None
            doc = await msg.download_media(bytes)
        logger.debug("Loading external module...")
        try:
            doc = doc.decode("utf-8")
        except UnicodeDecodeError:
            await utils.answer(message, self.strings("bad_unicode", message))
            return
        if path is not None:
            await self.load_module(doc, message, origin=path)
        else:
            await self.load_module(doc, message)

    async def load_module(self, doc, message, name=None, origin="<string>", did_requirements=False):
        if name is None:
            uid = "__extmod_" + str(uuid.uuid4())
        else:
            uid = name.replace("%", "%%").replace(".", "%d")
        
        try:
            try:
                spec = ModuleSpec(module_name, StringLoader(doc, origin), origin=origin)
                instance = self.allmodules.register_module(spec, module_name)
            except ImportError:
                logger.info("Module loading failed, attemping dependency installation", exc_info=True)
                # Let's try to reinstall dependencies
                requirements = list(filter(lambda x: x and x[0] not in ("-", "_", "."),
                                           map(str.strip, VALID_PIP_PACKAGES.search(doc)[1].split(" "))))
                logger.debug("Installing requirements: %r", requirements)
                if not requirements:
                    raise  # we don't know what to install
                if did_requirements:
                    if message is not None:
                        await utils.answer(message, self.strings("requirements_restart", message))
                    return True  # save to database despite failure, so it will work after restart
                if message is not None:
                    await utils.answer(message, self.strings("requirements_installing", message))
                pip = await asyncio.create_subprocess_exec(sys.executable, "-m", "pip", "install",
                                                           "--upgrade", "-q", "--disable-pip-version-check",
                                                           "--no-warn-script-location",
                                                           *["--user"] if USER_INSTALL else [],
                                                           *requirements)
                rc = await pip.wait()
                if rc != 0:
                    if message is not None:
                        await utils.answer(message, self.strings("requirements_failed", message))
                    return False
                else:
                    importlib.invalidate_caches()
                    return await self.load_module(doc, message, name, origin, True)  # Try again
        except BaseException:  # That's okay because it might try to exit or something, who knows.
            logger.exception("Loading external module failed.")
            if message is not None:
                await utils.answer(message, self.strings("load_failed", message))
            return False
        try:
            self.allmodules.send_config_one(instance, self._db, self.babel)
            await self.allmodules.send_ready_one(instance, self._client, self._db, self.allclients)
        except Exception:
            logger.exception("Module threw")
            if message is not None:
                await utils.answer(message, self.strings("load_failed", message))
            return False
        if message is not None:
            await utils.answer(message, self.strings("loaded", message))
        return True

    @loader.owner
    async def unloadmodcmd(self, message):
        """Unload module by class name"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("no_class", message))
            return
        clazz = args[0]
        worked = self.allmodules.unload_module(clazz)
        without_prefix = []
        for mod in worked:
            assert mod.startswith("friendly-telegram.modules."), mod
            without_prefix += [unescape_percent(mod[len("friendly-telegram.modules."):])]
        it = set(self._db.get(__name__, "loaded_modules", [])).difference(without_prefix)
        self._db.set(__name__, "loaded_modules", list(it))
        it = set(self._db.get(__name__, "unloaded_modules", [])).union(without_prefix)
        self._db.set(__name__, "unloaded_modules", list(it))
        if worked:
            await utils.answer(message, self.strings("unloaded", message))
        else:
            await utils.answer(message, self.strings("not_unloaded", message))

    async def _update_modules(self):
        todo = await self._get_modules_to_load()
        await asyncio.gather(*[self.download_and_install(mod) for mod in todo])

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        await self._update_modules()
