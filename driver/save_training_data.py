"""
This program saves the driving frames as labelled images.

The desired steering angle (label) for each frame 
is computed by hand_coded_lane_follower.py
and saved in the name of the image.
"""

import sys
import cv2
from hand_coded_lane_follower import HandCodedLaneFollower


def save_image_and_steering_angle(video_file):
    lane_follower = HandCodedLaneFollower()
    cap = cv2.VideoCapture(video_file + ".avi")

    try:
        i = 0
        while cap.isOpened():
            _, frame = cap.read()
            lane_follower.follow_lane(frame)
            cv2.imwrite(
                f"{video_file}_{i}_{lane_follower.curr_steering_angle}.png",
                frame,
            )
            i += 1
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    save_image_and_steering_angle(sys.argv[1])