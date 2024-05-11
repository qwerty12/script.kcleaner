# ============================================================
# KCleaner - Version 4.0 by D. Lanik (2017)
# ------------------------------------------------------------
# Clean up Kodi
# ------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# ============================================================

import xbmc
import xbmcaddon

# ============================================================
# Define Settings Monitor Class
# ============================================================


class SettingMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        GetSetting()

# ============================================================
# Get settings
# ============================================================


def GetSetting():
    global booBackgroundRun
    global lastrundays

    #__addon__ = xbmcaddon.Addon(id='script.kcleaner')

    booBackgroundRun = __settings__.getBool('autoclean')

    auto_interval = __settings__.getInt('auto_interval')

    if auto_interval == 0:
        lastrundays = 1
    elif auto_interval == 1:
        lastrundays = 7
    elif auto_interval == 2:
        lastrundays = 30
    elif auto_interval == 3:
        lastrundays = 90
    else:
        lastrundays = 0

    xbmc.log('KCLEANER SERVICE >> SETTINGS CHANGED >> SERVICE RUN: ' + str(booBackgroundRun))
    xbmc.log('KCLEANER SERVICE >> SETTINGS CHANGED >> RUN EVERY DAYS: ' + str(lastrundays))

# ============================================================
# Run cleaning according to settings
# ============================================================


def AutoClean():
    import os
    from default import DeleteFiles
    from default import CompactDatabases
    from default import CleanTextures
    from default import deleteAddonData

    global __addon__
    global __addonname__

    intMbDel = 0
    intMbCom = 0
    intMbTxt = 0
    intMbAdn = 0

    auto_cache = __settings__.getBool('auto_cache')
    auto_packages = __settings__.getBool('auto_packages')
    auto_thumbnails = __settings__.getBool('auto_thumbnails')
    auto_addons = __settings__.getBool('auto_addons')
    auto_compact = __settings__.getBool('auto_compact')
    auto_textures = __settings__.getBool('auto_textures')
    auto_userdata = __settings__.getBool('auto_userdata')
    auto_notification = __settings__.getInt('auto_notification')

    if auto_notification == 0:
        a_progress = 1
        a_notif = 1
    elif auto_notification == 1:
        a_progress = 1
        a_notif = 0
    elif auto_notification == 2:
        a_progress = 2
        a_notif = 1
    elif auto_notification == 3:
        a_progress = 2
        a_notif = 0

    actionToken = []

    if auto_cache:
        actionToken.append("cache")
    if auto_packages:
        actionToken.append("packages")
    if auto_thumbnails:
        actionToken.append("thumbnails")
    if auto_addons:
        actionToken.append("addons")

    if os.path.exists('/private/var/mobile/Library/Caches/AppleTV/Video/Other'):
        actionToken.append("atv")

    intC, intMbDel = DeleteFiles(actionToken, a_progress)

    if auto_textures:
        intC, intMbTxt = CleanTextures(a_progress)

    if auto_compact:
        intC, intMbCom = CompactDatabases(a_progress)

    if auto_userdata:
        intC, intMbAdn = deleteAddonData(a_progress)

    intMbTot = intMbDel + intMbCom + intMbTxt + intMbAdn
    mess = __addon__.getLocalizedString(30112)                             # Mb
    mess2 = " (%0.2f %s)" % (intMbTot, mess,)
    strMess = __addon__.getLocalizedString(30031) + mess2                  # Cleanup [COLOR red]done[/COLOR].

    if a_notif == 1:
        xbmc.executebuiltin("XBMC.Notification(%s,%s,5000,%s)" % (__addonname__, strMess, __addon__.getAddonInfo('icon')))

# ============================================================
# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
# ============================================================


if __name__ == '__main__':
    __addon__ = xbmcaddon.Addon(id='script.kcleaner')
    __settings__ = __addon__.getSettings()
    if __settings__.getBool('lock'):
        __settings__.setBool('lock', False)
    booBackgroundRun = __settings__.getBool('autoclean')

    if not booBackgroundRun:
        exit()

    import time

    __addonname__ = __addon__.getAddonInfo('name')
    __version__ = __addon__.getAddonInfo('version')

    xbmc.log("KCLEANER SERVICE >> STARTED VERSION %s" % (__version__))

    auto_lastrun = __settings__.getString('auto_lastrun')
    date_now = int(round(time.time()))

    if auto_lastrun != "":
        date_auto_lastrun = int(auto_lastrun)
        time_difference = date_now - date_auto_lastrun
        time_difference_days = int(time_difference) / 86400
    else:
        __settings__.setString('auto_lastrun', str(int(date_now - 31536000)))
        date_auto_lastrun = 365
        time_difference_days = 365

    auto_interval = __settings__.getInt('auto_interval')

    if auto_interval == 0:
        lastrundays = 1
    elif auto_interval == 1:
        lastrundays = 7
    elif auto_interval == 2:
        lastrundays = 30
    elif auto_interval == 3:
        lastrundays = 90
    else:
        lastrundays = 0

    autostart_delay = __settings__.getInt('autostart_delay')

    if booBackgroundRun:
        xbmc.log("KCLEANER SERVICE >> SERVICE INIT >> LAST RUN " + str(time_difference_days) + " DAYS AGO, SET TO RUN EVERY " + str(lastrundays) + " DAYS, WITH DELAY OF " + str(autostart_delay) + " MINUTE(S)")

        if time_difference_days > lastrundays or lastrundays == 0:
            xbmc.sleep(autostart_delay * 60000)

            if not __settings__.getBool('lock'):
                __settings__.setBool('lock', True)
                xbmc.log('KCLEANER SERVICE >> RUNNING AUTO...')
                AutoClean()
                __settings__.setString('auto_lastrun', str(int(round(time.time()))))
                __settings__.setBool('lock', False)
    else:
        xbmc.log("KCLEANER SERVICE >> SERVICE OFF")

    monitor = SettingMonitor()

    iCounter = 0

    while True:
        if monitor.waitForAbort(2):    # Sleep/wait for abort
            xbmc.log('KCLEANER SERVICE >> EXIT')
            break                      # Abort was requested while waiting. Exit the while loop.
        else:
            if booBackgroundRun:
                iCounter += 1

                if iCounter > 1800:
                    iCounter = 0
                    date_now = int(round(time.time()))
                    time_difference = date_now - date_auto_lastrun
                    time_difference_days = int(time_difference) / 86400

                    xbmc.log("KCLEANER SERVICE >> LAST RUN " + str(time_difference_days) + " DAYS AGO, SET TO RUN EVERY " + str(lastrundays) + " DAYS (NOW: " + str(date_now) + ")")

                    if time_difference_days > lastrundays:
                        if not __settings__.getBool('lock'):
                            __settings__.setBool('lock', True)
                            xbmc.log('KCLEANER SERVICE >> RUNNING AUTO...')
                            AutoClean()
                            date_auto_lastrun = int(round(time.time()))
                            __settings__.setString('auto_lastrun', str(date_auto_lastrun))
                            __settings__.setBool('lock', False)
                            xbmc.log('KCLEANER SERVICE >> END AUTO...')

# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
