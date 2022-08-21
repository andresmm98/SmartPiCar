import cv2
import numpy as np
import logging
import math
from pycoral.utils import edgetpu
from pycoral.adapters import common

# previous model: /home/pi/DeepPiCar/models/autonomous_car_model.tflite
class LaneFollower(object):

    def __init__(self,
                 car=None,
                 model_path='/home/pi/Smart-Pi-Car/models/lane-navigation-model-finetuned.tflite'):
        logging.info('Poniendo a punto el procesador')

        self.car = car
        self.curr_steering_angle = 90
        
        # Initialize the TF interpreter
        self.interpreter = edgetpu.make_interpreter(model_path)
        self.interpreter.allocate_tensors()

    def follow_lane(self, frame):
        # Main entry point of the lane follower

        new_steering_angle = self.compute_steering_angle(frame)
        self.curr_steering_angle = self.stabilize_steering_angle(new_steering_angle)
        logging.debug(f"Ángulo de giro: {self.curr_steering_angle - 90} grados")

        if self.car is not None:
            self.car.front_wheels.turn(self.curr_steering_angle)
        final_frame = display_heading_line(frame, self.curr_steering_angle)

        return final_frame

    def stabilize_steering_angle(self, new_steering_angle):
        # set max deviation from last angle to 3 degrees
        stabilized_steering_angle = new_steering_angle
        max_angle_deviation = 3
        angle_deviation = new_steering_angle - self.curr_steering_angle
        if angle_deviation > max_angle_deviation:
            stabilized_steering_angle = self.curr_steering_angle + max_angle_deviation
        elif angle_deviation < -max_angle_deviation:
            stabilized_steering_angle = self.curr_steering_angle - max_angle_deviation
        return stabilized_steering_angle
            
    def compute_steering_angle(self, frame):        
        input_frame = img_preprocess(frame)
        common.set_input(self.interpreter, input_frame)

        output_details = self.interpreter.get_output_details()[0]
        self.interpreter.invoke()
        steering_angle = self.interpreter.get_tensor(output_details['index'])

        steering_angle = int(steering_angle + 0.5) # redondeo
        return steering_angle

def img_preprocess(image):
    # cut top of image
    height = len(image)
    image = image[int(height/2):,:,:]

    # resize
    image = cv2.resize(image, (200,66))

    # change to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # normalize
    image = image / 255
    return image

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # figure out the heading line from steering angle
    # heading line (x1,y1) is always center bottom of the screen
    # (x2, y2) requires a bit of trigonometry

    # Note: the steering angle of:
    # 0-89 degree: turn left
    # 90 degree: going straight
    # 91-180 degree: turn right 
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
