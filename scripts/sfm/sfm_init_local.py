# SFM Autoinit Script by KiwifruitDev
# https://github.com/KiwifruitDev/sfm_autoinit
# This software is licensed under the MIT License.
# MIT License
# 
# Copyright (c) 2024 KiwifruitDev
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sfm
import sfmApp
import os
import traceback
from PySide import QtGui, QtCore

_autoinit_version = "1.0"

def _autoinit_msg(msg):
    sfm.Msg("[AUTOINIT] " + msg + "\n")

# The whole autoinit class
class Autoinit:
    def __init__(self):
        self.skipped_ini = "autoinit_skipped.txt"
        self.appended_ini = "autoinit_scripts.txt"
        self.light_limit_ini = "autoinit_light_limit_patch.txt"
        self.cwd = os.getcwd()
        self.autoinit_scripts = []
        self.appended_scripts = []
        self.mods = []
        self.skipped = []
        self.appended = []
        self.found_autoinit_scripts = []
        self.found_appended_scripts = []
        self.added_separator_header = False
        self.light_limit = 8
        self.detected_light_limit_patch = False
        self.loaded_light_limit_patch = False
        self.light_limit_patch_py = ""
        self.windows = []
        self.script_fixes = {}
    def check_sfm_init(self):
        # !!!HARDCODED FIX FOR QUICK MENU https://steamcommunity.com/sharedfiles/filedetails/?id=3200935729
        sfm_init_path = os.path.join(self.cwd, "usermod", "scripts", "sfm", "sfm_init.py")
        if os.path.exists(sfm_init_path):
            with open(sfm_init_path) as f:
                sfm_init_contents = f.read()
                if "##QMENU_BEGIN##" in sfm_init_contents and "##QMENU_END##" in sfm_init_contents:
                    # Remove everything between and including ##QMENU_BEGIN## and ##QMENU_END##
                    sfm_init_contents = sfm_init_contents.split("##QMENU_BEGIN##")[0] + "##QMENU_END##" + sfm_init_contents.split("##QMENU_END##")[1]
                    sfm_init_contents.replace("##QMENU_BEGIN##", "")
                    sfm_init_contents.replace("##QMENU_END##", "")
                    with open(sfm_init_path, "w") as f:
                        f.write(sfm_init_contents)
    def start_default(self):
        self.setup_default()
    def load_default(self):
        self.load_skipped_ini()
        self.load_appended_ini()
        self.load_light_limit_ini()
        self.load_mods()
        self.load_autoinit()
        self.load_appended()
    def setup_default(self):
        self.load_default()
    def load_skipped_ini(self):
        # Load ini if it exists
        self.skipped = []
        if os.path.exists(self.skipped_ini):
            with open(self.skipped_ini) as f:
                self.skipped = f.read().splitlines()
                _autoinit_msg("Loaded " + str(len(self.skipped)) + " skipped scripts from \"" + self.skipped_ini + "\".")
        else:
            _autoinit_msg("No ini file found, creating \"" + self.skipped_ini + "\"...")
            with open(self.skipped_ini, "w") as f:
                f.write("")
    def save_skipped_ini(self):
        # Save skipped scripts to ini
        _autoinit_msg("Saving " + str(len(self.skipped)) + " skipped scripts to \"" + self.skipped_ini + "\"...")
        with open(self.skipped_ini, "w") as f:
            for script in self.skipped:
                f.write(script + "\n")
    def load_appended_ini(self):
        # Load ini if it exists
        self.appended = []
        if os.path.exists(self.appended_ini):
            with open(self.appended_ini) as f:
                self.appended = f.read().splitlines()
                _autoinit_msg("Loaded " + str(len(self.appended)) + " appended scripts from \"" + self.appended_ini + "\".")
        else:
            _autoinit_msg("No ini file found, creating \"" + self.appended_ini + "\"...")
            with open(self.appended_ini, "w") as f:
                f.write("")
    def save_appended_ini(self):
        # Save appended scripts to ini
        _autoinit_msg("Saving " + str(len(self.appended)) + " appended scripts to \"" + self.appended_ini + "\"...")
        with open(self.appended_ini, "w") as f:
            for script in self.appended:
                f.write(script + "\n")
    def load_light_limit_ini(self):
        # Load ini if it exists
        if os.path.exists(self.light_limit_ini):
            with open(self.light_limit_ini) as f:
                self.light_limit = int(f.read())
                _autoinit_msg("Loaded light limit " + str(self.light_limit) + " from \"" + self.light_limit_ini + "\".")
        else:
            _autoinit_msg("No ini file found, creating \"" + self.light_limit_ini + "\"...")
            with open(self.light_limit_ini, "w") as f:
                f.write(str(self.light_limit))
    def save_light_limit_ini(self):
        # Save light limit to ini
        _autoinit_msg("Saving light limit " + str(self.light_limit) + " to \"" + self.light_limit_ini + "\"...")
        with open(self.light_limit_ini, "w") as f:
            f.write(str(self.light_limit))
    def load_mods(self):
        # Get all mod folders
        self.script_fixes = {}
        self.mods = []
        modstemp = []
        for dir in os.listdir(self.cwd):
            # scripts subfolder must exist
            scripts = os.path.join(self.cwd, dir, "scripts")
            if os.path.exists(scripts):
                mod = dir
                if not mod in modstemp:
                    modstemp.append(mod)
        self.mods = modstemp
        _autoinit_msg("Found " + str(len(self.mods)) + " mods.")
    def load_autoinit(self):
        autoinit_dir = "scripts" + os.sep + "sfm" + os.sep + "autoinit"
        self.autoinit_scripts = []
        self.found_autoinit_scripts = []
        # Load all scripts in the autoinit directory
        total_skipped = 0
        for mod in self.mods:
            autoinit_path = os.path.join(mod, autoinit_dir)
            if os.path.exists(autoinit_path):
                for root, dirs, files in os.walk(autoinit_path):
                    for file in files:
                        if file.endswith(".py"):
                            script = os.path.join(root, file)
                            if not script in self.found_autoinit_scripts:
                                self.found_autoinit_scripts.append(script)
                                if script in self.skipped:
                                    total_skipped += 1
                                else:
                                    self.autoinit_scripts.append(script)
        _autoinit_msg("Found " + str(len(self.autoinit_scripts)) + " autoinit scripts. (" + str(total_skipped) + " disabled)")
    def load_appended(self):
        appended_dir = "scripts" + os.sep + "sfm" + os.sep + "mainmenu"
        self.appended_scripts = []
        self.found_appended_scripts = []
        self.detected_light_limit_patch = False
        # The mainmenu directory uses subdirectories that contains scripts
        total_skipped = 0
        for mod in self.mods:
            appended_path = os.path.join(mod, appended_dir)
            if os.path.exists(appended_path):
                for root, dirs, files in os.walk(appended_path):
                    for file in files:
                        if file.endswith(".py"):
                            if file == "autoinit_manager.py":
                                continue # Skip the autoinit manager script
                            script = os.path.join(root, file)
                            if not script in self.found_autoinit_scripts:
                                # !!!HARDCODED FIX FOR LIGHT LIMIT PATCH https://steamcommunity.com/sharedfiles/filedetails/?id=2963450977
                                if script.endswith("light_limit_patch.py"):
                                    self.detected_light_limit_patch = True
                                    self.light_limit_patch_py = script
                                self.found_appended_scripts.append(script)
                                if script in self.appended:
                                    self.appended_scripts.append(script)
                                else:
                                    total_skipped += 1
        _autoinit_msg("Found " + str(len(self.appended)) + " appended scripts. (" + str(total_skipped) + " disabled)")
    def run(self, script):
        script_base = os.path.basename(script)
        self.script_fixes[script_base] = []
        _autoinit_msg("Running script \"" + script + "\"...")
        try:
            with open(os.path.join(self.cwd, script)) as f:
                # Replace RegisterTabWindow with a custom function so these windows can be opened again later
                script_contents = f.read()
                if "sfmApp.RegisterTabWindow(" in script_contents:
                    self.script_fixes[script_base].append("RegisterTabWindow")
                    script_contents = script_contents.replace("sfmApp.RegisterTabWindow(", "_autoinit_global.register_window(\"" + script_base + "\", ")
                # Hide windows on first boot
                if "sfmApp.ShowTabWindow(" in script_contents:
                    self.script_fixes[script_base].append("ShowTabWindow")
                    script_contents = script_contents.replace("sfmApp.ShowTabWindow(", "pass #sfmApp.ShowTabWindow(")
                # !!!HARDCODED FIX FOR QUICK MENU https://steamcommunity.com/sharedfiles/filedetails/?id=3200935729
                if script.endswith("quickmenu_v3.py"):
                    _autoinit_msg("Quick Menu Redux by Fames was detected. Applying fix...")
                    self.script_fixes[script_base].append("QuickMenuRedux1")
                    self.script_fixes[script_base].append("QuickMenuRedux2")
                    self.script_fixes[script_base].append("QuickMenuRedux3")
                    self.check_sfm_init()
                    script_contents = script_contents.replace("ui2.show()", "pass #ui2.show()")
                    script_contents = script_contents.replace("self.setupSfmInit()", "pass #self.setupSfmInit()")
                # !!!HARDCODED FIX FOR DIRECTIONAL SCALE CONTROLS https://steamcommunity.com/sharedfiles/filedetails/?id=2942912893
                if script.endswith("directional_scale_patch.py"):
                    _autoinit_msg("Directional Scale Controls (Stretching) by LLIoKoJIad was detected. Applying fix...")
                    self.script_fixes[script_base].append("PopUpBlocker")
                    script_contents = script_contents.replace("MessageBoxInfo('", "pass #MessageBoxInfo('")
                # !!!HARDCODED FIX FOR FACIAL FLEX UNLOCKER https://steamcommunity.com/sharedfiles/filedetails/?id=2873014451
                if script.endswith("sfm_flex_unlocker.py"):
                    _autoinit_msg("Facial Flex Unlocker by LLIoKoJIad was detected. Applying fix...")
                    self.script_fixes[script_base].append("PopUpBlocker")
                    script_contents = script_contents.replace("MessageBoxSuccess('", "pass #MessageBoxSuccess('")
                # !!!HARDCODED FIX FOR LIGHT LIMIT PATCH https://steamcommunity.com/sharedfiles/filedetails/?id=2963450977
                if script.endswith("light_limit_patch.py"):
                    _autoinit_msg("Light Limit Patch by KiwifruitDev was detected. Applying fix...")
                    self.script_fixes[script_base].append("PopUpBlocker")
                    self.script_fixes[script_base].append("LightLimitPatch")
                    self.loaded_light_limit_patch = True
                    script_contents = script_contents.replace("PatchDialog().exec_()", "apply_patches(" + str(self.light_limit) + ") #PatchDialog().exec_()")
                # Use global namespace so imported modules are available to the script
                exec(script_contents, globals())
        except Exception as e:
            # get traceback as string
            tb = traceback.format_exc()
            sfm.ErrMsg("Error: %s\n%s" % (e, tb))
    def run_all(self):
        # Run all scripts
        _autoinit_msg("Running autoinit scripts...")
        for script in self.autoinit_scripts:
            self.run(script)
        _autoinit_msg("Running appended scripts...")
        for script in self.appended_scripts:
            self.run(script)
        _autoinit_msg("Done.")
    def add_window_action(self, script, window, name):
        # Adds a window action to Windows menu, taken from https://steamcommunity.com/sharedfiles/filedetails/?id=562830725
        main_window = sfmApp.GetMainWindow()
        for widget in main_window.children():
            if isinstance(widget, QtGui.QMenuBar):
                menu_bar = widget
                break
        for menu_item in menu_bar.actions():
            if menu_item.text() == 'Windows':
                windows_menu = menu_item.menu()
                break
        separator_skipped = 0
        for action in windows_menu.actions():
            if self.added_separator_header and separator_skipped < 6 and action.isSeparator():
                separator_skipped += 1
                if separator_skipped == 6:
                    windows_menu.removeAction(action)
            if action.text() == 'Particle Editor Tool':
                below_action = action
                break
        if not self.added_separator_header:
            # Add separator just above Particle Editor Tool
            windows_menu.insertSeparator(below_action)
            self.added_separator_header = True
        window_action = QtGui.QAction(QtGui.QIcon(), name, windows_menu)
        window_action.triggered.connect(lambda: sfmApp.ShowTabWindow(window))
        windows_menu.insertAction(below_action, window_action)
        windows_menu.insertSeparator(below_action)
    def register_window(self, script, window, name, pointer):
        # Add script/window pair to list if it hasn't been added yet
        if not (script, window) in self.windows:
            # Register a window and add it to the Windows menu
            self.add_window_action(script, window, name)
            self.windows.append((script, window))
        sfmApp.RegisterTabWindow(window, name, pointer)
    def set_light_limit(self, limit):
        # Set the light limit and save it to ini
        self.light_limit = limit
        self.save_light_limit_ini()
        # Reload the light limit patch
        self.run(self.light_limit_patch_py)

def _Autoinit_FirstBoot():
    autoinit = None
    try:
        autoinit = globals().get("_autoinit_global")
        if autoinit is None:
            _autoinit_msg("Version " + _autoinit_version)
            autoinit = Autoinit()
            globals()["_autoinit_global"] = autoinit
            autoinit.start_default()
    except Exception as e:
        # get traceback as string
        tb = traceback.format_exc()
        sfm.ErrMsg("Error: %s\n%s" % (e, tb))
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle("Autoinit")
        msgBox.setText("Error: %s" % e)
        msgBox.exec_()
    # Don't except on non-autoinit scripts
    if autoinit != None:
        autoinit.run_all()

_Autoinit_FirstBoot()
