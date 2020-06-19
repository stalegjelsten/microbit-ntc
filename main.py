from microbit import *
import utime
import math

'''
Temperaturavlesning med NTC og microbit
=======================================

Dette scriptet for microbits micropython leser temperaturen fra en NTC-sensor
slik som ble levert til CanSat 2018 (se 
https://www.narom.no/undervisningsressurser/the-cansat-book/v3/ ) og lagrer
dataene som en .csv-fil på et eksternt SD-kort via SparkFun OpenLog eller 
internt på microbiten sitt minne.

Hold nede b-knappen for å avbryte avslutte lagringen av data

Oppsett av variabler
====================

OpenLog = True hvis du ønsker å bruke SparkFun openlog til å lagre data fra 
temperatursensoren. Dersom denne settes til False vil dataene lagres direkte
på Microbiten som du kan hente ut ved å bruke verktøyet ufs (microfs) eller
filer-verktøyet i Mu.

R_ref er verdien (i Ohm) på resistansen som kobles i serie med NTC-sensoren

Pin_NTC, TX og RX må korrespondere med riktige pins på microbiten
'''

OpenLog = False
R_ref = 10e3 #10 kOhm resistans
Pin_NTC = pin1 #pin for NTC sensor
Pin_TX = pin15 #pin for sending av informasjon fra microbit --> sdkort
               # (kobles til rx på OpenLog)
Pin_RX = pin14 #pin for mottak av informasjon fra microbit --> sdkort
               # (kobles til tx på OpenLog)

# Steinhart og Hart sin formel for temperatur fra NTC er gitt ved
# T = (A + B * ln(R/R_ref) + C * ln(R/R_ref)^2 + D * ln(R/R_ref)^3
# Verdiene nedenfor gjelder for B_25/85 = 3977

A = 3.354016e-3 
B = 2.569850e-4
C = 2.620131e-6
D = 6.383091e-8

row = "" 
icon = Image.ASLEEP

def get_centigrade_temp():
    # les signal fra NTC og returner temperaturen i grader celsius
    NTC_read = Pin_NTC.read_analog()
    R_NTC = R_ref * NTC_read / (1023 - NTC_read)
    log_NTC = math.log(R_NTC/R_ref)
    temp = 1/(A + B * log_NTC + C * log_NTC ** 2 + D * log_NTC ** 3)-273.15
    return temp

while True:
    if OpenLog == True:
        temp = round(get_centigrade_temp(),2)
        time = utime.ticks_ms()
        if button_a.is_pressed() and not button_b.is_pressed():
            uart.init(baudrate=9600, tx=Pin_TX, rx=Pin_RX)
            uart.write("Time;Temp (NTC);Temp mbit\n")
            icon = Image.NO
        elif button_b.is_pressed() and not button_a.is_pressed():
            uart.init(baudrate=115200)
            icon = Image.ASLEEP
        elif button_a.is_pressed() and button_b.is_pressed():
            OpenLog = False
            icon = Image.ARROW_E
        row = str(time) + ";" + str(temp) + ";" + str(temperature()) + "\n"
        uart.write(row)
        display.show(icon, delay=400, clear=True)
    elif OpenLog == False:
        if button_a.is_pressed() and not button_b.is_pressed():
            icon = Image.NO
            with open('data.csv', 'w') as datafile:
                while not button_b.is_pressed():
                    temp = round(get_centigrade_temp(),2)
                    time = utime.ticks_ms()
                    datafile.write('{};{};{}\n'.format(time,temp,temperature()))
                    display.show(icon, delay=400,clear=True)
            icon = Image.YES
        if button_a.is_pressed() and button_b.is_pressed():
            OpenLog = True
            icon = Image.ARROW_E
        display.show(icon, delay=400,clear=True)