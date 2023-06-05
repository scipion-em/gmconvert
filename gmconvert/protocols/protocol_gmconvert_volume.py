# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     James Krieger (jmkrieger@cnb.csic.es)
# *
# * your institution
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
from pwem.objects import EMFile


class GMConvertVolume(Protocol):
    """
    This protocol will convert a volume to a Gaussian mixture model
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
        form.addParam('inputVolume', params.PointerParam, label="Input volume",
                      important=True,
                      pointerClass='Volume',
                      help='The volume to be converted')
        
        form.addParam('cutoff', params.FloatParam,
                      default=10, label='threshold', important=True,
                      help='cutoff for thresholding the volume')        

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
        args = 'V2G -imap {0} -ogmm {1} -cutoff {2} -ng {3}'.format(self.inputStructure.get().getFileName(), 
                                                                    self.outFn.get(), self.cutoff.get(), 
                                                                    self.numGaussians.get())
        self.runJob('gmconvert', args)

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
