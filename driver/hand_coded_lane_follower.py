#------------------------------------------------------------------------------
# El programa crea una clase HandCodedLaneFollower,
# la cual conduce el coche mediante una programación explícita.
# 
# Esta consiste en identificar los colores de las líneas de la calzada, 
# encontrar las líneas presentes, unirlas en una para cada lado y calcular el ángulo promedio.
#------------------------------------------------------------------------------

import cv2
import numpy as np
import logging
import math
import datetime
import sys

_SHOW_IMAGE = False


class HandCodedLaneFollower(object):

    def __init__(self, car=None):
        logging.info('Iniciando el código de conducción')
        self.car = car
        self.curr_steering_angle = 90


    def follow_lane(self, frame):
        ''' Método principal de la clase, llama a los demás '''
        show_image("orig", frame)

        lane_lines, frame = detect_lane(frame)

        if len(lane_lines) == 0:
            logging.error('No se ha detectado ninguna línea de calzada, sigue recto.')
            return frame

        new_steering_angle = compute_steering_angle(frame, lane_lines)
        self.curr_steering_angle = stabilize_steering_angle(self.curr_steering_angle, new_steering_angle, len(lane_lines))

        if self.car is not None:
            self.car.front_wheels.turn(self.curr_steering_angle)
        curr_heading_image = display_heading_line(frame, self.curr_steering_angle)
        show_image("heading", curr_heading_image)

        return curr_heading_image

############################
# Funciones para calcular el ángulo de giro
############################
def detect_lane(frame):
    logging.debug('Detectando las líneas de calzada...')

    edges = edges(frame)
    show_image('edges', edges)

    cropped_edges = crop_top(edges, 1/3)
    show_image('edges cropped', cropped_edges)

    line_segments = get_lines(cropped_edges)
    line_segment_image = display_lines(frame, line_segments)
    show_image("line segments", line_segment_image)

    lane_lines = get_lane_lines(frame, line_segments)
    lane_lines_image = display_lines(frame, lane_lines)
    show_image("lane lines", lane_lines_image)

    return lane_lines, lane_lines_image


def edges(image):
    ''' Filtra los bordes de color rosa '''
    im_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    lower_pink = np.array([150, 50, 120])
    upper_pink = np.array([180, 255, 255])
    mask = cv2.inRange(im_hsv, lower_pink, upper_pink)

    edges = cv2.Canny(mask, 200, 400)

    return edges


def crop_top(image, cut):
    ''' Corta la mitad superior de la imagen '''
    height, width = image.shape
    mask = np.zeros_like(image)

    polygon = np.array([[
        (0, height * cut),
        (width, height * cut),
        (width, height),
        (0, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    show_image("mask", mask)
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image


def get_lines(edges):
    ''' Obtiene las líneas presentes en una imagen '''
    lines = cv2.HoughLinesP(
        edges, 
        np.array([]), # vector de salida
        rho=1, # distancia en píxeles
        angle=(np.pi / 180), # distancia angular en radianes
        min_threshold=25, # mínimo de votos
        minLineLength=10, # longitud mínima de la línea
        maxLineGap=6 # distancia máxima entre líneas
    )

    return lines


def get_lane_lanes(image, lines):
    '''
    Combina las líneas en una o dos líneas de calzada
    Si la pendiente de todas las líneas es < 0: todas las líneas son del lado izquierdo
    Si la pendiente de todas las líneas es > 0: todas las líneas son del lado derecho
    '''

    lane_lines = []
    if lines is None:
        return lane_lines

    height, width, _ = image.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # la línea izquierda debería estar en el tercio izquierdo de la pantalla
    right_region_boundary = width * boundary # la línea izquierda debería estar en el tercio derecho de la pantalla

    for line in lines:
        for x1, y1, x2, y2 in line:
            if x1 == x2:
                logging.info('Ignorando línea vertical (pendiente = infinito): %s' % line)
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    logging.debug('líneas de calzada: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

    return lane_lines


def compute_steering_angle(frame, lane_lines):
    ''' Calcula el ángulo de giro a partir de las líneas de la calzada '''

    if len(lane_lines) == 0:
        return -90

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        logging.debug('Se ha detectado una línea. %s' % lane_lines[0])
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        mid = int(width / 2)
        x_offset = (left_x2 + right_x2) / 2 - mid

    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
    steering_angle = angle_to_mid_deg + 90

    logging.debug('new steering angle: %s' % steering_angle)
    return steering_angle


def stabilize_steering_angle(curr_steering_angle, new_steering_angle, num_of_lane_lines, max_angle_deviation_two_lines=5, max_angle_deviation_one_lane=3):
    ''' Acota el ángulo de giro para evitar giros bruscos '''

    if num_of_lane_lines == 2 :
        max_angle_deviation = max_angle_deviation_two_lines
    else :
        max_angle_deviation = max_angle_deviation_one_lane
    
    angle_deviation = new_steering_angle - curr_steering_angle
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle
                                        + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle
    logging.info('Ángulo calculado: %s, ángulo estabilizado: %s' % (new_steering_angle, stabilized_steering_angle))

    return stabilized_steering_angle


############################
# Funciones de utilidad
############################
def display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    ''' Muestra por pantalla una línea en la dirección a la que se dirije el coche '''
    
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image


def length_of_line_segment(line):
    x1, y1, x2, y2 = line
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def show_image(title, frame, show=_SHOW_IMAGE):
    if show:
        cv2.imshow(title, frame)


def make_points(frame, line):
    ''' Crea los puntos que forman la línea de dirección '''
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height 
    y2 = int(y1 * 1 / 2)  

    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]


############################
# Funciones de prueba
############################
def test_photo(file):
    land_follower = HandCodedLaneFollower()
    frame = cv2.imread(file)
    combo_image = land_follower.follow_lane(frame)
    show_image('final', combo_image, True)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_video(video_file):
    lane_follower = HandCodedLaneFollower()
    cap = cv2.VideoCapture(video_file + '.avi')

    # salta el primer segundo de video
    for i in range(3):
        _, frame = cap.read()

    video_type = cv2.VideoWriter_fourcc(*'XVID')
    video_overlay = cv2.VideoWriter("%s_overlay.avi" % (video_file), video_type, 20.0, (320, 240))
    try:
        i = 0
        while cap.isOpened():
            _, frame = cap.read()
            print('frame %s' % i )
            combo_image= lane_follower.follow_lane(frame)
            
            cv2.imwrite("%s_%03d_%03d.png" % (video_file, i, lane_follower.curr_steering_angle), frame)
            
            cv2.imwrite("%s_overlay_%03d.png" % (video_file, i), combo_image)
            video_overlay.write(combo_image)
            cv2.imshow("Carretera con líneas de calzada", combo_image)

            i += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        video_overlay.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    test_video('/home/pi/DeepPiCar/driver/data/tmp/video01')
    #test_photo('/home/pi/DeepPiCar/driver/data/video/car_video_190427_110320_073.png')
    #test_photo(sys.argv[1])
    #test_video(sys.argv[1])
