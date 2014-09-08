#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import json
import yaml
import logging
import random
import copy
import time
import smtplib
from email.mime.text import MIMEText

# configure logging
logging.basicConfig(filename='log/wichtele.log', format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%d-%m %H:%M:%S', level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s [%(name)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
log = logging.getLogger(__name__)

class YamlConfig (object):
    def __init__(self, filename = None):
        self.filename = filename
        self.values = {}
        if filename:
            self.load()

    def load(self):
        f = open(self.filename)
        self.values = yaml.safe_load(f)
        f.close()

    def get_values(self):
        return self.values

    def set_values(self, values):
        self.values = values

def getWichteli(wichteli):
    aValues = random.choice(wichteli)
    aIndex = wichteli.index(aValues)
    wichteli.pop(aIndex)
    return (wichteli, aValues)

def getKey(myDict):
    for key in myDict.keys():
        return key

def getValue(myList, myKey):
    for pair in myList:
        try:
            return pair[myKey]
        except KeyError:
            pass

def calculate(config):
    solutionFound = False
    calcCountTotal = 0

    while not solutionFound:
        log.debug("Starting to solve")
        result = []
        pairsFound = False
        wichteliS = copy.copy(config['wichteli'])
        wichteliR = copy.copy(config['wichteli'])

        maxRuns = 10 * len(config['wichteli']) ^ 2
        
        calcCount = 0
        while not pairsFound:
            calcCount += 1

            if calcCount > maxRuns:
                log.debug("Unresolvable!")
                calcCountTotal += calcCount
                break 

            wichteliST = copy.copy(wichteliS)
            wichteliRT = copy.copy(wichteliR)
            (wichteliST, A) = getWichteli(wichteliST)
            (wichteliRT, B) = getWichteli(wichteliRT)

            if A != B:
                nameA = getKey(A)
                nameB = getKey(B)
                badPair = False

                try:
                    for entry in config['notwant'][nameA]:
                        if entry == nameB:
                            badPair = True
                except Exception:
                    pass
                try:
                    for entry in config['notwant'][nameB]:
                        if entry == nameA:
                            badPair = True
                except Exception:
                    pass

                if not badPair:
                    wichteliS = wichteliST
                    wichteliR = wichteliRT
                    log.debug("Result found: %s - %s" % (nameA, nameB))
                    result.append((nameA, nameB))
                    calcCountTotal += calcCount
                    calcCount = 0

            if len(wichteliR) == 0:
                pairsFound = True
                solutionFound = True

    log.info("Needed calculations: %s" % (calcCountTotal))
    return result

def sendEmail(config, donator, reciever, donatorEmail):
    log.debug("Sending email to %s (for %s)" % (donator, reciever))

    msg = MIMEText('Hallo %s\n\nDein Wichteli fuer dieses Jahr ist: %s\n\nBitte antworte NICHT auf dieses email!\n\nGruss,\nein Programm von Marc :)' % (donator.title(), reciever.title()))
    msg['Subject'] = 'Wichtele %s' % time.strftime('%Y')
    msg['From'] = config['from']
    msg['To'] = donatorEmail

    s = smtplib.SMTP(config['server'])
    s.login(config['login'], config['password'])
    s.sendmail(config['from'], [msg['To']], msg.as_string())
    s.quit()

if __name__ == "__main__":
    log.debug("Loading config")
    origConfig = YamlConfig("config/wichtele.yml").get_values()

    log.info("Beginning calculations")
    for (donator, reciever) in calculate(origConfig):
        donatorEmail = getValue(origConfig['wichteli'], donator)
        sendEmail(origConfig['email'], donator, reciever, donatorEmail)
    
    log.info("Finished!")