# SFM Autoinit Manager Script
This script is designed to automatically run other scripts when **Source Filmmaker** is started. It also provides a window to manage these scripts and their settings.

## Usage
The **Autoinit Manager** window will normally open automatically, but it can be opened manually through `Scripts > kiwifruitdev > autoinit_manager`.

Additionally, you can use `-nostartwizard` as a launch option to disable the session creation popup when starting **SFM**.

All script windows that are opened on startup will be given a button in the "Windows" menu so you can open them at any time. By default, these windows will be hidden until shown manually so that your layouts can stay consistent.

## Patches
Some scripts will be dynamically patched to work without interruptions. The following changes have been made:

- Any script that uses `sfmApp.RegisterTabWindow`
    - A "Show" button for this script will be added to the **Autoinit Manager** window.
    - The window that was registered will have an option added to the "Window" menu in **SFM**.
- Any script that uses `sfmApp.ShowTabWindow`
    - No windows will be shown, this is to prevent custom windows from popping up when **SFM** starts.
    - You can still show the window by using the "Window" menu in **SFM** or through the **Autoinit Manager** window.
- [Quick Menu Redux by Fames](https://steamcommunity.com/sharedfiles/filedetails/?id=3200935729) (`quickmenu_v3.py`)
    - Disabled showing the window on run since it does not use `sfmApp.ShowTabWindow`.
    - Prevented writing to `sfm_init.py` because it is no longer needed.
    - Removed existing code that runs this script from `sfm_init.py` if it exists.
- [Directional Scale Controls (Stretching) by LLIoKoJIad](https://steamcommunity.com/sharedfiles/filedetails/?id=2942912893) (`directional_scale_patch.py`)
    - Disabled pop-up dialogs that normally appear when the script is run.
- [Facial Flex Unlocker by LLIoKoJIad](https://steamcommunity.com/sharedfiles/filedetails/?id=2873014451) (`sfm_flex_unlocker.py`)
    - Disabled pop-up dialogs that normally appear when the script is run.
- [Light Limit Patch by KiwifruitDev](https://steamcommunity.com/sharedfiles/filedetails/?id=2963450977) (`light_limit_patch.py`)
    - Disabled pop-up dialogs that normally appear when the script is run.
    - Added enhanced options to **Autoinit Manager** to allow you to set the light limit on startup.

You can view which patches have been applied to a script by right clicking on its entry in the **Autoinit Manager** window and hovering over the "Autoinit Patches" option.

## Development
If you're a developer, add your script to a `scripts/sfm/autoinit` folder. The script will be executed when the **SFM** is started and users can enable or disable it in the **Autoinit Manager** window. You can then add [Autoinit Manager](https://steamcommunity.com/sharedfiles/filedetails/?id=3400621327) as a dependency to your Workshop item.

This script is also available on [GitHub](https://github.com/KiwifruitDev/sfm_autoinit).

## License
This script is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Funding
If you would like to support my work, you can check out [Nonsensical Video Generator](https://store.steampowered.com/app/2516360/Nonsensical_Video_Generator/), buy me a coffee on [Ko-fi](https://ko-fi.com/kiwifruitdev), become a sponsor through [GitHub Sponsors](https://github.com/sponsors/KiwifruitDev), or simply share my scripts with others. Thank you for your support!
