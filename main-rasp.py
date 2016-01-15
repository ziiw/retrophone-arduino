#!/usr/bin/python

'''
by Philippe Tring
This program reads data coming from the serial port from a arduino.
Add your twitter credential to use it
DATA FORMAT TO RECEIVE:
number received from the arduino:
    '0\r\n': 1,
    '9\r\n': 0,
    '8\r\n': 9,
    '7\r\n': 8,
    '6\r\n': 7,
    '5\r\n': 6,
    '4\r\n': 5,
    '3\r\n': 4,
    '2\r\n': 3,
    '1\r\n': 2
It assumes that the Arduino shows up in /dev/ttyACM0 on the Raspberry Pi which should happen if you're using Debian.
'''

import serial
import datetime
import twitter
import sched
import time

phone_state = 'unknown'
ring_time = datetime.datetime.today()
hour_first = 0
hour_second = 0
minute_first = 0
minute_second = 0
number_received_count = 0
ring_event = 0
tweet_event = 0
scheduler = sched.scheduler(time.time, time.sleep)
#To find out the port name: ls /dev/tty*
ser = serial.Serial('/dev/ttyACM0', 9600)
#To get the correct number from phone
phone_number_dict = {
    '0\r\n': 1,
    '9\r\n': 0,
    '8\r\n': 9,
    '7\r\n': 8,
    '6\r\n': 7,
    '5\r\n': 6,
    '4\r\n': 5,
    '3\r\n': 4,
    '2\r\n': 3,
    '1\r\n': 2
}

def set_number_received(new_value):
    global number_received_count
    global hour_first
    global hour_second
    global minute_first
    global minute_second
    if number_received_count == 0:
        hour_first = new_value
    elif number_received_count == 1:
        hour_second = new_value
    elif number_received_count == 2:
        minute_first = new_value
    elif number_received_count == 3:
        minute_second = new_value
    number_received_count = number_received_count + 1

def set_status(status):
    global phone_state
    global ring_time
    global number_received_count
    global ring_event
    global scheduler
    global tweet_event
    if status == 'pick_up\r\n':# change with ser.readline() received string when phone is pickup
        if phone_state == 'ringing':
            ser.write('stop_ringing')
            #scheduler.cancel(tweet_event)
            #tweet_event = 0
        phone_state = 'pick_up'
    elif status == 'pick_down\r\n':# when phone is hang up
        if phone_state == 'ringing':
            ser.write('stop_ringing')
            #scheduler.cancel(tweet_event)
            #tweet_event = 0
        elif number_received_count > 2:
            new_hour = `hour_first` + `hour_second`
            new_minute = `minute_first` + `minute_second`
            ring_time = ring_time.replace(hour=int(new_hour), minute=int(new_minute), second=0, microsecond=0)
            number_received_count = 0
            now = datetime.datetime.now()
            delay = (ring_time - now).total_seconds()
            if ring_event != 0:
                scheduler.cancel(ring_event)
            ring_event = scheduler.enter(delay, 1, ring_phone, ())
            scheduler.run()
        phone_state = 'pick_down'
    elif status == 'tweet\r\n':
        tweet()
    elif phone_state == 'pick_up':
        set_number_received(phone_number_dict[status])

def ring_phone():
    global phone_state
    global tweet_event
    global ring_event
    global scheduler
    print('RING TIME')
    ser.write('10')
    ring_event = 0
    #tweet_event = scheduler.enter(20, 1, tweet, ())
    #scheduler.run()
    phone_state = 'ringing'

def tweet():
    CON_SEC_KEY = '5MbXEE0x8bN2FmZGKbdjtxZQhNjXsdTaCaj0a68'
    CON_SEC = 'FnNF0Sgrk95Gjyyy26J'
    TOKEN = '502145429-UHqbcA8L9s4jw3y35kBUYdg4k18Zb'
    TOKEN_KEY = 'M1mzRMPx9zq1GrzSMm6D0S2E'
    my_auth = twitter.OAuth(TOKEN,TOKEN_KEY,CON_SEC,CON_SEC_KEY)
    twit = twitter.Twitter(auth=my_auth)
    twit.statuses.update(status="Je serais certainement en retard ce matin. Signe mon reveil https://www.youtube.com/watch?v=pIgZ7gMze7A")

while 1 :
    arduino_message = ser.readline()
    print('arduino_message: ' + arduino_message)
    set_status(arduino_message)
    print(phone_state)

#tweet()
#ser.write('10')
