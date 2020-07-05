from microbit import *
import utime
import math
import os

internt_filnavn = "data"    # første del av filnavnet
sleeptime = 9380    # det tar omtrent 620 ms å gjennomføre syklusen
                    # slik at en sleeptime på 380 vil gi omtrent 1 sek
                    # mellom hver måling. OBS! Micro:bit har kun plass til
                    # omtrent 2200 måleverdier i sitt minne i tillegg til dette
                    # programmet. Verdi i millisekunder

R_ref = 10e3    # 10 kOhm resistans kobles i serie med NTC
Pin_NTC = pin1  # pin for NTC sensor

# Steinhart og Hart sin formel for temperatur fra NTC er gitt ved
# T = (A + B * ln(R/R_ref) + C * ln(R/R_ref)^2 + D * ln(R/R_ref)^3
# Verdiene nedenfor gjelder for B_25/85 = 3977

A = 3.354016e-3
B = 2.569850e-4
C = 2.620131e-6
D = 6.383091e-8

row = ""
icon = Image.ASLEEP
filnummer = 0

def get_centigrade_temp():
    # les signal fra NTC og returner temperaturen i grader celsius
    NTC_read = Pin_NTC.read_analog()
    R_NTC = R_ref * NTC_read / (1023 - NTC_read)
    log_NTC = math.log(R_NTC/R_ref)
    temp = 1/(A + B * log_NTC + C * log_NTC ** 2 + D * log_NTC ** 3)-273.15
    return temp

while True:
    if button_a.is_pressed():
        # åpner filen spesifisert i internt_filnavn og skriver til den
        icon = Image.NO
        success = False
        while not success:
            # finner neste ledige filnavn
            try:
                # prøver å åpne filnavnet med gjeldende filnummer
                # hvis filen finnes så lukkes den, og vi øker filnummer +1
                f = open(internt_filnavn + str(filnummer) + ".csv", "r")
                f.close()
                filnummer = filnummer + 1
            except OSError:
                # hvis filen ikke finnes så avslutter vi letingen
                success = True
                display.scroll("Filnavn: " + internt_filnavn + \
                    str(filnummer) + ".csv")

        with open(internt_filnavn + str(filnummer) + ".csv", 'w') as datafile:
            # åpner den ledige filen for skriving
            datafile.write("Time; Temp (NTC)\n")
            while not button_b.was_pressed():
                # hent temperatur og tidsverdier og skriv til filen
                temp = round(get_centigrade_temp(),2)
                time = round(utime.ticks_ms()/1000,1)
                datafile.write('{};{}\n'.format(time,temp))
                display.show(round(temp),delay=200,clear=True)
                sleep(sleeptime)
        icon = Image.YES

    display.show(icon, delay=400,clear=True)

    if accelerometer.current_gesture() == "shake":
        # sletter alle filer dersom vi rister på enheten
        # for å slette må vi bekrefte med å trykke på begge knapper
        display.show(Image.GHOST, delay=3000, clear=True)
        if button_a.is_pressed() and button_b.is_pressed():
            filnummer = 0
            success = False
            while success == False:
                # finner neste ledige filnavn
                try:
                    # prøver å åpne filnavnet med gjeldende filnummer
                    # hvis filen finnes så lukkes den, og vi øker filnummer +1
                    f = open(internt_filnavn + str(filnummer) + ".csv", "r")
                    f.close()
                    os.remove(internt_filnavn + str(filnummer) + ".csv")
                    filnummer = filnummer + 1
                except OSError:
                    # hvis filen ikke finnes så avslutter vi letingen
                    success = True
                    display.scroll("Slettet alt")
