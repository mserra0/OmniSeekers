"""
Microphyton for ESP32 for Sparkfun TB6612FNG Motor Drive for two motors
by Atila ELMAS, atila.alpagut@gmail.com
the following functions implemented forward, backward, right, left,
brake, stor, standby

please note that only some Pin available for PWM and OUT for DOIT ESP32 dev.R1 36 pins
PWM pins : 0, 2, 4, 5, 10, 12, 13, 22
OUT pins : 0, 2, 4, 5, 10, 12, 13-19, 21-27,32,33


"""
from machine import Pin,PWM
from time import sleep

class Motor():
    def __init__(self, STBY, IN1, IN2, PWM_, frequency):
        self.in2 = Pin(IN2, Pin.OUT)
        self.in1 = Pin(IN1, Pin.OUT)
        self.stby = Pin(STBY, Pin.OUT)
        self.pwm = PWM(Pin(PWM_), freq=frequency)
        self.stby.value(1)
        
    def move_motor(self, in1_val, in2_val, duty_cycle_percentage, duration):
        self.in1.value(in1_val)
        self.in2.value(in2_val)
        if duty_cycle_percentage > 1:
            duty_cycle_percentage = 1
        duty_cycle = duty_cycle_percentage * 1023
        self.pwm.duty(int(duty_cycle))
        #sleep(duration)