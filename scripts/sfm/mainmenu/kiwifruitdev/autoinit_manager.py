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

def _AutoinitManager_MainMenu():
    manager = globals().get("_autoinit_manager")
    if manager is None:
        try:
            # run the manager script
            cwd = os.getcwd()
            for root, dirs, files in os.walk(cwd):
                for dir in dirs:
                    if dir == "scripts":
                        script = os.path.join(root, dir, "sfm", "autoinit", "autoinit_manager.py")
                        if os.path.exists(script):
                            # first line must start with "# SFM Autoinit Script"
                            is_manager = False
                            with open(script) as f:
                                if f.readline().strip().startswith("# SFM Autoinit Script"):
                                    is_manager = True
                            if is_manager:
                                with open(script) as f:
                                    exec(f.read(), globals())
                            break
            manager = globals().get("_autoinit_manager")
            if manager is None:
                raise Exception("Autoinit Manager not found")
        except Exception  as e:
            import traceback
            traceback.print_exc()
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle("Autoinit")
            msgBox.setText("Error: %s" % e)
            msgBox.exec_()
    else:
        _AutoinitManager_FirstBoot()
        sfmApp.ShowTabWindow("autoinit_manager")

_AutoinitManager_MainMenu()