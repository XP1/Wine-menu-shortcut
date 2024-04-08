#!/usr/bin/env python
"""
Copyright 2024 XP1

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import re
import sys
import copy
import argparse
import subprocess
import traceback
from re import Match, Pattern
from pathlib import Path, PureWindowsPath
import pylnk3.helpers
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROGRAM = {
    "name": "Create Wine menu shortcut",
    "version": "1.00",
    "description": "Creates an LNK shortcut file for a provided executable and then uses winemenubuilder to add a Wine menu item."
}

CONFIG = {
    "target_unix_path": None,
    "wine_bin_path": None,
    "auto": False,
    "link_location_index": None,
    "lnk_name": None,
    "lnk_unix_path": None,
    "lnk_arguments": None,
    "lnk_description": None,
    "lnk_icon_file": None,
    "lnk_icon_index": 0,
    "lnk_work_dir": None,
    "lnk_window_mode": None
}


def handle_exception(exception) -> None:
    exception_text = "".join(traceback.format_exception(exception))
    logger.error(exception_text)
    print("Exception:")
    print(exception_text)
    print()


def fetch_text_file(path: str) -> str:
    with open(path, encoding="utf-8") as file:
        text = file.read()
        return text


def write_text_file(path: str, data: any) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(data)


def contains_text(text: str) -> bool:
    return (isinstance(text, str) and len(text.strip()) > 0)


class NameLinkLocation():
    # https://source.winehq.org/git/wine.git/blob/HEAD:/programs/winemenubuilder/winemenubuilder.c#l1473
    name_link_location = {
        "Common programs": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        "Programs": r"C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
        "Common start menu": r"C:\ProgramData\Microsoft\Windows\Start Menu",
        "Start menu": r"C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Start Menu",
        "Common desktop": r"C:\Users\Public\Desktop",
        "Desktop": r"C:\Users\<username>\Desktop",
        "Common startup": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp",
        "Startup": r"C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\StartUp"
    }
    number_of_name_link_locations = len(name_link_location)

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def print(cls) -> None:
        print("Link locations:")
        i = 0
        for name, link_location in cls.name_link_location.items():
            print(f"    {i}) {name}: \"{link_location}\"")
            i += 1

    @classmethod
    def prompt(cls, link_location_index: int = None, auto: bool = False) -> dict:
        has_index = (isinstance(link_location_index, int) and 0 <= link_location_index < cls.number_of_name_link_locations)
        i = (link_location_index if has_index else 0)

        if not auto:
            while not has_index:
                cls.print()
                text = input("Enter link location index (0): ").strip()
                if len(text) == 0:
                    i = 0
                    has_index = True
                elif text.isdigit():
                    i = int(text)
                    if 0 <= i < cls.number_of_name_link_locations:
                        has_index = True

                if not has_index:
                    print(f"Invalid link location index.")
                    print()

        name = [*(cls.name_link_location)][i]
        link_location = cls.name_link_location[name]
        result = {"i": i, "name": name, "link_location": link_location}
        logger.debug(f"Result: {result}")
        return result


class Wine():
    arch = os.environ.get("WINEARCH", os.environ.get("WINE_ARCH"))
    prefix = os.environ.get("WINEPREFIX", os.environ.get("WINE_PREFIX", "~/.wine"))
    prefix_path = os.path.expanduser(prefix)

    def __init__(self, config: dict) -> None:
        super().__init__()

        self.wine_system = WineSystemReg()
        self.wine_userdef = WineUserdefReg()

        wine_bin_path = config["wine_bin_path"]
        self.bin_path = self.get_wine_bin_path(wine_bin_path)

        self.name_link_location = None

    @classmethod
    def match_arch(self, arch: str = None) -> str:
        bin_path = "wine64"

        match arch.strip().lower():
            case "win64":
                bin_path = "wine64"
            case "win32":
                bin_path = "wine"
            case _:
                logger.warning(f"Unknown WINEARCH={arch}, neither \"win64\" nor \"win32\". Wine may fail if binary, arch, and prefix do not match.")
                bin_path = "wine"

        return bin_path

    def get_wine_bin_path(self, path: str = None) -> str:
        bin_path = "wine64"

        if contains_text(path):
            bin_path = path
        else:
            arch = self.arch
            if contains_text(arch):
                bin_path = self.match_arch(arch)
            else:
                arch = self.wine_system.get_arch()
                if contains_text(arch):
                    bin_path = self.match_arch(arch)

        return bin_path

    def resolve_name_link_location(self) -> None:
        wine_system = self.wine_system
        wine_userdef = self.wine_userdef

        name_link_location = self.name_link_location.name_link_location
        name_link_location["Common programs"] = wine_system.get_common_programs()
        name_link_location["Programs"] = wine_userdef.get_programs()
        name_link_location["Common start menu"] = wine_system.get_common_start_menu()
        name_link_location["Start menu"] = wine_userdef.get_start_menu()
        name_link_location["Common desktop"] = wine_system.get_common_desktop()
        name_link_location["Desktop"] = wine_userdef.get_desktop()
        name_link_location["Common startup"] = wine_system.get_common_startup()
        name_link_location["Startup"] = wine_userdef.get_startup()

    def create_name_link_location(self) -> NameLinkLocation:
        name_link_location = NameLinkLocation()
        self.name_link_location = name_link_location
        self.resolve_name_link_location()
        return name_link_location

    def winepath(
        self,
        path: str | Path | PureWindowsPath,
        unix: bool = False,
        windows: bool = False
    ) -> str:
        option = ""
        if unix:
            option += "--unix"
        elif windows:
            option += "--windows"
        else:
            raise NotImplementedError("winepath")

        arguments = [self.bin_path, "winepath", option, path]
        logger.debug(" ".join([str(a) for a in arguments]))
        result = subprocess.run(arguments, text=True, encoding="utf-8", capture_output=True)
        stderr = result.stderr
        stdout = result.stdout
        print(stderr)

        p = stdout.strip()
        logger.debug(f"Path: \"{p}\"")

        if not contains_text(p):
            raise ValueError("winepath did not output a path.")

        return p

    def get_desktop_path(self, text: str) -> str:
        desktop_menubuilder_regex = re.compile(r"^.+:trace:menubuilder:write_desktop_entry(?P<arguments>.+)$", re.MULTILINE)
        arguments_text = desktop_menubuilder_regex.search(text).group("arguments")

        string_arguments_regex = re.compile(r"\"(.*?)\"")
        string_arguments = string_arguments_regex.findall(arguments_text)

        desktop_path_argument = string_arguments[1]
        desktop_windows_path = desktop_path_argument[(desktop_path_argument.index(":") - 1):]
        desktop_unix_path = self.winepath(desktop_windows_path, unix=True)
        return desktop_unix_path

    @classmethod
    def add_missing_env(cls, path: str | Path) -> None:
        text = fetch_text_file(path)
        next_text = None

        exec_regex = re.compile(r"^((\s*Exec\s*=\s*)(?P<env>env\s+)?(.+))$", re.IGNORECASE | re.MULTILINE)
        exec_match = exec_regex.search(text)
        exec_text = exec_match.group()
        needs_env = (not contains_text(exec_match.group("env")))
        if " WINEARCH=" not in exec_text:
            next_text = exec_regex.sub(fr"\2\3{"env " if needs_env else ""}WINEARCH={cls.arch} \4", text)

        if contains_text(next_text):
            write_text_file(path, next_text)

    def winemenubuilder(self, path: str | Path) -> dict:
        arguments = ["env", "WINEDEBUG=+menubuilder", self.bin_path, "winemenubuilder", path]
        logger.debug(" ".join([str(a) for a in arguments]))
        result = subprocess.run(arguments, text=True, encoding="utf-8", capture_output=True)
        stderr = result.stderr
        stdout = result.stdout
        print(stderr)
        print(stdout)

        desktop_path = None
        if contains_text(self.arch):
            desktop_path = self.get_desktop_path(stderr)
            logger.info(f"Editing DESKTOP file \"{desktop_path}\"...")
            self.add_missing_env(desktop_path)

        return {"result": result, "desktop_path": desktop_path}


class WineReg():
    name_data_pattern = r"^\s*\"(?P<name>{name})\"\s*=\s*\"(?P<data>.*)\"\s*$"

    arch_regex = re.compile(r"^\s*#arch\s*=\s*(?P<arch>.+)\s*$", re.IGNORECASE | re.MULTILINE)

    def __init__(self) -> None:
        super().__init__()

        self.reg_text = None

    @classmethod
    def compile_regex(cls, name: str) -> Pattern[str]:
        pattern = cls.name_data_pattern.format(name=name)
        regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        return regex

    def search(self, name: str) -> Match[str] | None:
        regex = self.compile_regex(name)
        return regex.search(self.reg_text)

    def get_data(self, regex: Pattern[str]) -> str:
        match = regex.search(self.reg_text)
        data = match.group("data")
        return data

    def get_arch(self) -> str:
        match = self.arch_regex.search(self.reg_text)
        arch = match.group("arch")
        return arch

    def get_path(self, regex: Pattern[str]) -> str:
        data = self.get_data(regex)
        return data.replace("\\\\", "\\")


class WineSystemReg(WineReg):
    reg_path = f"{Wine.prefix_path}/system.reg"

    common_programs_regex = WineReg.compile_regex("Common programs")
    common_start_menu_regex = WineReg.compile_regex("Common start menu")
    common_desktop_regex = WineReg.compile_regex("Common desktop")
    common_startup_regex = WineReg.compile_regex("Common startup")

    def __init__(self) -> None:
        super().__init__()

        reg_text = fetch_text_file(self.reg_path)
        self.reg_text = reg_text

    def get_common_programs(self) -> str:
        return self.get_path(self.common_programs_regex)

    def get_common_start_menu(self) -> str:
        return self.get_path(self.common_start_menu_regex)

    def get_common_desktop(self) -> str:
        return self.get_path(self.common_desktop_regex)

    def get_common_startup(self) -> str:
        return self.get_path(self.common_startup_regex)


class WineUserdefReg(WineReg):
    reg_path = f"{Wine.prefix_path}/userdef.reg"

    programs_regex = WineReg.compile_regex("Programs")
    start_menu_regex = WineReg.compile_regex("Start menu")
    desktop_regex = WineReg.compile_regex("Desktop")
    startup_regex = WineReg.compile_regex("Startup")

    def __init__(self) -> None:
        super().__init__()

        reg_text = fetch_text_file(self.reg_path)
        self.reg_text = reg_text

    def get_programs(self) -> str:
        return self.get_path(self.programs_regex)

    def get_start_menu(self) -> str:
        return self.get_path(self.start_menu_regex)

    def get_desktop(self) -> str:
        return self.get_path(self.desktop_regex)

    def get_startup(self) -> str:
        return self.get_path(self.startup_regex)


def append_extension(text: str, extension: str) -> str:
    return (text + (extension if not text.endswith(extension) else ""))


def append_lnk_extension(text: str) -> str:
    return append_extension(text, ".lnk")


def prompt_lnk_name(target_path: str, lnk_name: str = None, auto: bool = False) -> str:
    has_lnk_name = contains_text(lnk_name)
    target_stem = (lnk_name if has_lnk_name else Path(target_path).stem)
    name = append_lnk_extension(target_stem)
    if not has_lnk_name and not auto:
        text = input(f"Enter LNK shortcut name (\"{name}\"): ").strip()
        if len(text) > 0:
            name = append_lnk_extension(text)
    logger.debug(f"LNK shortcut name: \"{name}\"")
    return name


class ArgumentController():
    def __init__(self, program: dict, default_config: dict) -> None:
        self.program = program
        self.default_config = default_config
        self.parser = None
        self.config = None

    @staticmethod
    def add_argument(parser, *args, **kwargs) -> None:
        if "metavar" not in kwargs and "choices" not in kwargs and "default" in kwargs:
            kwargs["metavar"] = kwargs["default"]
        parser.add_argument(*args, **kwargs)

    @classmethod
    def add_arguments(cls, parser, arguments) -> None:
        add_argument = cls.add_argument
        for argument in arguments:
            names, kwargs = argument
            add_argument(parser, *names, **kwargs)

    def create_parser(self):
        program = self.program
        name = program["name"]
        description = program["description"]
        version = program["version"]

        parser = argparse.ArgumentParser(prog=name, description=description)

        config = self.default_config
        add_arguments = self.add_arguments

        add_arguments(parser, [
            (["--version"], {"action": "version", "version": f"{name} {version}"}),
        ])

        basic_group = parser.add_argument_group("basic", "Basic options.")
        add_arguments(basic_group, [
            (["target_unix_path"], {"help": "Target Unix path (of an EXE file).", "metavar": "\"/home/user/.wine/drive_c/Program Files/Program/Program.exe\""}),

            (["--wine_bin_path"], {"help": "Path to Wine binary, usually \"/usr/bin/wine64\" (64 bit) or \"/usr/bin/wine\" (32 bit).", "metavar": "{wine64,wine}"}),

            (["--auto", "-a"], {"help": "Automatically selects the default values for options \"--link_location_index\" and \"--lnk_name\".", "action": argparse.BooleanOptionalAction, "type": bool, "default": config["auto"]}),
            (["--link_location_index", "--lli", "-i"], {"help": "Link location index for the path where the LNK shortcut file will be created.", "type": int, "metavar": 0}),
            (["--lnk_name", "--lnkn", "-n"], {"help": "LNK shortcut filename.", "metavar": "\"Program.lnk\""}),
            (["--lnk_unix_path", "--lnkp", "-p"], {"help": "Unix path of the LNK shortcut file to be created. Overrides options \"--auto\", \"--link_location_index\", and \"--lnk_name\".", "metavar": "\"/home/user/.wine/drive_c/ProgramData/Microsoft/Windows/Start Menu/Programs/Program.lnk\""}),
        ])

        extra_lnk_group = parser.add_argument_group("LNK", "Extra LNK shortcut file options.")
        add_arguments(extra_lnk_group, [
            (["--lnk_arguments", "--lnka"], {"help": "Additional arguments for the LNK shortcut file.", "metavar": "\"/help\""}),
            (["--lnk_description", "--lnkd", "-d"], {"help": "Description for the LNK shortcut file.", "metavar": "\"Program that programs the program.\""}),
            (["--lnk_icon_file", "--lnki"], {"help": "Windows path of icon file for the LNK shortcut file.", "metavar": "\"C:\\Program Files\\Program\\Program.ico\""}),
            (["--lnk_icon_index", "--lnkii"], {"help": "Icon index of icon file for the LNK shortcut file.", "type": int, "default": 0}),
            (["--lnk_work_dir", "--lnkw", "-w"], {"help": "Windows path of the work directory for the LNK shortcut file.", "metavar": "\"C:\\Program Files\\Program\""}),
            (["--lnk_window_mode", "--lnkm", "-m"], {"help": "Window mode for the LNK shortcut file.", "choices": ["Maximized", "Normal", "Minimized"]})
        ])

        self.parser = parser

        return parser

    def parse_system_arguments(self):
        parser = self.create_parser()
        result = vars(parser.parse_args())
        return result

    def create_config_from_arguments(self, result):
        default_config = self.default_config
        config = None
        try:
            config = copy.deepcopy(default_config)
        except TypeError:
            config = copy.copy(default_config)

        for key, value in result.items():
            config[key] = value

        self.config = config

        return config

    def create_config_from_system_arguments(self):
        result = self.parse_system_arguments()
        return self.create_config_from_arguments(result)


class MainController():
    def __init__(self, config: dict) -> None:
        self.config = config

    def run(self) -> None:
        config = self.config
        target_unix_path = config["target_unix_path"]
        auto = config["auto"]
        link_location_index = config["link_location_index"]
        lnk_name = config["lnk_name"]
        lnk_unix_path = config["lnk_unix_path"]
        lnk_arguments = config["lnk_arguments"]
        lnk_description = config["lnk_description"]
        lnk_icon_file = config["lnk_icon_file"]
        lnk_icon_index = config["lnk_icon_index"]
        lnk_work_dir = config["lnk_work_dir"]
        lnk_window_mode = config["lnk_window_mode"]

        wine = Wine(config)

        # Set `lnk_unix_path`.
        if not contains_text(lnk_unix_path):
            name_link_location = wine.create_name_link_location()
            selection = name_link_location.prompt(link_location_index, auto=auto)
            print()

            lnk_name = prompt_lnk_name(target_unix_path, lnk_name=lnk_name, auto=auto)
            lnk_windows_path = PureWindowsPath(selection["link_location"], lnk_name)
            print()

            lnk_unix_path = wine.winepath(lnk_windows_path, unix=True)

        print(f"Writing LNK shortcut file to \"{lnk_unix_path}\"...", end="", flush=True)
        target_windows_path = wine.winepath(target_unix_path, windows=True)
        pylnk3.helpers.for_file(
            target_windows_path,
            lnk_name=lnk_unix_path,
            arguments=lnk_arguments,
            description=lnk_description,
            icon_file=(lnk_icon_file if contains_text(lnk_icon_file) else target_windows_path),
            icon_index=lnk_icon_index,
            work_dir=lnk_work_dir,
            window_mode=lnk_window_mode,
            is_file=True
        )
        print(" Done.")

        print("Creating Wine menu item...")
        wine.winemenubuilder(lnk_unix_path)
        print("Done.")


def main(argv: list[str]) -> None:
    try:
        argument_controller = ArgumentController(PROGRAM, CONFIG)
        config = argument_controller.create_config_from_system_arguments()

        main_controller = MainController(config)
        main_controller.run()
    except Exception as exception:
        handle_exception(exception)


if __name__ == "__main__":
    main(sys.argv)