from pijuice import PiJuice
from time import sleep
from signal import pause
from gpiozero import Button,LED
from random import shuffle

buttons = []
pijuice = PiJuice(1, 0x14)

# available pins 4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,22,23,24,26,27

###################################################
# CONTROL FUNCTIONS                               #
###################################################

def savecurrentvalues():
  currentvalues = []
  for relay in relays: currentvalues.append(relay.value)
  return currentvalues

def restoresavedvalues(saved):
  for i in range(len(saved)): relays[i].value = saved[i]

def alloff():
  for relay in relays:
    relay.off()

def allon():
  for relay in relays:
    relay.on()

def allblink(timeon=0.1, timeoff=0.1):
  allon()
  sleep(timeon)
  alloff()
  sleep(timeoff)

def alltoggle():
  for relay in relays:
    relay.toggle()

###################################################
# ACTION FUNCTIONS                                #
###################################################

def starfield(repeat=5, timeon=0.1):
  currentvalues = savecurrentvalues()
  alloff()
  if relays[4].is_lit:
    relays[4].off()
  else:
    for x in range(repeat):
      a = [i for i in range(0,10)]
      shuffle(a)
      for i in a:
        relays[i].on()
        sleep(timeon)
        relays[i].off()
    relays[4].on()
  restoresavedvalues(currentvalues)

def showcharge():
  chargelevel = pijuice.status.GetChargeLevel()['data']
  illcount = int(chargelevel / 10)
  relays[9].toggle() #turn this back to it's original state before we long pressed
  currentvalues = savecurrentvalues()
  alloff()
  print(f"Showing {illcount} illuminated buttons for {chargelevel}% battery charge ")
  for i in range(len(relays)):
    if i < illcount: relays[i].on()
  sleep(3)
  restoresavedvalues(currentvalues)

def cycle(repeat=1, timeon=0.05):
  alloff()
  for i in range(repeat):
    for relay in relays:
      relay.on()
      sleep(timeon)
      relay.off()

def explode(repeat=1, timeon=0.05, timeoff=0.05):
  alloff()
  for i in range(repeat):
    allblink(timeon,timeoff)

def countdown(blinkcount=2, timeon=0.05, timeoff=0, button=None):
  allon()
  for relay in relays:
    for i in range(blinkcount):
      relay.on()
      sleep(timeon)
      relay.off()
      sleep(timeoff)
      if not button.is_pressed: return

def knightrider(button):
  while button.is_pressed:
    for n in range(5):
      relays[n].on()
      relays[-1-n].on()
      sleep(0.2)
      relays[n].off()
      relays[-1-n].off()
    for n in range(3,0,-1):
      relays[n].on()
      relays[-1-n].on()
      sleep(0.2)
      relays[n].off()
      relays[-1-n].off()
  relays[0].on()
  relays[9].on()
  sleep(0.2)
  relays[0].off()
  relays[9].off()


###################################################
# OBJECT SETUP                                    #
###################################################

def buttonpress(button):
  #print(f"{button.pin} was pressed")
  i = pins.index(str(button.pin))
  function = names[i]
  # print(f"Executing {function}")
  if function == "Nuke":
    print("Preparing to launch nuclear missile. Release button to cancel.")
    currentvalues = savecurrentvalues()
    countdown(blinkcount=5, button=button)
    if button.is_pressed:
      print("\tLaunching nuclear missile.")
      explode(10)
    else:
      print("\tCancelling nuclear missle launch.")
    restoresavedvalues(currentvalues)

  elif function == "Eject":
    print("Preparing to eject passenger. Release button to cancel.")
    currentvalues = savecurrentvalues()
    countdown(blinkcount=3, button=button)
    if button.is_pressed:
      print("\tEjecting passenger.")
      explode(5)
    else:
      print("\tEjection cancelled")
    restoresavedvalues(currentvalues)

  elif function == "Oil Slick":
    print("Releasing oil slick. Release button to cancel.")
    currentvalues = savecurrentvalues()
    while button.is_pressed: cycle(2)
    restoresavedvalues(currentvalues)

  elif function == "Self Destruct":
    print("Initiating self destruct. Hold button to cancel.")
    currentvalues = savecurrentvalues()
    for i in [(1,1),(1,0.5),(2,0.25),(3,0.125),(6,0.06),(12,0.03)]:
      cycle(i[0],i[1])
      if button.is_pressed: break
    if button.is_pressed:
      print("\tSelf destruct cancelled")
      for i in range(9,-1,-1):
        relays[i].blink(0.1,0,1,False)
    else:
      print("\tSelf destructing")
      explode(15)
    restoresavedvalues(currentvalues)

  elif function == "Submarine Mode":
    if relays[i].is_lit:
      print("Exiting submarine mode.")
      relays[i].off()
    else:
      currentvalues = savecurrentvalues()
      print("Activating sonar.")
      currentvalues = savecurrentvalues()
      alloff()
      knightrider(button)
      restoresavedvalues(currentvalues)
      print("Entering submarine mode.")
      relays[i].on()

  elif function == "Warp Speed":
    if relays[4].is_lit:
      print("Exiting warp speed, beware floating bits of Alderaan.")
      relays[4].off()
    else:
      print("Entering warp speed, buckle up buttercup!")
      currentvalues = savecurrentvalues()
      alloff()
      for x in range(5):
        a = [i for i in range(0,10)]
        shuffle(a)
        for i in a:
          relays[i].on()
          speed = 1/(x*10+i+2)
          sleep(speed)
          relays[i].off()
      restoresavedvalues(currentvalues)
      relays[4].on()

  elif function in ["Crawler Mode", "Pirate Mode", "Invisibility Mode", "Mall Crawl"]:
    print(f"{'Dis' if relays[i].is_lit else 'En'}abling {function}")
    relays[i].toggle()

pins = [
  "GPIO9", #T1
  "GPIO7", #T2
  "GPIO6", #T3
  "GPIO5", #T4
  "GPIO4", #T5
  "GPIO13", #B5
  "GPIO12", #B4
  "GPIO11", #B3
  "GPIO10", #B2
  "GPIO8", #B1
]

relays = [
  LED(16,active_high=False), #T1
  LED(17,active_high=False), #T2
  LED(22,active_high=False), #T3
  LED(23,active_high=False), #T4
  LED(26,active_high=False), #T5
  LED(27,active_high=False), #B5
  LED(24,active_high=False), #B4
  LED(19,active_high=False), #B3
  LED(18,active_high=False), #B2
  LED(15,active_high=False), #B1
]

names = [
  "Nuke", #T1
  "Eject", #T2
  "Oil Slick", #T3
  "Crawler Mode", #T4
  "Warp Speed", #T5
  "Submarine Mode", #B5
  "Mall Crawl", #B4
  "Self Destruct", #B3
  "Invisibility Mode", #B2
  "Pirate Mode", #B1
]

def initiateButtons():
  global buttons
  buttons = [
    Button(9), #T1
    Button(7), #T2
    Button(6), #T3
    Button(5), #T4
    Button(4), #T5
    Button(13), #B5
    Button(12), #B4
    Button(11), #B3
    Button(10), #B2
    Button(8), #B1
  ]
  for button in buttons:
    button.when_pressed = buttonpress
  buttons[9].when_held = showcharge
  buttons[4].when_held = starfield
  #buttons[6].when_held = resetbuttons
  alloff()
  for i in range(1): cycle()
  print("Ready.")

initiateButtons()

def resetbuttons():
  global buttons
  for i in buttons:
    i = None
  initiateButtons()

if __name__ == "__main__": pause()

