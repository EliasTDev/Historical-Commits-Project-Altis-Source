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
from toontown.hood import Place
import DayTimeGlobals
from DistributedWeatherMGR import DistributedWeatherMGR
from toontown.battle import BattleParticles

class DistributedRainManager(DistributedWeatherMGR):
    notify = directNotify.newCategory('DistributedRainManager')
    
    def __init__(self, cr):
        DistributedWeatherMGR.__init__(self, cr)
        self.cr = cr
        self.currentWeather = None
        self.rain = None
        self.rainRender = None
        self.rainSound = None
        self.nextWindTime = 0

    def generate(self):
        DistributedWeatherMGR.generate(self)
        
    def announceGenerate(self):
        DistributedWeatherMGR.announceGenerate(self)
        
    def delete(self):
        DistributedWeatherMGR.delete(self)
        if self.currentWeather == 0:
            self.rain.cleanup()
            taskMgr.remove('snowWind')
            if self.rainSound:
                self.rainSound.stop()
                del self.rainSound
            
            del self.rain
            del self.rainRender

    def enterRain(self, timestamp):
        self.rain = BattleParticles.loadParticleFile('raindisk.ptf')
        self.rain.setPos(0, 0, 20)
        self.rainRender = render.attachNewNode('rainRender')
        self.rainRender.setDepthWrite(0)
        self.rainRender.setBin('fixed', 1)
        self.rain.start(camera, self.rainRender)
        
        self.rainSound = base.loadSfx('phase_12/audio/sfx/CHQ_rain_ambient.ogg')
        base.playSfx(self.rainSound, looping=1, volume=0.25)
        
        self.currentWeather = 0
        
    def exitRain(self):
        pass

    def enterSnow(self, timestamp):
        self.rain = BattleParticles.loadParticleFile('snowdisk.ptf')
        self.rain.setPos(0, 0, 20)
        self.rainRender = render.attachNewNode('rainRender')
        self.rainRender.setDepthWrite(0)
        self.rainRender.setBin('fixed', 1)
        self.rain.start(camera, self.rainRender)
        
        # Winter time stuff
        self.wind1Sound = base.loadSfx('phase_8/audio/sfx/SZ_TB_wind_1.ogg')
        self.wind2Sound = base.loadSfx('phase_8/audio/sfx/SZ_TB_wind_2.ogg')
        self.wind3Sound = base.loadSfx('phase_8/audio/sfx/SZ_TB_wind_3.ogg')
        taskMgr.add(self.snowWindSoundTask, 'snowWind')
        
        self.currentWeather = 0
    
    def exitSnow(self):
        taskMgr.remove('snowWind')
        
    def enterSunny(self, timestamp):
        if self.rain:
            self.rain.cleanup()
            if self.rainSound:
                self.rainSound.stop()
                del self.rainSound
            
            del self.rain
            del self.rainRender
            taskMgr.remove('snowWind')
        
        self.currentWeather = 1

    def exitSunny(self):
        pass
        
    def snowWindSoundTask(self, task):
        now = globalClock.getFrameTime()
        if now < self.nextWindTime:
            return Task.cont
        
        randNum = random.random()
        wind = int(randNum * 100) % 3 + 1
        if wind == 1:
            base.playSfx(self.wind1Sound)
        elif wind == 2:
            base.playSfx(self.wind2Sound)
        elif wind == 3:
            base.playSfx(self.wind3Sound)
        
        self.nextWindTime = now + randNum * 8.0
        return Task.cont
        