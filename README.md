# Wine menu shortcut
This script creates an LNK shortcut file for a provided executable and then uses winemenubuilder to add a Wine menu item.

## Requirements

* [Python 3.10+](https://www.python.org/downloads/)
* [Wine](https://wiki.winehq.org/Download)

## Installation

```shell
# Install dependencies.
pip install "pylnk3>=1.0.0a1"

# Download script to current directory.
wget "https://github.com/XP1/Wine-menu-shortcut/raw/main/src/Create%20Wine%20menu%20shortcut.py"

# ...
```

## Usage

```
python "Create Wine menu shortcut.py" --help
usage: Create Wine menu shortcut [-h] [--version] [--wine_bin_path {wine64,wine}] [--auto | --no-auto | -a]
                                 [--link_location_index 0] [--lnk_name "Program.lnk"]
                                 [--lnk_unix_path "/home/user/.wine/drive_c/ProgramData/Microsoft/Windows/Start Menu/Programs/Program.lnk"]
                                 [--lnk_arguments "/help"] [--lnk_description "Program that programs the program."]
                                 [--lnk_icon_file "C:\Program Files\Program\Program.ico"] [--lnk_icon_index 0]
                                 [--lnk_work_dir "C:\Program Files\Program"]
                                 [--lnk_window_mode {Maximized,Normal,Minimized}]
                                 "/home/user/.wine/drive_c/Program Files/Program/Program.exe"

Creates an LNK shortcut file for a provided executable and then uses winemenubuilder to add a Wine menu item.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

basic:
  Basic options.

  "/home/user/.wine/drive_c/Program Files/Program/Program.exe"
                        Target Unix path (of an EXE file).
  --wine_bin_path {wine64,wine}
                        Path to Wine binary, usually "/usr/bin/wine64" (64 bit) or "/usr/bin/wine" (32 bit).
  --auto, --no-auto, -a
                        Automatically selects the default values for options "--link_location_index" and "--lnk_name".
  --link_location_index 0, --lli 0, -i 0
                        Link location index for the path where the LNK shortcut file will be created.
  --lnk_name "Program.lnk", --lnkn "Program.lnk", -n "Program.lnk"
                        LNK shortcut filename.
  --lnk_unix_path "/home/user/.wine/drive_c/ProgramData/Microsoft/Windows/Start Menu/Programs/Program.lnk", --lnkp "/home/user/.wine/drive_c/ProgramData/Microsoft/Windows/Start Menu/Programs/Program.lnk", -p "/home/user/.wine/drive_c/ProgramData/Microsoft/Windows/Start Menu/Programs/Program.lnk"
                        Unix path of the LNK shortcut file to be created. Overrides options "--auto", "--
                        link_location_index", and "--lnk_name".

LNK:
  Extra LNK shortcut file options.

  --lnk_arguments "/help", --lnka "/help"
                        Additional arguments for the LNK shortcut file.
  --lnk_description "Program that programs the program.", --lnkd "Program that programs the program.", -d "Program that programs the program."
                        Description for the LNK shortcut file.
  --lnk_icon_file "C:\Program Files\Program\Program.ico", --lnki "C:\Program Files\Program\Program.ico"
                        Windows path of icon file for the LNK shortcut file.
  --lnk_icon_index 0, --lnkii 0
                        Icon index of icon file for the LNK shortcut file.
  --lnk_work_dir "C:\Program Files\Program", --lnkw "C:\Program Files\Program", -w "C:\Program Files\Program"
                        Windows path of the work directory for the LNK shortcut file.
  --lnk_window_mode {Maximized,Normal,Minimized}, --lnkm {Maximized,Normal,Minimized}, -m {Maximized,Normal,Minimized}
                        Window mode for the LNK shortcut file.
```

### Commands

#### Basic default

Uses "wine64" binary, "win64" arch, and "`~/.wine`" prefix by default for 64-bit apps.

```shell
python "Create Wine menu shortcut.py" '/home/user/.wine/drive_c/Program Files/Program/Program.exe'
```

#### Custom arch and prefix

Uses "wine" binary, "win32" arch, and "`~/.wine32`" custom prefix for 32-bit apps.

```shell
env WINEARCH=win32 WINEPREFIX="~/.wine32" python "Create Wine menu shortcut.py" '/home/user/.wine/drive_c/Program Files/Program/Program.exe'
```

#### Auto

Automatically selects the default link location index and LNK shortcut name without prompting the user.

```shell
python "Create Wine menu shortcut.py" '/home/user/.wine/drive_c/Program Files/Program/Program.exe' --auto
```

### Example

```
python "Create Wine menu shortcut.py" '/home/user/.wine/drive_c/Program Files/Program/Program.exe'
Link locations:
    0) Common programs: "C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
    1) Programs: "C:\users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
    2) Common start menu: "C:\ProgramData\Microsoft\Windows\Start Menu"
    3) Start menu: "C:\users\user\AppData\Roaming\Microsoft\Windows\Start Menu"
    4) Common desktop: "C:\users\Public\Desktop"
    5) Desktop: "C:\users\user\Desktop"
    6) Common startup: "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
    7) Startup: "C:\users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\StartUp"
Enter link location index (0):

Enter LNK shortcut name ("Program.lnk"):

002c:fixme:winediag:loader_init wine-staging 9.6 is a testing version containing experimental patches.
002c:fixme:winediag:loader_init Please mention your exact version when filing bug reports on winehq.org.

Writing LNK shortcut file to "/home/user/.wine/dosdevices/c:/ProgramData/Microsoft/Windows/Start Menu/Programs/Program.lnk"...002c:fixme:winediag:loader_init wine-staging 9.6 is a testing version containing experimental patches.
002c:fixme:winediag:loader_init Please mention your exact version when filing bug reports on winehq.org.

 Done.
Creating Wine menu item...
002c:fixme:winediag:loader_init wine-staging 9.6 is a testing version containing experimental patches.
002c:fixme:winediag:loader_init Please mention your exact version when filing bug reports on winehq.org.
0124:trace:menubuilder:Process_Link L"/home/user/.wine/dosdevices/c:/ProgramData/Microsoft/Windows/Start Menu/Programs/Program.lnk", wait 0
0124:trace:menubuilder:get_link_location L"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Program.lnk"
0124:trace:menubuilder:get_link_location L"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Program.lnk"
0124:trace:menubuilder:get_link_location L"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Program.lnk"
0124:trace:menubuilder:InvokeShellLinker Link       : L"Programs\\Program"
0124:trace:menubuilder:InvokeShellLinker workdir    : L""
0124:trace:menubuilder:InvokeShellLinker description: L""
0124:trace:menubuilder:InvokeShellLinker path       : L""
0124:trace:menubuilder:InvokeShellLinker args       : L""
0124:trace:menubuilder:InvokeShellLinker icon file  : L"C:\\Program Files\\Program\\Program.exe"
0124:trace:menubuilder:InvokeShellLinker pidl path  : L"C:\\Program Files\\Program\\Program.exe"
0124:trace:menubuilder:extract_icon path=[L"C:\\Program Files\\Program\\Program.exe"] index=0 destFilename=[(null)]
0124:trace:menubuilder:platform_write_icon [0]: 48 x 48 @ 32
0124:trace:menubuilder:platform_write_icon Selected: 0
0124:trace:menubuilder:platform_write_icon [1]: 64 x 64 @ 32
0124:trace:menubuilder:platform_write_icon Selected: 1
0124:trace:menubuilder:platform_write_icon [2]: 32 x 32 @ 8
0124:trace:menubuilder:platform_write_icon Selected: 2
0124:trace:menubuilder:platform_write_icon [3]: 16 x 16 @ 8
0124:trace:menubuilder:platform_write_icon Selected: 3
0124:trace:menubuilder:write_menu_entry (L"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Program.lnk", L"Programs\\Program", L"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Program.lnk", (null), L"", L"", L"18C2_Program.0", L"program.exe")
0124:trace:menubuilder:write_desktop_entry (L"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Program.lnk",L"\\\\?\\Z:\\home\\user\\.local\\share\\applications\\wine\\Programs\\Program.desktop",L"Programs\\Program",L"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Program.lnk",(null),L"",L"",L"18C2_Program.0",L"program.exe")
0124:trace:menubuilder:write_menu_file (L"Programs\\Program")


Done.
```

## Shortcut locations

The script should create the LNK files in [one of the several link location directories that winemenubuilder accepts](https://source.winehq.org/git/wine.git/blob/HEAD:/programs/winemenubuilder/winemenubuilder.c#l1469):

| Folder name       | Folder path                                                   | CSIDL | CSIDL name                    |
|-------------------|---------------------------------------------------------------|-------|-------------------------------|
| Startup           | `%AppData%\Microsoft\Windows\Start Menu\Programs\StartUp`     | 0x07  | CSIDL_STARTUP                 |
| Desktop           | `%UserProfile%\Desktop`                                       | 0x10  | CSIDL_DESKTOPDIRECTORY        |
| Start Menu        | `%AppData%\Microsoft\Windows\Start Menu`                      | 0x0b  | CSIDL_STARTMENU               |
| Common Startup    | `%ProgramData%\Microsoft\Windows\Start Menu\Programs\StartUp` | 0x18  | CSIDL_COMMON_STARTUP          |
| Common Desktop    | `%Public%\Desktop`                                            | 0x19  | CSIDL_COMMON_DESKTOPDIRECTORY |
| Common Start Menu | `%ProgramData%\Microsoft\Windows\Start Menu`                  | 0x16  | CSIDL_COMMON_STARTMENU        |

If the LNK is not placed in a valid location, winemenubuilder exits with a warning. For example:

```
warn:menubuilder:InvokeShellLinker Unknown link location L"C:\\Program Files\\Program\\Program.lnk". Ignoring.
```

Wine creates DESKTOP files in the "`~/.local/share/applications/wine`" directory.

If the Wine menu item does not appear immediately, you may need to run the command:

```shell
update-desktop-database "~/.local/share/applications"
```