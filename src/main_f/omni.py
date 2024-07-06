from machine import Pin,PWM
from time import sleep
from .hcsr04 import HCSR04
from .TB6612FNG import Motor
import math
import time
from math import cos, sin, pi
import random

WheelRadius = 0.053
robot_radius = 0.12
dt = 0.1

def calculate_wheel_velocities(speed, rotation, orientation):
    alpha = [0, 2 * math.pi / 3, -2 * math.pi / 3]  
    Vx = speed * cos(orientation)
    Vy = speed * sin(orientation)
    omega = rotation / WheelRadius
    
    V_wheels = []
    for a in alpha:
        V_wheel = -Vx * cos(a) + Vy * sin(a) + omega * WheelRadius
        V_wheels.append(V_wheel)
    
    return V_wheels

def calc_h(distance_front, distance_back):
    c = math.sqrt(distance_front**2 + distance_back**2)
    h = distance_front * distance_back / c
    return h

class OmniSeeker():
    def __init__(self):
        # FLAGS ACTIVADOS SIEMPRE QUE HAYA DISTANCIA MINIMA DE 20 CM
        self.followingWall = False
        self.flagSideBack = False # Activar solo si esta a menos de 20 cm
        self.flagSideLeft = False # Activar solo si esta a menos de 20 cm
        self.flagSideRight = False
        self.movement = 0 #1:right, -1:left, 2:forward
        self.distance = float('inf')
        self.dist_diff = -1
        self.generated_movement = False
        self.vel1 = 0
        self.vel2 = 0
        self.vel3 = 0
        self.Ypos = 0
        self.Xpos = 0
        self.theta = pi/2
        
    def addMotors(self, STBY_1, AIN1_1, AIN2_1, PWMA_1, BIN1_1, BIN2_1, PWMB_1, STBY_2, AIN1_2, AIN2_2, PWMA_2, freq):
        self.motor1 = Motor(STBY_1, AIN1_1, AIN2_1, PWMA_1, freq)
        self.motor2 = Motor(STBY_1, BIN1_1, BIN2_1, PWMB_1, freq)
        self.motor3 = Motor(STBY_2, AIN1_2, AIN2_2, PWMA_2, freq)
        
    def addSensors(self, trigger_1, echo_1, trigger_2, echo_2, trigger_3, echo_3):
        self.sensorBack = HCSR04(trigger_1, echo_1)
        self.sensor2 = HCSR04(trigger_2, echo_2)
        self.sensor3 = HCSR04(trigger_3, echo_3)
    
    def moveRobot(self, speed, rotation, orientation): # MOVE FORMWARD, MOVE BACKWARD, ROTATE LEFT, ROTATE RIGHT, MOVE LEFT, MOVE RIGHT
        wheel_velocities = calculate_wheel_velocities(speed, rotation, orientation)
        
        self.vel1 = wheel_velocities[1]
        self.vel2 = wheel_velocities[2]
        self.vel3 = wheel_velocities[0]
        
        if self.vel1 < 0:
            dir1_0 = 1
            dir1_1 = 0
        else:
            dir1_0 = 0
            dir1_1 = 1
            
        if self.vel2 < 0:
            dir2_0 = 1
            dir2_1 = 0
        else:
            dir2_0 = 0
            dir2_1 = 1
            
        if self.vel3 < 0:
            dir3_0 = 0
            dir3_1 = 1
        else:
            dir3_0 = 1
            dir3_1 = 0
        
        self.motor1.move_motor(dir1_0, dir1_1, abs(self.vel1), 1)
        self.motor2.move_motor(dir2_0, dir2_1, abs(self.vel2), 1)
        self.motor3.move_motor(dir3_0, dir3_1, abs(self.vel3), 1)
        
    def correctTheta(self):
        if self.theta < 3*pi/4 and self.theta > pi/4:
            self.theta = pi/2
        elif self.theta > 3*pi/4 and self.theta < 5*pi/4:
            self.theta = pi
        elif self.theta > 5*pi/4 and self.theta < 7*pi/4:
            self.theta = 3*pi/2
        else:
            self.theta = 0
            
    def stop(self):
        self.moveRobot(0, 0, 0)

    def getDistance(self, sensor):
        distance = sensor.distance_cm()
        if distance is not None:
            return round(distance, 1)
        else:
            return 9999
        
    def sweeping(self):
        print('Sweeping')
        min_distance = float('inf')
        start_time = time.time()
        
        while time.time() - start_time < 1:
            distance = self.getDistance(self.sensorBack)
            if distance < 50:
                min_distance = min(min_distance, distance)
            self.moveRobot(0, -(12.5/distance) * self.movement, 0)
            
        start_time = time.time()
        while time.time() - start_time < 2:
            distance = self.getDistance(self.sensorBack)
            if distance < 50:
                min_distance = min(min_distance, distance)
            self.moveRobot(0, (12.5/distance) * self.movement, 0)
        
        if min_distance < 50:
            distance = self.getDistance(self.sensorBack)
            while abs(distance - min_distance) > 0.1:
                distance = self.getDistance(self.sensorBack)
                self.moveRobot(0, -(12.5/distance) * self.movement, 0)
            
            while int(distance) > 20:
                self.moveRobot(1, 0, math.pi / 2)
                distance = self.getDistance(self.sensorBack)
            self.followingWall = True
            print('FollowingWalls')
        else:
            self.moveRobot(0, -(12.5/distance) * self.movement, 0)
            time.sleep(1)
        self.stop()
        
    def get_dist_diff(self):
        distance = self.getDistance(self.sensorBack)
        diff_dist = self.distance - distance
        return distance, diff_dist
    
    def correct_position(self):
        distance = self.getDistance(self.sensorBack)
        diff_dist = self.distance - distance
        self.distance = distance
        dist_diff_th = self.dist_diff - 3 < diff_dist < self.dist_diff + 3

        if distance < 15 and dist_diff_th:
            print('Correcting position')
            while distance < 20:
                distance = self.getDistance(self.sensorBack)
                self.moveRobot(1, 0, 3 * math.pi / 2)
            self.stop()
            time.sleep(0.1)
            self.moveRobot(0, -0.1 * self.movement, 0)
            time.sleep(0.5)
        elif distance > 30 and dist_diff_th:
            time.sleep(1)
            print('Correcting position')
            distance = self.getDistance(self.sensorBack)
            if distance > 50:
                print('Not following wall')
                self.followingWall = False
                return
            while distance > 20:
                distance = self.getDistance(self.sensorBack)
                self.moveRobot(1, 0, math.pi / 2)
            self.stop()
            time.sleep(0.1)
            self.moveRobot(0, 0.1 * self.movement, 0)
            time.sleep(0.5)
        self.distance = distance
        self.dist_diff = diff_dist
        
    def setFlags(self):
        self.flagSideRight = self.getDistance(self.sensorRight) < 20
        self.flagSideLeft = self.getDistance(self.sensorLeft) < 20
        if self.movement != 2:
            self.flagSideBack = self.getDistance(self.sensorBack) < 50

    def moveToTurn(self):
        while self.getDistance(self.sensorBack) < 20:
            self.moveRobot(1, 0, 3 * math.pi / 2)
        self.stop()
        while self.getDistance(self.sensorRight) < 20 or self.getDistance(self.sensorLeft) < 20:
            self.moveRobot(1, 0, math.pi / 2 - self.movement * math.pi / 2)
        self.stop()
        
    # def update_odometry(self, t):
    #     result = self.calculate_odometry(self.vel1, self.vel2, self.vel3)
        
    #     self.theta += result[2] * t / dt
        
    #     if self.theta >= 2 * math.pi:
    #         self.theta -= 2 * math.pi
    #     elif self.theta <= 0:
    #         self.theta += 2 * math.pi
            
    #     if 3 * math.pi / 4 > self.theta > math.pi / 4:
    #         self.Xpos -= result[1] * t * 2.25
    #         self.Ypos += result[0] * t * 2.25
    #     elif 5 * math.pi / 4 > self.theta > 3 * math.pi / 4:
    #         self.Xpos -= result[0] * t * 2.25
    #         self.Ypos -= result[1] * t * 2.25
    #     elif self.theta < math.pi / 4 or self.theta > 7 * math.pi / 4:
    #         self.Xpos += result[0] * t * 2.25
    #         self.Ypos += result[1] * t * 2.25
    #     elif 7 * math.pi / 4 > self.theta > 5 * math.pi / 4:
    #         self.Xpos += result[1] * t * 2.25
    #         self.Ypos -= result[0] * t * 2.25
        
    #     sim.simxSetObjectPosition(self.clientID, self.odometry, -1, [self.Xpos, self.Ypos, 0], sim.simx_opmode_oneshot)
    #     sim.simxSetObjectOrientation(self.clientID, self.odometry, -1, [0, 0, self.theta], sim.simx_opmode_oneshot)
        
    #     time.sleep(dt)
    
    # def calculate_odometry(self, w1, w2, w3):
    #     V1 = w1 * WheelRadius
    #     V2 = w2 * WheelRadius
    #     V3 = w3 * WheelRadius
        
    #     Vx = V3 - V2 * math.sin(math.radians(30)) - V1 * math.sin(math.radians(30))
    #     Vy = V1 * math.cos(math.radians(30)) - V2 * math.cos(math.radians(30))
    #     w = (WheelRadius / (3 * robot_radius)) * (w1 + w2 + w3)
        
    #     return [Vx, Vy, w]
    
    def wallFollowing(self):
        while True:
            if not self.followingWall:
                self.generated_movement = False
                self.movement = 2
                self.moveRobot(1, 0, math.pi / 2)  # Move forward
                distance = self.getDistance(self.sensorBack)
                if distance < 50:
                    self.stop()
                    self.sweeping()
                    self.correctTheta()
            else:
                if not self.generated_movement:
                    if self.getDistance(self.sensorLeft) < 75:
                        self.movement = -1
                    elif self.getDistance(self.sensorRight) < 75:
                        self.movement = 1
                    else:
                        self.movement = random.choice([1, -1])
                    self.generated_movement = True 
                
                self.setFlags()
                if not self.flagSideRight and not self.flagSideLeft:                   
                    self.moveRobot(1, 0, math.pi / 2 + self.movement * math.pi / 2)  # Move sideways
                    if not self.flagSideBack:
                        time.sleep(1)
                        self.followingWall = False
                    else:
                        self.correct_position()
                        self.setFlags()
                else:
                    self.stop()
                    self.moveToTurn()
                    self.moveRobot(0, -1 * self.movement, 0)
                    time.sleep(1)
                    self.sweeping()
                    self.correctTheta()
                    self.setFlags()