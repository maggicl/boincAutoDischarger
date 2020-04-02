#!/usr/bin/env python3
# vim: set ft=python:

import xml.etree.ElementTree as ET
import os
from enum import Enum
import time
import signal
import sys
from datetime import date as D

MIN_CPU=8
MAX_CPU=85

BOINC_XML="/Library/Application Support/BOINC Data/global_prefs_override.xml"
BOINC_PASS=os.popen("cat '/Library/Application Support/BOINC Data/gui_rpc_auth.cfg'").read()
BOINC_CMD="env boinccmd --host localhost --passwd '" + BOINC_PASS + "'"

def send_notification(message):
    os.system("terminal-notifier -title 'BOINC Auto discharger' -message '%s'" % (message))

class State(Enum):
    CHARGING = 1
    MUST_DISCHARGE = 2
    DISCHARGING = 3
    MUST_CHARGE = 4

    def next(self, percent, charging):
        state = None
        if (self is State.DISCHARGING and percent <= 20) or (self is State.CHARGING and not charging):
            state = State.MUST_CHARGE
        elif (self is State.CHARGING and percent >= 90) or (self is State.DISCHARGING and charging):
            state = State.MUST_DISCHARGE
        elif (self is State.MUST_CHARGE and charging):
            state = State.CHARGING
        elif (self is State.MUST_DISCHARGE and not charging):
            state = State.DISCHARGING
        else:
            return self

        state.action()
        return state

    def action(self):
        if self is State.MUST_CHARGE:
            set_params(cpu=MIN_CPU, time_range=TimeRange(12, 30, 21, 00))
            send_notification("Connect the charger! BOINC slowed down")
        elif self is State.MUST_DISCHARGE:
            send_notification("Disconnect the charger to speed up BOINC")
        elif self is State.DISCHARGING:
            set_params(cpu=MAX_CPU, time_range=TimeRange(00, 00, 24, 00))
        else:
            set_params(cpu=MIN_CPU, time_range=TimeRange(12, 30, 21, 00))

    def __str__(self):
        if self is State.DISCHARGING:
            return "Discharging, BOINC at full speed"
        elif self is State.CHARGING:
            return "Charging, BOINC at slow speed"
        elif self is State.MUST_CHARGE:
            return "Waiting for charger, BOINC at slow speed"
        else:
            return "Waiting for charger disconnect, BOINC at slow speed"


class TimeRange:
    def __init__(self, start_h, start_m, end_h, end_m):
        self.start_h = start_h
        self.start_m = start_m
        self.end_h = end_h
        self.end_m = end_m

    def valid(self):
        if self.start_h is None or self.end_h is None or self.start_m is None or self.end_m is None:
            return False
        if not (0 <= self.start_h < 24 and 0 < self.end_h <= 24 and 0 <= self.start_m < 60 \
                and 0 <= self.end_m < 60):
            return False
        return self.start_h * 60 + self.start_m < self.end_h * 60 + self.end_m

    def get_start(self):
        return self.start_h + self.start_m / 60

    def get_end(self):
        return self.end_h + self.end_m / 60


def set_param(tree, name, value):
    dom = tree.find(name)
    dom.text = "%2.6f" % (value)


def set_params(cpu=None, time_range=None, disable=True):
    tree = ET.parse(BOINC_XML)

    if cpu is not None and 0 < cpu <= 100:
        set_param(tree, 'cpu_usage_limit', cpu)

    if time_range is not None and time_range.valid():
        set_param(tree, 'start_hour', time_range.get_start())
        set_param(tree, 'end_hour', time_range.get_end())

    tree.write(BOINC_XML)
    os.system(BOINC_CMD + ' --read_global_prefs_override')

def charge_status():
    percent = int(os.popen("pmset -g batt | awk '/Internal/ {print $3}'").read()[:-3])
    charging = not os.system("pmset -g batt | grep discharging 2>&1 >/dev/null") == 0
    return (percent, charging)


def signal_handler(sig, frame):
    print('')
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    status = None
    percent, charging = charge_status()

    if charging:
        status = State.CHARGING
    else:
        status = State.DISCHARGING

    os.system('clear')
    status = status.next(percent, charging)
    status.action()

    while True:
        percent, charging = charge_status()
        count = int(os.popen("system_profiler SPPowerDataType | grep " +
              "'Cycle Count' | awk '{print $3}'").read())
        cycles_remaining = 1000 - count
        care_days = (D(2021, 6, 30) - D.today()).days

        stats = None
        if len(sys.argv) > 2 and sys.argv[2] == "stats":
            stats = os.popen('istats').read()

        os.system('clear')
        print("Battery: %d%% - %s\nCharge count: %d" % (percent, status, count))
        print("Remaining: %d days, %d cycles\nRate needed: %.5f cycles a day" %
              (care_days, cycles_remaining, cycles_remaining / care_days))

        if stats is not None:
            print('\n' + stats[:stats.rfind('\n\n')])

        status = status.next(percent, charging)
        time.sleep(10 if len(sys.argv) <= 1 or sys.argv[1] is None else
                int(sys.argv[1]))

if __name__ == "__main__":
    main()
