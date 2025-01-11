# SFM Autoinit Script by KiwifruitDev
# https://github.com/KiwifruitDev/sfm_autoinit
# This software is licensed under the MIT License.
# MIT License
# 
# Copyright (c) 2025 KiwifruitDev
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

import sfmApp
import os
from sfmApp import ShowTabWindow as sfmapp_show_tab_window
from PySide import QtGui, QtCore, shiboken

class AutoInitManagerButtonContainer(QtGui.QWidget):
    def __init__(self):
        super( AutoInitManagerButtonContainer, self ).__init__()
        self.buttoncount = 0
        self.initUI()
    def initUI(self):
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
    def addButton(self, button):
        self.buttoncount += 1
        self.layout.addWidget(button)
    def clearButtons(self):
        self.buttoncount = 0
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()

class AutoinitManager(QtGui.QWidget):
    def __init__(self):
        super( AutoinitManager, self ).__init__()
        self.appended = []
        self.autoinited = []
        self.scrollamount = 0
        self.table_entries = 0
        self.selected_row_number = 0
        self.selected_workshop_id = 0
        self.workshop_dats = []
        self.ran_manually = []
        self.scanned_workshop_dats = False
        self.initUI()
        # wait 1 second before populating the table
        QtCore.QTimer.singleShot(1000, self.populate_timer)
    def read_workshop_dat(self, path):
        # path is "D:\SteamLibrary\steamapps\common\SourceFilmmaker\game\workshop\metadata\3379593854.dat"
        id = os.path.basename(path).split(".")[0]
        name = ""
        items = []
        once_1_max = 128 # max name length
        once_2_max = 32 # max amount of items
        once_3_max = 256 # max item path length
        # first 8 bytes 00-07 are a header we don't need
        # then from column 08 to the first 00 byte is the name
        # each item is a path, separated by 00 bytes
        # last byte in the whole file is 00
        with open(path, "rb") as f:
            f.seek(8) # skip header
            once_1 = once_1_max
            while once_1 > 0:
                byte = f.read(1)
                if byte == b"\x00":
                    break
                name += byte.decode("utf-8")
                once_1 -= 1
            name = name
            if once_1 == 0:
                # could not read name
                return (id, name, [])
            once_2 = once_2_max
            while once_2 > 0:
                item = ""
                once_3 = once_3_max
                while once_3 > 0:
                    byte = f.read(1)
                    if byte == b"\x00":
                        break
                    item += byte.decode("utf-8")
                    once_3 -= 1
                if item == "":
                    break
                if once_3 == 0:
                    # could not read item
                    break
                items.append(item)
                once_2 -= 1
        return (id, name, items)
    def read_all_workshop_dats(self):
        if not self.scanned_workshop_dats:
            self.scanned_workshop_dats = True
            self.workshop_dats = []
            workshop_dir = os.path.join(_autoinit_global.cwd, "workshop", "metadata")
            for relative_file in os.listdir(workshop_dir):
                file = os.path.join(workshop_dir, relative_file)
                if os.path.isfile(file):
                    if file.endswith(".dat"):
                        dat = {}
                        dat["id"], dat["name"], dat["items"] = self.read_workshop_dat(file)
                        self.workshop_dats.append(dat)
    def find_workshop_item(self, path):
        path = path.lower()
        for dat in self.workshop_dats:
            for item in dat["items"]:
                if path in item.lower():
                    return dat["id"], dat["name"]
        return 0, ""
    def setuptable(self):
        self.table_entries = 0
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Path", "Enabled", "Active", "Buttons"])
        self.table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.table.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Fixed)
        self.table.horizontalHeader().setDefaultSectionSize(80)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)     
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.table_context_menu)   
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
    def table_context_menu(self, pos):
        # reload workshop dats
        self.read_all_workshop_dats()
        self.selected_row_number = self.table.indexAt(pos).row()
        path = self.table.item(self.selected_row_number, 0).text()
        full_path = os.path.join(_autoinit_global.cwd, path)
        basename = os.path.basename(path)
        basefolder = os.path.dirname(path)
        self.selected_workshop_id, workshop_name = self.find_workshop_item(full_path)
        menu = QtGui.QMenu()
        if self.selected_workshop_id > 0:
            workshop_header = menu.addAction("**** %s: ****" % workshop_name)
            workshop_header.setEnabled(False)
            open_workshop_item = menu.addAction("Open Workshop Item")
            open_workshop_item.triggered.connect(self.open_workshop_item)
        script_header = menu.addAction("**** %s: ****" % basename)
        script_header.setEnabled(False)
        currently_enabled = self.table.cellWidget(self.selected_row_number, 1).isChecked()
        if currently_enabled:
            disable = menu.addAction("Disable Autoinit")
            disable.triggered.connect(self.disable_script)
        else:
            enable = menu.addAction("Enable Autoinit")
            enable.triggered.connect(self.enable_script)
        run = menu.addAction("Run Script")
        run.triggered.connect(lambda: self.run(path))
        if basename == "autoinit_manager.py":
            run.setEnabled(False)
        windows = []
        for script_window_pair in _autoinit_global.windows:
            if script_window_pair[0] == basename:
                windows.append(script_window_pair)
        if len(windows) > 0:
            show = menu.addAction("Show Windows")
            show.triggered.connect(lambda: self.show(windows))
            if basename == "autoinit_manager.py":
                show.setEnabled(False)
        edit = menu.addAction("Open with Default Association")
        edit.triggered.connect(self.edit_script)
        # _autoinit_global.script_fixes is a key-value list where basenames map to an array of strings
        # each string is an identifier of a fix
        if basename in _autoinit_global.script_fixes:
            fix_counts = {}
            for fix in _autoinit_global.script_fixes[basename]:
                if fix in fix_counts:
                    fix_counts[fix] += 1
                else:
                    fix_counts[fix] = 1
            if len(fix_counts) > 0:
                fix_menu = menu.addMenu("Autoinit Patches")
                pretty_fixes = {}
                pretty_fixes["RegisterTabWindow"] = "Replaced RegisterTabWindow calls"
                pretty_fixes["ShowTabWindow"] = "Replaced ShowTabWindow calls"
                pretty_fixes["PopUpBlocker"] = "Disabled pop-up dialogs"
                pretty_fixes["QuickMenuRedux1"] = "Disabled showing the window on run"
                pretty_fixes["QuickMenuRedux2"] = "Prevented writing to sfm_init.py"
                pretty_fixes["QuickMenuRedux3"] = "Removed existing code from sfm_init.py"
                pretty_fixes["LightLimitPatch"] = "Added options to Autoinit Manager"
                for fix, count in fix_counts.items():
                    fix_pretty = fix
                    if fix in pretty_fixes:
                        fix_pretty = pretty_fixes[fix]
                    if count > 1:
                        fix_action = fix_menu.addAction("%s (x%d)" % (fix_pretty, count))
                    else:
                        fix_action = fix_menu.addAction(fix_pretty)
                    fix_action.setEnabled(False)
        folder_header = menu.addAction("**** %s: ****" % basefolder)
        folder_header.setEnabled(False)
        open_in_explorer = menu.addAction("Open in Explorer")
        open_in_explorer.triggered.connect(self.open_in_explorer)
        search_inside = menu.addAction("Search Inside")
        search_inside.triggered.connect(self.search_inside)
        menu.exec_(self.table.viewport().mapToGlobal(pos))
    def disable_script(self):
        self.table.cellWidget(self.selected_row_number, 1).setChecked(False)
        self.update()
    def enable_script(self):
        self.table.cellWidget(self.selected_row_number, 1).setChecked(True)
        self.update()
    def edit_script(self):
        # open in default text editor
        path = self.table.item(self.selected_row_number, 0).text()
        full_path = os.path.join(_autoinit_global.cwd, path)
        os.startfile(full_path)
    def open_workshop_item(self):
        # open in browser
        workshop_url = "https://steamcommunity.com/sharedfiles/filedetails/?id=%s" % self.selected_workshop_id
        os.startfile(workshop_url)
    def open_in_explorer(self):
        path = self.table.item(self.selected_row_number, 0).text()
        full_path = os.path.join(_autoinit_global.cwd, path)
        os.startfile(full_path)
    def search_inside(self):
        # set search to containing folder
        path = self.table.item(self.selected_row_number, 0).text()
        folder = os.path.dirname(path)
        self.search.setText(folder)
        self.searchfor()
    def initUI(self):
        self.mainlayout = QtGui.QVBoxLayout()
        self.headerlayout = QtGui.QHBoxLayout()
        self.header = QtGui.QLabel("Detected Scripts:")
        self.headerlayout.addWidget(self.header)
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.search.textChanged.connect(self.searchfor)
        self.headerlayout.addWidget(self.search)
        self.reloadbutton = QtGui.QPushButton("Reload")
        self.reloadbutton.clicked.connect(self.reload)
        self.reloadbutton.setMaximumWidth(48)
        self.headerlayout.addWidget(self.reloadbutton)
        self.mainlayout.addLayout(self.headerlayout)
        # list with columns
        self.table = QtGui.QTableWidget()
        self.setuptable()
        self.mainlayout.addWidget(self.table)
        self.footerlayout = QtGui.QHBoxLayout()
        self.footertextlayout = QtGui.QVBoxLayout()
        self.footer1 = QtGui.QLabel("SFM Autoinit v%s by KiwifruitDev" % _autoinit_version)
        self.footertextlayout.addWidget(self.footer1)
        #self.footer2 = QtGui.QLabel("Copyright (c) 2025 KiwifruitDev")
        #self.footertextlayout.addWidget(self.footer2)
        #self.footer3 = QtGui.QLabel("This software is licensed under the MIT License.")
        #self.footertextlayout.addWidget(self.footer3)
        self.footerlayout.addLayout(self.footertextlayout)
        #self.footeroptionslayout = QtGui.QVBoxLayout()
        self.footeroptionslayout = QtGui.QHBoxLayout()
        self.footeroptionslayout.addStretch()
        #self.footeroptionstext = QtGui.QLabel("Options:")
        #self.footeroptionslayout.addWidget(self.footeroptionstext)
        #self.footeroptionscontainerlayout = QtGui.QHBoxLayout()
        #self.footeroptions1 = QtGui.QPushButton("Reload")
        #self.footeroptions1.clicked.connect(self.reload)
        #self.footeroptionscontainerlayout.addWidget(self.footeroptions1)
        #self.footeroptionslayout.addLayout(self.footeroptionscontainerlayout)
        self.footerlayout.addLayout(self.footeroptionslayout)
        self.footeroptions2text = None
        self.footeroptions2spinbox = None
        self.mainlayout.addLayout(self.footerlayout)
        self.setLayout(self.mainlayout)
    def searchfor(self):
        search = self.search.text()
        for row in range(self.table.rowCount()):
            path = self.table.item(row, 0).text()
            if search.lower() in path.lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
    def add_light_limit(self, active):
        if _autoinit_global.detected_light_limit_patch:
            if not self.footeroptions2spinbox:
                self.footeroptions2text = QtGui.QLabel("Shadowed Light Limit:")
                self.footeroptionslayout.addWidget(self.footeroptions2text, 0, QtCore.Qt.AlignRight)
                self.footeroptions2spinbox = QtGui.QSpinBox()
                self.footeroptions2spinbox.setRange(1, 127)
                self.footeroptions2spinbox.setValue(_autoinit_global.light_limit)
                self.footeroptions2spinbox.setSingleStep(1)
                self.footeroptions2spinbox.setToolTip("""Using high max shadowed light values with high -sfm_shadowmapres values can cause SFM to crash.
        Make sure you save before using! Try using a lower -sfm_shadowmapres value if SFM crashes.
        A sane max shadowed light value is 24, but higher options are available for experimentation.""")
                self.footeroptions2spinbox.valueChanged.connect(lambda: _autoinit_global.set_light_limit(self.footeroptions2spinbox.value()))
                self.footeroptions2spinbox.setMaximumWidth(64)
                self.footeroptionslayout.addWidget(self.footeroptions2spinbox, 0, QtCore.Qt.AlignRight)
            self.footeroptions2spinbox.setValue(_autoinit_global.light_limit)
            self.footeroptions2spinbox.setEnabled(active)
        else:
            if self.footeroptions2spinbox:
                # Remove the light limit options
                #self.footeroptionslayout.removeWidget(self.footeroptions2spinbox)
                self.footeroptions2spinbox.deleteLater()
                self.footeroptions2spinbox = None
                #self.footeroptionslayout.removeWidget(self.footeroptions2text)
                self.footeroptions2text.deleteLater()
                self.footeroptions2text = None
    def addentry(self, path, enabled, active):
        self.table_entries += 1
        row = self.table.rowCount()
        self.table.insertRow(row)
        item = QtGui.QTableWidgetItem(path)
        item.setToolTip(path)
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.table.setItem(row, 0, item)
        enabledbox = QtGui.QCheckBox()
        enabledbox.setChecked(enabled)
        enabledbox.stateChanged.connect(self.update)
        self.table.setCellWidget(row, 1, enabledbox)
        activebox = QtGui.QCheckBox()
        activebox.setChecked(active)
        activebox.setEnabled(False)
        self.table.setCellWidget(row, 2, activebox)
        script_basename = os.path.basename(path)
        buttons = AutoInitManagerButtonContainer()
        runbutton = QtGui.QPushButton("Run")
        runbutton.clicked.connect(lambda: self.run(path))
        runbutton.setToolTip("Run this script")
        buttons.addButton(runbutton)
        if script_basename == "autoinit_manager.py":
            runbutton.setEnabled(False)
        if active:
            # Search for script basename as first value in a pair in _autoinit_global.windows
            windows = []
            for script_window_pair in _autoinit_global.windows:
                if script_window_pair[0] == script_basename:
                    windows.append(script_window_pair)
            if len(windows) > 0:
                # Add show button
                showbutton = QtGui.QPushButton("Show")
                showbutton.clicked.connect(lambda: self.show(windows))
                showbutton.setToolTip("Show all windows associated with this script")
                buttons.addButton(showbutton)
                if script_basename == "autoinit_manager.py":
                    showbutton.setEnabled(False)
        self.table.setCellWidget(row, 3, buttons)
        if script_basename == "light_limit_patch.py":
            self.add_light_limit(active)
    def populate_timer(self):
        self.populate(False)
    def populate(self, reload):
        for script in _autoinit_global.found_autoinit_scripts:
            was_autoinited = script in _autoinit_global.autoinit_scripts
            was_ran_manually = script in self.ran_manually
            if reload:
                was_autoinited = script in self.autoinited
            elif was_autoinited:
                self.autoinited.append(script)
            self.addentry(script, script not in _autoinit_global.skipped, was_autoinited or was_ran_manually)
        for script in _autoinit_global.found_appended_scripts:
            was_appended = script in _autoinit_global.appended_scripts
            was_ran_manually = script in self.ran_manually
            if reload:
                was_appended = script in self.appended
            elif was_appended:
                self.appended.append(script)
            self.addentry(script, script in _autoinit_global.appended, was_appended or was_ran_manually)
        # filter by current search
        self.searchfor()
    def update(self):
        for row in range(self.table.rowCount()):
            path = self.table.item(row, 0).text()
            enabled = self.table.cellWidget(row, 1).isChecked()
            active = self.table.cellWidget(row, 2).isChecked()
            if path in _autoinit_global.found_autoinit_scripts:
                if enabled:
                    if path in _autoinit_global.skipped:
                        _autoinit_global.skipped.remove(path)
                else:
                    if path not in _autoinit_global.skipped:
                        _autoinit_global.skipped.append(path)
            elif path in _autoinit_global.found_appended_scripts:
                if enabled:
                    if path not in _autoinit_global.appended:
                        _autoinit_global.appended.append(path)
                else:
                    if path in _autoinit_global.appended:
                        _autoinit_global.appended.remove(path)
        _autoinit_global.save_skipped_ini()
        _autoinit_global.save_appended_ini()
    def reload(self):
        self.scanned_workshop_dats = False
        # store scroll amount of table
        current_table_entries = self.table_entries
        self.scrollamount = self.table.verticalScrollBar().value()
        # reload scripts
        sfmApp.RescanScriptMenus()
        _autoinit_global.load_default()
        # reset table
        self.table.clear()
        self.table.setRowCount(0)
        self.setuptable()
        # repopulate table
        self.populate(True)
        # restore scroll amount using current_table_entries
        if current_table_entries > 0:
            self.table.scrollToItem(self.table.item(current_table_entries - 1, 0))
        self.table.verticalScrollBar().setValue(self.scrollamount)
        
    def run(self, script):
        if "/autoinit/" in script:
            if not script in self.autoinited:
                self.autoinited.append(script)
        elif "/mainmenu/" in script:
            if not script in self.appended:
                self.appended.append(script)
        # Add to ran_manually
        if not script in self.ran_manually:
            self.ran_manually.append(script)
        # Run the script
        _autoinit_global.run(script)
        self.reload()
    def show(self, windows):
        for window in windows:
            sfmapp_show_tab_window(window[1])

def _AutoinitManager_FirstBoot():
    try:
        # Create window if it doesn't exist
        manager = globals().get("_autoinit_manager")
        if manager is None:
            autoinit = globals().get("_autoinit_global")
            if autoinit is None:
                # run the autoinit script
                cwd = os.getcwd()
                for root, dirs, files in os.walk(cwd):
                    for dir in dirs:
                        if dir == "scripts":
                            script = os.path.join(dir, "sfm", "sfm_init_local.py")
                            if os.path.exists(script):
                                # first line must start with "# SFM Autoinit Script"
                                is_autoinit = False
                                with open(script) as f:
                                    if f.readline().strip().startswith("# SFM Autoinit Script"):
                                        is_autoinit = True
                                if is_autoinit:
                                    globals()["_autoinit_global"] = True # dummy value so first boot doesn't run again
                                    with open(script) as f:
                                        exec(f.read(), globals())
                                    # create the autoinit object
                                    autoinit = Autoinit()
                                    globals()["_autoinit_global"] = autoinit
                                    autoinit.load_default()
                                break
            manager = AutoinitManager()
            globals()["_autoinit_manager"] = manager
            pointer = shiboken.getCppPointer(manager)
            _autoinit_global.register_window("autoinit_manager.py", "autoinit_manager", "Autoinit Manager", pointer[0])
        sfmApp.ShowTabWindow("autoinit_manager")
    except Exception  as e:
        import traceback
        traceback.print_exc()
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle("Autoinit")
        msgBox.setText("Error: %s" % e)
        msgBox.exec_()

_AutoinitManager_FirstBoot()
