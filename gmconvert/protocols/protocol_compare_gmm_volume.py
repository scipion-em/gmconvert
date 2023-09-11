# -*- coding: utf-8 -*-
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
# *  e-mail address 'jmkrieger@cnb.csic.es'
# *
# **************************************************************************


"""
This module will provide the conversion of a volume to a Gaussian mixture model
"""
from pyworkflow.protocol import Protocol, params
from pyworkflow.utils import exists

from pwem.objects import Volume

from gmconvert import Plugin as gmconvertPlugin

class GMConvertCompareVolume(Protocol):
    """
    This protocol will convert a volume to a Gaussian mixture model
    """
    _label = 'gmconvert compare volume'

    IMPORT_FROM_FILES = 0
    USE_POINTER = 1

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label='gmconvert compare volume')
        form.addParam('inputVolume', params.PointerParam, label="Input volume",
                      important=True,
                      pointerClass='Volume',
                      help='The volume to be converted')
        
        form.addParam('inputGmmData', params.EnumParam, choices=['file', 'pointer'],
                      label="Import atomic structure from",
                      default=self.USE_POINTER,
                      display=params.EnumParam.DISPLAY_HLIST,
                      help='Choose whether to import GMM data from file path or pointer')
        form.addParam('gmmFile', params.PathParam, label="File path",
                      condition='inputGmmData == IMPORT_FROM_FILES',
                      allowsNull=True,
                      help='Specify a path to desired GMM.')
        form.addParam('inputGmm', params.PointerParam, label="Input GMM",
                      condition='inputGmmData == USE_POINTER',
                      pointerClass='EMFile',
                      help='The input GMM can be based on an atomic model '
                           'or an EM volume')
        
        form.addParam('cutoff', params.FloatParam,
                      default=0.05, label='threshold', important=True,
                      help='cutoff for thresholding the volume')
        
        form.addParam('outMap', params.StringParam,
                      default='', label='Output map filename')

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('convertStep')
        self._insertFunctionStep('createOutputStep')

    def convertStep(self):

        if self.inputGmmData == self.IMPORT_FROM_FILES:
            self.inputGmmFn = self.gmmFile.get()
            if not exists(self.inputGmmFn):
                raise ValueError("GMM not found at *%s*" % self.inputGmmFn)
        else:
            self.inputGmmFn = self.inputGmm.get().getFileName()

        args = 'VcmpG -imap {0} -igmm {1} -omap {2} -cutoff {3}'.format(self.inputVolume.get().getFileName(), 
                                                                        self.inputGmmFn, self._getPath(self.outMap.get()), 
                                                                        self.cutoff.get())

        try:
            gmconvertPlugin.runGMConvert(self, args)
        except:
            # check if it actually finished correctly
            fi = open(self._getLogsPath('run.stdout'), 'r')
            lines = fi.readlines()
            fi.close()

            if not lines[-1].startswith('COMP_TIME_SEC_FINAL'):
                # gmconvert usually raises an non-zero error code regardless 
                # so we should go and read the error information from the log file
                log = open(self._getLogsPath("run.stderr"), 'r')
                if len(log.read().splitlines()) > 0:
                    for line in log.read().splitlines():
                        self.info("ERROR: %s." % line)
                        raise ChildProcessError("gmconvert has failed: %s. See error log "
                                                "for more details." % line) from None

    def createOutputStep(self):
        outVol = Volume()
        outVol.setSamplingRate(self.inputVolume.get().getSamplingRate())
        outVol.setLocation(self._getPath(self.outMap.get()))
        self._defineOutputs(outputVolume=outVol)

    # --------------------------- INFO functions -----------------------------------
