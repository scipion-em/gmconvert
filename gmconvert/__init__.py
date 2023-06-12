# **************************************************************************
# *
# * Authors:     James Krieger (jmkrieger@cnb.csic.es)
# *
# * Biocomputing Unit, Centro Nacional de Biotecnologia, CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import pwem
from .constants import *
from os.path import join
import subprocess

_logo = "icon.png"
_references = ['Kawabata2018']

GMCONVERT_DIC = {'name': 'gmconvert', 'version': '20220509', 'home': 'GMCONVERT_HOME'}

class Plugin(pwem.Plugin):
    _homeVar = GMCONVERT_DIC['home']
    _pathVars = [GMCONVERT_DIC['home']]
    _supportedVersions = [LATEST]
    _gmconvertName = GMCONVERT_DIC['name'] + '-' + GMCONVERT_DIC['version']

    @classmethod
    def _defineVariables(cls):
        """ Return and write a variable in the config file.
        """
        cls._defineEmVar(GMCONVERT_DIC['home'], cls._gmconvertName)

    @classmethod
    def defineBinaries(cls, env):
        installationCmd = 'wget -O gmconvert-{}.tar.gz {} --no-check-certificate && '. \
          format(GMCONVERT_DIC['version'], cls._getGMConvertDownloadUrl())
        installationCmd += 'tar -xf gmconvert-{}.tar.gz && '.\
          format(GMCONVERT_DIC['version'])
        installationCmd += 'cd src && make &&'

        # Creating validation file
        GMCONVERT_INSTALLED = '%s_installed' % GMCONVERT_DIC['name']
        installationCmd += 'cd .. && touch %s' % GMCONVERT_INSTALLED  # Flag installation finished

        env.addPackage(GMCONVERT_DIC['name'],
                       version=GMCONVERT_DIC['version'],
                       tar='void.tgz',
                       commands=[(installationCmd, GMCONVERT_INSTALLED)],
                       default=True)

    @classmethod
    def _getGMConvertDownloadUrl(cls):
        return 'https://pdbj.org/gmfit/cgi-bin/dwnld_src_file.cgi?filename=gmconvert-src-{}.tar.gz'.format(GMCONVERT_DIC['version'])

    @classmethod
    def getGMConvertBin(cls):
        return join(cls.getVar(GMCONVERT_DIC['home']), 'gmconvert')

    @classmethod
    def runGMConvert(cls, protocol, args='', cwd=None):
        """ Run Gromacs command from a given protocol. """
        protocol.runJob(cls.getGMConvertBin(), args, cwd=cwd)
