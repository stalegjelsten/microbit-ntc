from microbit import *
import utime
import math

OpenLog = False
Use_OLED = True
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

def writing_to(destination):
    clear_oled()
    add_text(0,0,"Skriver til:")
    add_text(0,1,destination)
    return

if Use_OLED == True:
    from ssd1306 import initialize, clear_oled
    from ssd1306_text import add_text
    initialize()
    clear_oled()
    if OpenLog == True:
        writing_to("OpenLog")
    else:
        writing_to("Internminne")

while True:
    if OpenLog == True:
        if button_a.is_pressed() and not button_b.is_pressed():
            uart.init(baudrate=9600, tx=Pin_TX, rx=Pin_RX)
            uart.write("Time;Temp (NTC)\n")
            icon = Image.NO
            while not button_b.is_pressed():
                temp = round(get_centigrade_temp(),2)
                time = round(utime.ticks_ms()/1000,1)
                row = str(time) + ";" + str(temp)
                uart.write(row + "\n")
                if Use_OLED == True:
                    clear_oled()
                    add_text(0,1,row)
                display.show(icon, delay=400, clear=True)
            uart.init(baudrate=115200) # restore Python console
            icon = Image.YES
            clear_oled()

        elif button_a.is_pressed() and button_b.is_pressed():
            OpenLog = False
            icon = Image.ARROW_E
            if Use_OLED == True:
                writing_to("Internminne")

        display.show(icon, delay=400, clear=True)

    elif OpenLog == False:
        if button_a.is_pressed() and not button_b.is_pressed():
            icon = Image.NO
            with open('data.csv', 'w') as datafile:
                datafile.write("Time; Temp (NTC)\n")
                while not button_b.is_pressed():
                    temp = round(get_centigrade_temp(),2)
                    time = round(utime.ticks_ms()/1000,1)
                    datafile.write('{};{}\n'.format(time,temp))
                    display.show(icon, delay=400,clear=True)
                    if Use_OLED == True:
                        clear_oled()
                        row = str(time) + ";" + str(temp)
                        add_text(0,1,row)
            icon = Image.YES

        if button_a.is_pressed() and button_b.is_pressed():
            OpenLog = True
            icon = Image.ARROW_E
            if Use_OLED == True:
                writing_to("OpenLog")

        display.show(icon, delay=400,clear=True)