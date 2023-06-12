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
This module will provide conversion of an atomic structure to a Gaussian mixture model
"""
from pyworkflow.protocol import Protocol, params
from pwem.objects import EMFile

from gmconvert import Plugin as gmconvertPlugin

class GMConvertAtomStruct(Protocol):
    """
    This protocol will convert an atomic structure to a Gaussian mixture model
    """
    _label = 'gmconvert atomic structure'

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label='gmconvert atomic structure')
        form.addParam('inputStructure', params.PointerParam, label="Input structure",
                      important=True,
                      pointerClass='AtomStruct',
                      help='The input structure can be an atomic model '
                           '(true PDB) or a pseudoatomic model '
                           '(an EM volume converted into pseudoatoms)')

        form.addParam('numGaussians', params.IntParam,
                      default=10, label='number of Gaussians', important=True)

        form.addParam('outFn', params.StringParam,
                      default='', label='Output filename', important=True)

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('convertStep')
        self._insertFunctionStep('createOutputStep')

    def convertStep(self):
        args = 'A2G -ipdb {0} -ng {1} -ogmm {2}'.format(self.inputStructure.get().getFileName(),
                                                        self.numGaussians.get(), 
                                                        self._getPath(self.outFn.get()))
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
        # register how many times the message has been printed
        # Now count will be an accumulated value
        outputFile = EMFile(filename=self._getPath(self.outFn.get()))
        self._defineOutputs(outFile=outputFile)

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []
        if self.isFinished():
            summary.append("This protocol has converted {0} to a GMM in {0}." % (self.inputStructure.get().getFileName(), 
                                                                                 self._getPath(self.outFn.get())))
        return summary

    def _methods(self):
        methods = []
        if self.isFinished():
            methods.append("This protocol has converted {0} to a GMM in {0}." % (self.inputStructure.get().getFileName(), 
                                                                                 self._getPath(self.outFn.get())))
        return methods
