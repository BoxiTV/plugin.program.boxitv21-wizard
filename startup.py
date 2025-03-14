import xbmc
import xbmcgui
import time
from datetime import datetime
from datetime import timedelta
import os
import sys

try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

from resources.libs.common.config import CONFIG
from resources.libs import clear
from resources.libs import check
from resources.libs import db
from resources.libs.gui import window
from resources.libs.common import logging
from resources.libs.common import tools
from resources.libs import skin
from resources.libs import update

def installed_build_check():
    dialog = xbmcgui.Dialog()

    if not CONFIG.EXTRACT == '100' and CONFIG.EXTERROR > 0:
        logging.log("[Build Installed Check] Build was extracted {0}/100 with [ERRORS: {1}]".format(CONFIG.EXTRACT,
                                                                                                    CONFIG.EXTERROR),
                    level=xbmc.LOGINFO)
        yes = dialog.yesno(CONFIG.ADDONTITLE,'[COLOR {0}]{2}[/COLOR] [COLOR {1}]was not installed correctly![/COLOR]'.format(CONFIG.COLOR1,CONFIG.COLOR2,CONFIG.BUILDNAME)
                           +'\n'+('Installed: [COLOR {0}]{1}[/COLOR] / '
                            'Error Count: [COLOR {2}]{3}[/COLOR]').format(CONFIG.COLOR1, CONFIG.EXTRACT, CONFIG.COLOR1,CONFIG.EXTERROR)
                           +'\n'+'Would you like to try again?[/COLOR]', nolabel='[B]No Thanks![/B]', yeslabel='[B]Retry Install[/B]')
        CONFIG.clear_setting('build')
        if yes:
            xbmc.executebuiltin("PlayMedia(plugin://{0}/?mode=install&name={1}&url=fresh)".format(CONFIG.ADDON_ID,quote_plus(CONFIG.BUILDNAME)))
            logging.log("[Build Installed Check] Fresh Install Re-activated", level=xbmc.LOGINFO)
        else:
            logging.log("[Build Installed Check] Reinstall Ignored")
    elif CONFIG.SKIN in ['skin.confluence', 'skin.estuary', 'skin.estouchy']:
        logging.log("[Build Installed Check] Incorrect skin: {0}".format(CONFIG.SKIN), level=xbmc.LOGINFO)
        defaults = CONFIG.get_setting('defaultskin')
        if not defaults == '':
            if os.path.exists(os.path.join(CONFIG.ADDONS, defaults)):
                if skin.skin_to_default(defaults):
                    skin.look_and_feel_data('restore')
        if not CONFIG.SKIN == defaults and not CONFIG.BUILDNAME == "":
            gui_xml = check.check_build(CONFIG.BUILDNAME, 'gui')

            response = tools.open_url(gui_xml, check=True)
            if not response:
                logging.log("[Build Installed Check] Guifix was set to http://", level=xbmc.LOGINFO)
                dialog.ok(CONFIG.ADDONTITLE,"[COLOR {0}]It looks like the skin settings was not applied to the build.".format(CONFIG.COLOR2)
                          +'\n'+"Sadly no gui fix was attached to the build"
                          +'\n'+"You will need to reinstall the build and make sure to do a force close[/COLOR]")
            else:
                yes = dialog.yesno(CONFIG.ADDONTITLE,'{0} was not installed correctly!'.format(CONFIG.BUILDNAME)
                                       +'\n'+'It looks like the skin settings was not applied to the build.'
                                       +'\n'+'Would you like to apply the GuiFix?',
                                       nolabel='[B]No, Cancel[/B]', yeslabel='[B]Apply Fix[/B]')
                if yes:
                    xbmc.executebuiltin("PlayMedia(plugin://{0}/?mode=install&name={1}&url=gui)".format(CONFIG.ADDON_ID,quote_plus(CONFIG.BUILDNAME)))
                    logging.log("[Build Installed Check] Guifix attempting to install")
                else:
                    logging.log('[Build Installed Check] Guifix url working but cancelled: {0}'.format(gui_xml),level=xbmc.LOGINFO)
    else:
        logging.log('[Build Installed Check] Install seems to be completed correctly', level=xbmc.LOGINFO)
        
    if CONFIG.get_setting('installed') == 'true':
        if CONFIG.get_setting('keeplogin') == 'true':
            from resources.libs import loginit
            logging.log('[Build Installed Check] Restoring Login Data', level=xbmc.LOGINFO)
            loginit.login_it('restore', 'all')

        CONFIG.clear_setting('install')

def build_update_check():
    response = tools.open_url(CONFIG.BUILDFILE, check=True)

    if not response:
        logging.log("[Build Check] Not a valid URL for Build File: {0}".format(CONFIG.BUILDFILE), level=xbmc.LOGINFO)
    elif not CONFIG.BUILDNAME == '':
        if CONFIG.SKIN in ['skin.confluence', 'skin.estuary', 'skin.estouchy'] and not CONFIG.DEFAULTIGNORE == 'true':
            check.check_skin()

        logging.log("[Build Check] Build Installed: Checking Updates", level=xbmc.LOGINFO)
        check.check_build_update()

    CONFIG.set_setting('nextbuildcheck', tools.get_date(days=CONFIG.UPDATECHECK, formatted=True))

def save_login():
    current_time = time.mktime(time.strptime(tools.get_date(formatted=True), "%Y-%m-%d %H:%M:%S"))
    next_save = time.mktime(time.strptime(CONFIG.get_setting('loginnextsave'), "%Y-%m-%d %H:%M:%S"))
    
    if next_save <= current_time:
        from resources.libs import loginit
        logging.log("[Login Info] Saving all Data", level=xbmc.LOGINFO)
        loginit.auto_update('all')
        CONFIG.set_setting('loginnextsave', tools.get_date(days=3, formatted=True))
    else:
        logging.log("[Login Info] Next Auto Save isn't until: {0} / TODAY is: {1}".format(CONFIG.get_setting('loginnextsave'),
                                                                                          tools.get_date(formatted=True)),
                    level=xbmc.LOGINFO)

def auto_clean():
    service = False
    days = [tools.get_date(formatted=True), tools.get_date(days=1, formatted=True), tools.get_date(days=3, formatted=True), tools.get_date(days=7, formatted=True),
            tools.get_date(days=30, formatted=True)]

    freq = int(CONFIG.AUTOFREQ)
    next_cleanup = time.mktime(time.strptime(CONFIG.NEXTCLEANDATE, "%Y-%m-%d %H:%M:%S"))

    if next_cleanup <= tools.get_date() or freq == 0:
        service = True
        next_run = days[freq]
        CONFIG.set_setting('nextautocleanup', next_run)
    else:
        logging.log("[Auto Clean Up] Next Clean Up {0}".format(CONFIG.NEXTCLEANDATE),
                    level=xbmc.LOGINFO)
    if service:
        if CONFIG.AUTOCACHE == 'true':
            logging.log('[Auto Clean Up] Cache: On', level=xbmc.LOGINFO)
            clear.clear_cache(True)
        else:
            logging.log('[Auto Clean Up] Cache: Off', level=xbmc.LOGINFO)
        if CONFIG.AUTOTHUMBS == 'true':
            logging.log('[Auto Clean Up] Old Thumbs: On', level=xbmc.LOGINFO)
            clear.old_thumbs()
        else:
            logging.log('[Auto Clean Up] Old Thumbs: Off', level=xbmc.LOGINFO)
        if CONFIG.AUTOPACKAGES == 'true':
            logging.log('[Auto Clean Up] Packages: On', level=xbmc.LOGINFO)
            clear.clear_packages_startup()
        else:
            logging.log('[Auto Clean Up] Packages: Off', level=xbmc.LOGINFO)

def stop_if_duplicate():
    NOW = time.time()
    temp = CONFIG.get_setting('time_started')
    
    if temp:
        if temp > NOW - (60 * 2):
            logging.log('Killing Start Up Script')
            sys.exit()
            
    logging.log("{0}".format(NOW))
    CONFIG.set_setting('time_started', NOW)
    xbmc.sleep(1000)
    
    if not CONFIG.get_setting('time_started') == NOW:
        logging.log('Killing Start Up Script')
        sys.exit()
    else:
        logging.log('Continuing Start Up Script')

def check_for_video():
    while xbmc.Player().isPlayingVideo():
        xbmc.sleep(1000)


# Don't run the script while video is playing :)
check_for_video()
# Ensure that any needed folders are created
tools.ensure_folders()
# Stop this script if it's been run more than once
# if CONFIG.KODIV < 18:
    # stop_if_duplicate()
# Ensure that the wizard's name matches its folder
check.check_paths()

# BUILD INSTALL PROMPT
if tools.open_url(CONFIG.BUILDFILE, check=True) and CONFIG.get_setting('installed') == 'false':
    logging.log("[Current Build Check] Build Not Installed", level=xbmc.LOGINFO)
    window.show_build_prompt()
else:
    logging.log("[Current Build Check] Build Installed: {0}".format(CONFIG.BUILDNAME), level=xbmc.LOGINFO)

# ENABLE ALL ADDONS AFTER INSTALL
if CONFIG.get_setting('enable_all') == 'true':
    logging.log("[Post Install] Enabling all Add-ons", level=xbmc.LOGINFO)
    from resources.libs.gui import menu
    menu.enable_addons(all=True)
    if os.path.exists(os.path.join(CONFIG.USERDATA, '.enableall')):
    	logging.log("[Post Install] .enableall file found in userdata. Deleting..", level=xbmc.LOGINFO)
    	import xbmcvfs
    	xbmcvfs.delete(os.path.join(CONFIG.USERDATA, '.enableall'))
    xbmc.executebuiltin('UpdateLocalAddons')
    xbmc.executebuiltin('UpdateAddonRepos')
    db.force_check_updates(auto=True)
    CONFIG.set_setting('enable_all', 'false')
    xbmc.executebuiltin("ReloadSkin()")
    tools.reload_profile(xbmc.getInfoLabel('System.ProfileName'))

# BUILD UPDATE CHECK
buildcheck = CONFIG.get_setting('nextbuildcheck')
if CONFIG.get_setting('buildname'):
    current_time = time.time()
    epoch_check = time.mktime(time.strptime(buildcheck, "%Y-%m-%d %H:%M:%S"))
    
    if current_time >= epoch_check:
        logging.log("[Build Update Check] Started", level=xbmc.LOGINFO)
        build_update_check()
else:
    logging.log("[Build Update Check] Next Check: {0}".format(buildcheck), level=xbmc.LOGINFO)

# REINSTALL ELIGIBLE BINARIES
binarytxt = os.path.join(CONFIG.USERDATA, 'build_binaries.txt')
if os.path.exists(binarytxt):
    logging.log("[Binary Detection] Reinstalling Eligible Binary Addons", level=xbmc.LOGINFO)
    from resources.libs import restore
    restore.restore('binaries')
else:
    logging.log("[Binary Detection] Eligible Binary Addons to Reinstall", level=xbmc.LOGINFO)

# INSTALLED BUILD CHECK
if CONFIG.get_setting('installed') == 'true':
    logging.log("[Build Installed Check] Started", level=xbmc.LOGINFO)
    installed_build_check()
else:
    logging.log("[Build Installed Check] Not Enabled", level=xbmc.LOGINFO)

# SAVE LOGIN
if CONFIG.get_setting('keeplogin') == 'true':
    logging.log("[Login Info] Started", level=xbmc.LOGINFO)
    save_login()
else:
    logging.log("[Login Info] Not Enabled", level=xbmc.LOGINFO)

# AUTO CLEAN
if CONFIG.get_setting('autoclean') == 'true':
    logging.log("[Auto Clean Up] Started", level=xbmc.LOGINFO)
    auto_clean()
else:
    logging.log('[Auto Clean Up] Not Enabled', level=xbmc.LOGINFO)

	
