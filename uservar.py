import xbmcaddon
import os

ADDON_ID = xbmcaddon.Addon().getAddonInfo('id')
PATH = xbmcaddon.Addon().getAddonInfo('path')
ART = os.path.join(PATH, 'resources', 'media')

ADDONTITLE = '[COLORdeepskyblue]BoxiTV-Kodi 21 Omega[/COLOR] Wizard'
BUILDERNAME = 'BoxiTV'
EXCLUDES = [ADDON_ID, 'plugin.program.boxitv21-wizard']
BUILDFILE = 'https://shorturl.at/EIi5p'
UPDATECHECK = 0

ICONBUILDS = os.path.join(ART, 'builds.png')
ICONCLEAN = os.path.join(ART, 'clean.png')
ICONREPO = os.path.join(ART, 'repo.png')
ICONNET = os.path.join(ART, 'network.png')
ICONSAVE = os.path.join(ART, 'save.png')
ICONLOGIN = os.path.join(ART, 'login.png')
ICONLOG = os.path.join(ART, 'log.png')
ICONDEV = os.path.join(ART, 'dev.png')
ICONSETTINGS = os.path.join(ART, 'settings.png')

HIDESPACERS = 'No'
SPACER = '='

COLOR1 = 'deepskyblue'
COLOR2 = 'lime'
THEME1 = u'[COLOR {color1}]BoxiTV[/COLOR] Wizard'.format(color1=COLOR1, color2=COLOR2)
THEME2 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
THEME3 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
THEME4 = u'Aktuelles Build: [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
THEME5 = u'[COLOR {color1}]Aktuelles Theme:[/COLOR] {{}}'.format(color1=COLOR1, color2=COLOR2)




