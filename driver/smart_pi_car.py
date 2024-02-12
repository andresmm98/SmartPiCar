"""
This program is responsible for driving the car as the user wants to.

The car can be driven manually with the keyboard & autonomously,
both using a trained deep learning model or a hand-coded program.
While driving, the program stores the frames coming from the camera
as labelled images for training the neural network.
"""

import logging
import sys
import os
import time
import datetime
import cv2

import picar
from autonomous_driver import LaneFollower
from hand_coded_lane_follower import HandCodedLaneFollower


class SmartPiCar:

    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240
    STRAIGHT_ANGLE = 90
    default_speed = 20  # speed range is 0 - 100

    def __init__(self):
        """initialize camera and wheels."""
        logging.info("Creating a Smart Pi Car...")

        picar.setup()

        logging.debug("Setting up the camera...")
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3, self.CAMERA_WIDTH)
        self.camera.set(4, self.CAMERA_HEIGHT)

        self.horizontal_servo = picar.Servo.Servo(1)
        self.horizontal_servo.offset = 20  # calibrates servum to the center
        self.horizontal_servo.write(self.STRAIGHT_ANGLE)

        self.vertical_servo = picar.Servo.Servo(2)
        self.vertical_servo.offset = 0
        self.vertical_servo.write(self.STRAIGHT_ANGLE)
        logging.debug("Camera is ready.")

        logging.debug("Setting up the wheels...")
        self.back_wheels = picar.back_wheels.Back_Wheels()
        self.back_wheels.speed = self.default_speed

        self.steering_angle = self.STRAIGHT_ANGLE
        self.front_wheels = picar.front_wheels.Front_Wheels()
        self.front_wheels.turning_offset = -10
        self.front_wheels.turn(self.steering_angle)  # from 45 to 135
        logging.debug("Wheels ready.")

        self.short_date_str = datetime.datetime.now().strftime("%d%H%M")

        # Record a video

        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.date_str = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        self.video = cv2.VideoWriter(
            f"../footage/car-video-{self.date_str}.avi",
            self.fourcc,
            20.0,
            (self.CAMERA_WIDTH, self.CAMERA_HEIGHT),
        )

        logging.info("Smart Pi Car created successfully.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback is not None:
            logging.error("Stopping execution with error %s", traceback)
        self.cleanup()

    def cleanup(self):
        """Restore the hardware."""
        logging.info("Stopping the car, restoring the hardware...")
        self.back_wheels.speed = 0
        self.front_wheels.turn(self.STRAIGHT_ANGLE)
        self.camera.release()
        self.video.release()
        cv2.destroyAllWindows()
        logging.info("Car has stopped.")
        sys.exit()

    def manual_driver(self):
        """Drive with keyboard keys A (left) and D (right)."""
        pressed_key = cv2.waitKey(50) & 0xFF
        if pressed_key == ord("a"):
            if self.steering_angle > 40:
                self.steering_angle -= 3
            self.front_wheels.turn(self.steering_angle)
        elif pressed_key == ord("d"):
            if self.steering_angle < 140:
                self.steering_angle += 3
            self.front_wheels.turn(self.steering_angle)
        elif pressed_key & 0xFF == ord("p"):
            self.back_wheels.speed = 0  # stops
        elif pressed_key & 0xFF == ord("g"):
            self.back_wheels.speed = self.default_speed  # starts moving
        elif pressed_key == ord("q"):
            self.cleanup()

    def drive(self, mode, speed=default_speed):
        """Drive the car using the desired mode.

        The autonomous driving mode uses a trained deep learning model.
        The manual driving mode & the handocded one store labelled
        driving frames for training the model.
        """
        self.back_wheels.speed = speed
        lane_follower = None
        i = 0
        if mode == "auto":

            lane_follower = LaneFollower(self)
            logging.info("Initiating autonomous driving...")
            logging.info("Starting at a speed of %i...", speed)

            while self.camera.isOpened():
                _, frame = self.camera.read()

                img_lane = lane_follower.follow_lane(frame)
                # self.video.write(img_lane)

                cv2.imshow("Video", img_lane)

                i += 1

                key = cv2.waitKey(1)
                if key & 0xFF == ord("q"):
                    self.cleanup()
                    break
                if key & 0xFF == ord("p"):
                    self.back_wheels.speed = 0
                elif key & 0xFF == ord("g"):
                    self.back_wheels.speed = speed
        elif mode == "manual":

            logging.info("Starting manual driving...")
            logging.info("Driving at a speed of %i...", speed)
            os.chdir("../footage")

            while self.camera.isOpened():
                _, frame = self.camera.read()
                cv2.imshow("Video", frame)

                self.manual_driver()

                cv2.imwrite(
                    f"v{self.short_date_str} \
                            -f{i}-a{self.steering_angle}.png",
                    frame,
                )

                i += 1
                time.sleep(0.2)
        elif mode == "handcoded":

            lane_follower = HandCodedLaneFollower(self)
            logging.info("Starting autonomous driving...")
            logging.info("Driving at a speed of %i...", speed)

            while self.camera.isOpened():
                # Get, write and show current frame

                _, frame = self.camera.read()
                self.video.write(frame)

                image_lane = lane_follower.follow_lane(frame)

                cv2.imshow("Video", image_lane)

                key = cv2.waitKey(1)
                if key & 0xFF == ord("q"):
                    self.cleanup()
                    break
                if key & 0xFF == ord("p"):
                    self.back_wheels.speed = 0
                elif key & 0xFF == ord("g"):
                    self.back_wheels.speed = speed
                i += 1
        else:
            self.back_wheels.speed = speed

            logging.info("Starting manual driving...")
            logging.info("Driving at a speed of %i..., speed")

            while self.camera.isOpened():
                # Get, write and show current frame

                _, frame = self.camera.read()
                self.video.write(frame)
                cv2.imshow("Video", frame)

                self.manual_driver()

                i += 1


def main(mode="auto"):
    "Create a car and drive it, faster if the driving is autonomous."
    with SmartPiCar() as car:
        if mode == "auto":
            car.drive(mode, 40)
        else:
            car.drive(mode, 20)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(levelname)s: %(asctime)s: %(message)s"
    )

    if len(sys.argv) > 1:
        if sys.argv[1] not in ["auto", "manual", "handcoded"]:
            logging.error(
                "Please, write down the desired driving mode after the name of the program.\n"
                '- "manual": drive using the keyboard keys "a" (left) & "d" (right)\n'
                '- "auto": autonomous driving using artificial intelligence\n'
                '- "handcoded": autonomous driving without artificial intelligence'
            )
            sys.exit()
        else:
            main(sys.argv[1])
    else:
        main()
