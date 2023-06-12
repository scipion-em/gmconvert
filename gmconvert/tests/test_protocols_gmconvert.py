# **************************************************************************
# *
# * Authors:     James Krieger (jmkrieger@cnb.csic.es)
# *
# * Biocomputing Unit, Centro Nacional de Biotecnologia, CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
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

from pyworkflow.tests import BaseTest, setupTestProject
from pwem.protocols import ProtImportVolumes, ProtImportPdb
import pwem
import shutil, os

from ..protocols import GMConvertAtomStruct, GMConvertVolume


FROM_FILE, FROM_SCIPION = 0, 1

class TestGMConvert(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)

    def test_gmconvertPdb(cls):
        cls._runImportPDB()
        cls._runConvertPdb()

    def test_gmconvertVol(cls):
        cls._runImportVolumes()
        cls._runConvertVol()

    @classmethod
    def _runImportVolumes(cls):
        """ Run an Import volumes protocol. """
        protImportVol = cls.newProtocol(
            ProtImportVolumes,
            importFrom=1,
            emdbId='2190')
        cls.launchProtocol(protImportVol)
        cls.protImportVol = protImportVol

    @classmethod
    def _runImportPDB(cls):
        protImportPDB = cls.newProtocol(
            ProtImportPdb,
            inputPdbData=0,
            pdbId='5c44')
        cls.launchProtocol(protImportPDB)
        cls.protImportPDB = protImportPDB

    def _runConvertVol(self):
        protVol = self.newProtocol(
            GMConvertVolume,
            inputVolume=self.protImportVol.outputVolume,
            cutoff=0.0666, numGaussians=10,
            outFn='2190_ng10.gmm')

        self.launchProtocol(protVol)
        gmmOut = getattr(protVol, 'outFile', None)
        self.assertIsNotNone(gmmOut)

    def _runConvertPdb(self):
        protPdb = self.newProtocol(
            GMConvertAtomStruct,
            inputStructure=self.protImportPDB.outputPdb,
            numGaussians=10,
            outFn='5c44_ng10.gmm')

        self.launchProtocol(protPdb)
        gmmOut = getattr(protPdb, 'outFile', None)
        self.assertIsNotNone(gmmOut)



