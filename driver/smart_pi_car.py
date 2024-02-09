#------------------------------------------------------------------------------
# El programa inicializa un coche SmartPiCar y lo conduce de la forma escogida por el usuario:
# - Manual: mediante el teclado
# - Auto: mediante el modelo de aprendizaje profundo
# - Entrenamiento manual: manual recopilando imágenes etiquetadas
# - Entrenamiento auto: mediante una programación explícita, guardando un video de la conducción
#------------------------------------------------------------------------------

import logging
import picar
import cv2
import datetime
import sys
import os
import time
from autonomous_driver import LaneFollower
from hand_coded_lane_follower import HandCodedLaneFollower

mode = 'auto'

class SmartPiCar(object):

    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240
    STRAIGHT_ANGLE = 90

    def __init__(self):

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
        self.vertical_servo.offset = 0  # calibrates servum to the center
        self.vertical_servo.write(self.STRAIGHT_ANGLE)
        logging.debug("Camera is ready.")

        logging.debug("Setting up the wheels...")
        self.back_wheels = picar.back_wheels.Back_Wheels()
        self.back_wheels.speed = 0  # speed range is 0 - 100

        self.steering_angle = self.STRAIGHT_ANGLE
        self.front_wheels = picar.front_wheels.Front_Wheels()
        self.front_wheels.turning_offset = -10  # calibrates servum to the center
        self.front_wheels.turn(self.steering_angle)  # Steering angle range is 45 (left) - 90 (straight) - 135 (right)
        logging.debug("Wheels ready.")

        self.short_date_str = datetime.datetime.now().strftime("%d%H%M")
        self.lane_follower = LaneFollower(self)
        self.hand_coded_lane_follower = HandCodedLaneFollower(self)
        
        # Records a video
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.date_str = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        self.video = cv2.VideoWriter('../footage/car-video-%s.avi' % self.date_str,
                                     self.fourcc,
                                     20.0,
                                     (self.camera_width, self.camera_height))
        
        logging.info("Smart Pi Car creado con éxito.")


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        if traceback is not None:
            logging.error(f"Parando la ejecución con el error {traceback}")

        self.cleanup()


    def cleanup(self):
        """ Resetea el hardware """
        logging.info("Parando el coche, restaurando el hardware...")
        self.back_wheels.speed = 0
        self.front_wheels.turn(self.STRAIGHT_ANGLE)
        self.camera.release()
        #self.video.release()
        cv2.destroyAllWindows()
        logging.info("Coche detenido.")
        sys.exit()


    def manual_driver(self):
        """ Conduce mediante las teclas A (derecha) y D (izquierda) """
        pressed_key = cv2.waitKey(50) & 0xFF
        if pressed_key == ord('a'):
            if self.steering_angle > 40: self.steering_angle -= 3
            self.front_wheels.turn(self.steering_angle)
        elif pressed_key == ord('d'):
            if self.steering_angle < 140: self.steering_angle += 3
            self.front_wheels.turn(self.steering_angle)
        elif key & 0xFF == ord('p'):
            self.back_wheels.speed = 0 # pausa
        elif key & 0xFF == ord('g'):
            self.back_wheels.speed = speed # go, arranca
        elif pressed_key == ord('q'):
            self.cleanup()


    def drive(self, mode, speed=0):
        """ Arranca el coche """
        self.back_wheels.speed = speed
        i = 0
        if mode == "auto":

            logging.info("Iniciando la conducción autónoma...")
            logging.info(f"Arrancando a una velocidad de {speed}...")
            
            while self.camera.isOpened():
                _, frame = self.camera.read()
                
                img_lane = self.lane_follower.follow_lane(frame)
                # self.video.write(img_lane)
                cv2.imshow('Video', img_lane)

                i += 1
                
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    self.cleanup()
                    break
                elif key & 0xFF == ord('p'):
                    self.back_wheels.speed = 0
                elif key & 0xFF == ord('g'):
                    self.back_wheels.speed = speed
        
        elif mode == "entrenamiento_manual": 

            logging.info("Iniciando la conducción manual...")
            logging.info(f"Arrancando a una velocidad de {speed}...")
            os.chdir('../footage')

            while self.camera.isOpened():
                _, frame = self.camera.read()
                cv2.imshow('Video',frame)

                self.manual_driver()

                cv2.imwrite('v%s-f%03d-a%03d.png' % (self.short_date_str, i, self.steering_angle), frame)
                
                i += 1 
                time.sleep(0.2)

        elif mode == "entrenamiento_auto":
            self.back_wheels.speed = 30

            logging.info("Iniciando la conducción autónoma...")
            logging.info(f"Arrancando a una velocidad de {speed}...")

            while self.camera.isOpened():
                # Get, write and show current frame
                _, frame = self.camera.read()
                self.video.write(frame)

                image_lane = self.hand_coded_lane_follower.follow_lane(frame)

                cv2.imshow('Video',image_lane)
                
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    self.cleanup()
                    break
                elif key & 0xFF == ord('p'):
                    self.back_wheels.speed = 0
                elif key & 0xFF == ord('g'):
                    self.back_wheels.speed = speed

                i += 1
            
        else:
            self.back_wheels.speed = 20

            logging.info("Iniciando la conducción manual...")
            logging.info(f"Arrancando a una velocidad de {speed}...")

            while self.camera.isOpened():
                # Get, write and show current frame
                _, frame = self.camera.read()
                # self.video.write(frame)
                cv2.imshow('Video',frame)

                self.manual_driver()
                
                i += 1


def main(mode):
    with SmartPiCar() as car:
        if mode == "auto":
            car.drive(mode,40)
        else:
            car.drive(mode,20)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(asctime)s: %(message)s')

    if len(sys.argv) > 1:
        if sys.argv[1] not in ['manual', 'training','auto', 'hand_coded']:
            logging.error('Por favor, escriba el modo de conducción deseado después del nombre del programa.\n \
- "manual": conducción mediante el teclado\n \
- "auto": conducción autónoma mediante inteligencia artificial\n \
- "entrenamiento_manual": conducción mediante el teclado recopilando datos\n \
- "entrenamiento_auto": conducción autónoma (sin inteligencia artificial) recopilando datos')
            sys.exit()
        else: main(sys.argv[1])

    else: main("auto")