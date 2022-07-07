import logging
import picar
import cv2
import datetime
import sys

class SmartPiCar(object):

    camera_width = 320
    camera_height = 240
    straight_angle = 90

    def __init__(self):
        """ Intitialize car and camera """
        logging.info("Creating a Smart Pi Car...")

        picar.setup()

        logging.debug("Setting up camera")
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3, self.camera_width)
        self.camera.set(4, self.camera_height)

        self.horizontal_servo = picar.Servo.Servo(1)
        self.horizontal_servo.offset = -50  # calibrate servo to center
        self.horizontal_servo.write(self.straight_angle)

        self.vertical_servo = picar.Servo.Servo(2)
        self.vertical_servo.offset = 20  # calibrate servo to center
        self.vertical_servo.write(self.straight_angle)

        logging.debug("Setting up wheels")
        self.back_wheels = picar.back_wheels.Back_Wheels()
        self.back_wheels.speed = 0  # Speed Range is 0 (stop) - 100 (fastest)

        self.steering_angle = self.straight_angle
        self.front_wheels = picar.front_wheels.Front_Wheels()
        self.front_wheels.turning_offset = -10  # calibrate servo to center
        self.front_wheels.turn(self.steering_angle)  # Steering Range is 45 (left) - 90 (center) - 135 (right)

        # Record video
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.date_str = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        self.video = cv2.VideoWriter('../footage/driving-videos/car_video%s.avi' % self.date_str,
                                     self.fourcc,
                                     20.0,
                                     (self.camera_width, self.camera_height))
        
        logging.info("Smart Pi Car created")

    def __enter__(self):
        """ Entering a with statement """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Exiting a with statement """
        if traceback is not None:
            logging.error("Stopping with exception %s" % traceback)

        self.cleanup()

    def cleanup(self):
        """ Reset the hardware """
        logging.info("Stopping the car, resetting the hardware")
        self.back_wheels.speed = 0
        self.front_wheels.turn(self.straight_angle)
        self.camera.release()
        self.video.release()
        cv2.destroyAllWindows()
        sys.exit()

    def manual_driver(self):
        """ Drive using A and D keys """
        pressed_key = cv2.waitKey(50) & 0xFF
        if pressed_key == ord('a'):
            if self.steering_angle > 60: self.steering_angle -= 1
            self.front_wheels.turn(self.steering_angle)
        elif pressed_key == ord('d'):
            if self.steering_angle < 120: self.steering_angle += 1
            self.front_wheels.turn(self.steering_angle)
        elif pressed_key == ord('q'):
            self.cleanup()

    def drive(self, speed=0):
        """ Start driving """
        logging.info("Starting to drive at speed %s..." % speed)
        self.back_wheels.speed = speed
        i=0
        while self.camera.isOpened():
            # Get, write and show current frame
            _, frame = self.camera.read()
            self.video.write(frame)
            cv2.imshow('Video',frame)

            self.manual_driver()

            # Save frame and steering angle
            cv2.imwrite('%s_%03d%03d.png' % (self.date_str, i, self.steering_angle), frame)
            
            i += 1

def main():
    with SmartPiCar() as car:
        car.drive(40)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(asctime)s: %(message)s')

    main()