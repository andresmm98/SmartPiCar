import logging
import picar
import cv2
import datetime

class SmartPiCar(object):

    camera_width = 320
    camera_height = 240

    def __init__(self):
        """ Intitialize car and camera """
        logging.info("Creating a Smart Pi Car...")

        picar.setup()

        logging.debug("Setting up camera")
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3, self.camera_widht)
        self.camera.set(4, self.camera_height)

        self.horizontal_servo = picar.Servo.Servo(1)
        self.pan_servo.offset = -30  # calibrate servo to center
        self.pan_servo.write(80)

        self.vertical_servo = picar.Servo.Servo(2)
        self.tilt_servo.offset = 20  # calibrate servo to center
        self.tilt_servo.write(90)

        logging.debug("Setting up wheels")
        self.back_wheels = picar.back_wheels.Back_Wheels()
        self.back_wheels.speed = 0  # Speed Range is 0 (stop) - 100 (fastest)

        self.steering_angle = 95
        self.front_wheels = picar.front_wheels.Front_Wheels()
        self.front_wheels.turning_offset = -25  # calibrate servo to center
        self.front_wheels.turn(steering_angle)  # Steering Range is 45 (left) - 90 (center) - 135 (right)

        # Record video
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        date_str = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        self.video = cv2.VideoWriter('../data/tmp/car_video%s.avi' % date_str,
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
        self.front_wheels.turn(95)
        self.camera.release()
        self.video.release()
        cv2.destroyAllWindows()

    def manual_drive(self):
        """ Drive using A and D keys """
        pressed_key = cv2.waitKey(50) & 0xFF
        if pressed_key == ord('a'):
            if self.steering_angle > 65: self.steering_angle -= 1
            self.front_wheels.turn(self.steering_angle)
        elif pressed_key == ord('d'):
            if self.steering_angle < 125: self.steering_angle += 1
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
            self.video_orig.write(frame)
            cv2.imshow('Video',frame)

            self.manual_drive()

            # Save frame and steering angle
            cv2.imwrite('%s_%03d_%03d.png' % (date_str, i, self.steering_angle), frame)
            
            i += 1

def main():
    with SmartPiCar() as car:
        car.Drive(40)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(asctime)s: %(message)s')

    main()