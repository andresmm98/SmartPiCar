import logging
import picar
import cv2
import datetime
import sys
import os
import time
from autonomous_driver import LaneFollower

mode = 'auto'

class SmartPiCar(object):

    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240
    STRAIGHT_ANGLE = 90

    def __init__(self):
        """ Intitialize car and camera """
        logging.info("Creating a Smart Pi Car...")

        picar.setup()

        logging.debug("Setting up camera")
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3, self.CAMERA_WIDTH)
        self.camera.set(4, self.CAMERA_HEIGHT)

        self.horizontal_servo = picar.Servo.Servo(1)
        self.horizontal_servo.offset = 20  # calibrate servo to center
        self.horizontal_servo.write(self.STRAIGHT_ANGLE)

        self.vertical_servo = picar.Servo.Servo(2)
        self.vertical_servo.offset = 0  # calibrate servo to center
        self.vertical_servo.write(self.STRAIGHT_ANGLE)

        logging.debug("Setting up wheels")
        self.back_wheels = picar.back_wheels.Back_Wheels()
        self.back_wheels.speed = 0  # Speed Range is 0 (stop) - 100 (fastest)

        self.steering_angle = self.STRAIGHT_ANGLE
        self.front_wheels = picar.front_wheels.Front_Wheels()
        self.front_wheels.turning_offset = -10  # calibrate servo to center
        self.front_wheels.turn(self.steering_angle)  # Steering Range is 45 (left) - 90 (center) - 135 (right)

        self.short_date_str = datetime.datetime.now().strftime("%d%H%M")
        self.lane_follower = LaneFollower(self)
        
        ''' # Record video
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.date_str = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        self.video = cv2.VideoWriter('../footage/car-video-%s.avi' % self.date_str,
                                     self.fourcc,
                                     20.0,
                                     (self.camera_width, self.camera_height))'''
        
        logging.info("Smart Pi Car created")

    def __enter__(self):
        """ Entering a with statement """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Exiting a with statement """
        if traceback is not None:
            logging.error(f"Stopping with exception {traceback}")

        self.cleanup()

    def cleanup(self):
        """ Reset the hardware """
        logging.info("Stopping the car, resetting the hardware")
        self.back_wheels.speed = 0
        self.front_wheels.turn(self.STRAIGHT_ANGLE)
        self.camera.release()
        #self.video.release()
        cv2.destroyAllWindows()
        sys.exit()

    def manual_driver(self):
        """ Drive using A and D keys """
        pressed_key = cv2.waitKey(50) & 0xFF
        if pressed_key == ord('a'):
            if self.steering_angle > 50: self.steering_angle -= 3
            self.front_wheels.turn(self.steering_angle)
        elif pressed_key == ord('d'):
            if self.steering_angle < 130: self.steering_angle += 3
            self.front_wheels.turn(self.steering_angle)
        elif pressed_key == ord('q'):
            self.cleanup()

    def drive(self, mode):
        """ Start driving """
        i=0
        if mode == "auto":
            self.back_wheels.speed = 40

            logging.info("Initiating autonomous driving...")
            logging.info(f"Starting to drive at speed {speed}...")
            
            while self.camera.isOpened():
                _, frame = self.camera.read()
                
                img_lane = self.lane_follower.follow_lane(frame)
                # self.video.write(img_lane)
                cv2.imshow('Video', img_lane)

                i += 1
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.cleanup()
                    break
        elif mode == "training": 
            self.back_wheels.speed = 20

            logging.info("Initiating manual driving...")
            logging.info(f"Starting to drive at speed {speed}...")
            os.chdir('../footage')

            while self.camera.isOpened():
                # Get, write and show current frame
                _, frame = self.camera.read()
                # self.video.write(frame)
                cv2.imshow('Video',frame)

                self.manual_driver()

                # Save frame and steering angle
                cv2.imwrite('v%s-f%03d-a%03d.png' % (self.short_date_str, i, self.steering_angle), frame)
                
                i += 1
                time.sleep(0.2)

        else:
            self.back_wheels.speed = 20

            logging.info("Initiating manual driving...")
            logging.info(f"Starting to drive at speed {speed}...")

            while self.camera.isOpened():
                # Get, write and show current frame
                _, frame = self.camera.read()
                # self.video.write(frame)
                cv2.imshow('Video',frame)

                self.manual_driver()
                
                i += 1

def main(mode):
    with SmartPiCar() as car:
        car.drive(mode)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(asctime)s: %(message)s')

    if len(sys.argv) > 1:
        if sys.argv[1] not in ['manual', 'training','auto']:
            logging.error('Please, write the driving mode after the name of the program:\n - "auto" for autonomous driving\n - "manual" for manual driving\n - "training" for collecting data with manual driving')
            sys.exit()
        else: main(sys.argv[1])

    main("auto")