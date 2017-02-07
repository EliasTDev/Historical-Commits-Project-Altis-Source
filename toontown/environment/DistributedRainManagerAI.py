from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.task.Task import Task
from toontown.toonbase import TTLocalizer
import random
import time
from direct.showbase import PythonUtil
import DayTimeGlobals
from DistributedWeatherMGRAI import DistributedWeatherMGRAI

class DistributedRainManagerAI(DistributedWeatherMGRAI):
    notify = directNotify.newCategory('DistributedRainManagerAI')
    
    def __init__(self, air):
        DistributedWeatherMGRAI.__init__(self, air)

    def announceGenerate(self):
        DistributedWeatherMGRAI.announceGenerate(self)

        Sequence(
            Func(self.b_setState, 'Sunny'),
            Wait(1800),
            Func(self.b_setState, 'Rain'),
            Wait(900)).loop()

    def enterRain(self):
        pass
        
    def exitRain(self):
        pass

    def enterSnow(self):
        pass

    def exitSnow(self):
        pass
        
    def enterSunny(self):
        pass
        
    def exitSunny(self):
        pass