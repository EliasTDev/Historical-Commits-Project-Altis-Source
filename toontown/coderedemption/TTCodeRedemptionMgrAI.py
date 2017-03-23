'''
Created on Mar 21, 2017

@author: Drew
'''

import time
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.catalog import CatalogItem
from toontown.catalog.CatalogInvalidItem import CatalogInvalidItem
from toontown.catalog.CatalogClothingItem import CatalogClothingItem
from toontown.catalog.CatalogItemList import CatalogItemList
from toontown.catalog.CatalogPoleItem import CatalogPoleItem
from toontown.catalog.CatalogBeanItem import CatalogBeanItem
from toontown.catalog.CatalogChatItem import CatalogChatItem
from toontown.catalog.CatalogAccessoryItem import CatalogAccessoryItem
from toontown.catalog.CatalogRentalItem import CatalogRentalItem
from toontown.catalog.CatalogGardenItem import CatalogGardenItem
from toontown.catalog.CatalogGardenStarterItem import CatalogGardenStarterItem
from toontown.coderedemption import TTCodeRedemptionConsts
from toontown.toonbase import ToontownGlobals

class TTCodeRedemptionMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("TTCodeRedemptionMgrAI")

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.air = air

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

    def delete(self):
        DistributedObjectAI.delete(self)

    def giveAwardToToonResult(self, todo0, todo1):
        pass

    def redeemCode(self, context, code):
        # Default values. They will get modified if needed
        
        isValid = True
        hasExpired = False
        isEligible = True
        beenDelivered = False
    
        avId = self.air.getAvatarIdFromSender()
        print("%s entered %s" %(avId, code))
        if not avId:
            self.air.writeServerEvent('suspicious', avId = avId, issue = 'Tried to redeem a code from an invalid avId')
            return

        av = self.air.doId2do.get(avId)
        if not av:
            self.air.writeServerEvent('suspicious', avId = avId, issue = 'Invalid avatar tried to redeem a code')
            return

        if not isValid:
            self.air.writeServerEvent('code-redeemed', avId = avId, issue = 'Invalid code: %s' % code)
            self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, ToontownGlobals.CODE_INVALID, 0])
            return

        # Make sure its not expired, which it shouldnt be considering there is none that have expirations :thinking:
        if hasExpired:
            self.air.writeServerEvent('code-redeemed', avId = avId, issue = 'Expired code: %s' % code)
            self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, ToontownGlobals.CODE_EXPIRED, 0])
            return

        # Make sure the toon is allowed to use this code
        if not isEligible:
            self.air.writeServerEvent('code-redeemed', avId = avId, issue = 'Ineligible for code: %s' % code)
            self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, ToontownGlobals.CODE_INELIGIBLE, 0])
            return

        items = self.getItemsForCode(code)
        for item in items:
            if isinstance(item, CatalogInvalidItem): # Incase theres an invalid item type
                self.air.writeServerEvent('suspicious', avId = avId, issue = 'uh oh! invalid item type for code: %s' % code)
                self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, ToontownGlobals.CODE_INVALID, 0])
                break

            if len(av.mailboxContents) + len(av.onGiftOrder) >= ToontownGlobals.MaxMailboxContents:
                # Targets mailbox is full
                beenDelivered = False
                break

            item.deliveryDate = int(time.time() / 60) + 1 # Basically instant delivery
            av.onOrder.append(item)
            av.b_setDeliverySchedule(av.onOrder)
            beenDelivered = True

        if not beenDelivered:
            # Something went wrong!
            self.air.writeServerEvent('code-redeemed', avId = avId, issue = 'Could not deliver items for code: %s' % code)
            self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, ToontownGlobals.CODE_INVALID, 0])
            return

        # send
        self.air.writeServerEvent('code-redeemed', avId = avId, issue = 'Successfuly redeemed code: %s' % code)
        self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, ToontownGlobals.CODE_SUCCESS, 0])

    def getItemsForCode(self, code):
        avId = self.air.getAvatarIdFromSender()
        if not avId:
            self.air.writeServerEvent('suspicious', avId = avId, issue = 'AVID is none')
            return

        av = self.air.doId2do.get(avId)
        if not av:
            self.air.writeServerEvent('suspicious', avId = avId, issue = 'Avatar doesnt exist')
            return

        code = str(code.lower()) # Convert to str and use lowercase bc fuck case sensitivity

        if code == "sillymeter" or code == "silly meter" or code == "silly-meter":
            shirt = CatalogClothingItem(1753, 0)
            return [shirt]

        if code == "getconnected" or code == "get connected" or code == "get_connected":
            shirt = CatalogClothingItem(1752, 0)
            return [shirt]

        if code == "toontastic":
            shirt = CatalogClothingItem(1820, 0)
            return [shirt]

        if code == "gardens":
            gardenStarter = CatalogGardenStarterItem()
            return [gardenStarter]

        if code == "sweet":
            beans = CatalogBeanItem(12000, tagCode = 2)
            return [beans]

        return []

    def redeemCodeAiToUd(self, avId, context, code):
        self.sendUpdate('redeemCodeAiToUd', [avId, context, code])

    def redeemCodeResultUdToAi(self, avId, context, result, awardMgrResult):
        self.d_redeemCodeResult(avId, context, result, awardMgrResult)

    def d_redeemCodeResult(self, avId, context, result, awardMgrResult):
        self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, result, awardMgrResult])
