# Copyright (c) 2015, UT-BATTELLE, LLC
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


'''
Master module for dome performance test cases.  Inherits methods from the AbstractTest
class from the Test module.  Dome specific performance tests are performed by calling
the run() method, which passes the necessary information to the runDomePerformance()
method.

Created on Dec 8, 2014

@author: arbennett
'''
import os
import fnmatch

from performance.base import AbstractTest
from util.parser import Parser
import util.variables

def getName(): return "Dome"

'''
Main class for handling dome performance validation

The dome test cases inherit functionality from AbstractTest for
generating scaling plots and generating the output webpage.
'''
class Test(AbstractTest):

    ''' Constructor '''
    def __init__(self):
        super(self.__class__, self).__init__()
        self.name = "Dome"
        self.modelDir = util.variables.inputDir + os.sep + "dome"
        self.benchDir = util.variables.benchmarkDir + os.sep + "dome"
        self.description = "3-D paraboloid dome of ice with a circular, 60 km" + \
                      " diameter base sitting on a flat bed. The horizontal" + \
                      " spatial resolution studies are 2 km, 1 km, 0.5 km" + \
                      " and 0.25 km, and there are 10 vertical levels. For this" + \
                      " set of experiments a quasi no-slip basal condition in" + \
                      " imposed by setting. A zero-flux boundary condition is" + \
                      " applied to the dome margins. "

    '''
    Runs the performance specific test cases.
    
    When running a test this call will record the specific test case
    being run.  Each specific test case string is run via the 
    runDomePerformance function.  All of the data pulled is then
    assimilated via the runScaling method defined in the base class
    '''
    def run(self):
        if not (os.path.exists(self.modelDir) and os.path.exists(self.benchDir)):
            print("    Could not find data for dome verification!  Tried to find data in:")
            print("      " + self.modelDir)
            print("      " + self.benchDir)
            print("    Continuing with next test....")
            return
        resolutions = set()
        modelConfigFiles = fnmatch.filter(os.listdir(self.modelDir), 'dome*.config')
        for mcf in modelConfigFiles:
            resolutions.add( mcf.split('.')[1] )
        resolutions = sorted( resolutions )
        
        for resolution in resolutions:
            self.runDome(resolution, self.modelDir, self.benchDir)
            #self.testsRun.append("Dome " + resolution)
        self.runScaling('dome', resolutions)
        self.testsRun.append('Scaling')


    '''
    Run an instance of dome performance testing
    
    @param resolution: the size of the test being analyzed
    @param perfDir: the location of the performance data
    @param perfBenchDir: the location of the benchmark performance data
    '''
    def runDome(self, resolution, perfDir, perfBenchDir):
        print("  Dome " + resolution + " performance testing in progress....")

        # Process the configure files
        domeParser = Parser()
        self.modelConfigs['Dome ' + resolution], self.benchConfigs['Dome ' + resolution] = \
                domeParser.parseConfigurations(perfDir, perfBenchDir, "*" + resolution + "*.config")

        # Scrape the details from each of the files and store some data for later
        self.fileTestDetails["Dome " + resolution] = domeParser.parseStdOutput(perfDir, "dome." + resolution + ".*.config.oe")

        # Go through and pull in the timing data
        self.modelTimingData['dome' + resolution] = domeParser.parseTimingSummaries(perfDir, 'dome', resolution)
        self.benchTimingData['dome' + resolution] = domeParser.parseTimingSummaries(perfBenchDir, 'dome', resolution)

        # Record the data from the parser
        numberOutputFiles, numberConfigMatches, numberConfigTests = domeParser.getParserSummary()

        self.summary['dome' + resolution] = [numberOutputFiles, numberConfigMatches, numberConfigTests]
