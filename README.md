# SMART PI CAR
#### A small autonomous car capable of following routes not previously seen. Based on the work of dctian/DeepPiCar.

https://github.com/andresmm98/Smart-Pi-Car/assets/74978050/008b2022-e49a-43e9-a5a2-7f268404ab1b

## HARDWARE EMPLEADO

Sun Founder PiCar-V kit

<img src="https://user-images.githubusercontent.com/74978050/189338200-6830eb05-ace2-41a8-995a-be26a52df5c1.png" alt="CAR" width="300"/>

Raspberry Pi Model 3B+ 

<img src="https://user-images.githubusercontent.com/74978050/189338829-ff91b5ce-db12-42d2-994b-6d7aa143d27d.png" alt="drawing" width="300"/>

Acelerador Coral Edge TPU 

<img src="https://user-images.githubusercontent.com/74978050/189338830-47b72149-811e-47d0-9358-f1a2c3cdd8c4.png" alt="drawing" width="300"/>

Accessories:
- 2 18650 batteries and a charger
- Micro SD card

## SOFTWARE USED

The code is programmed in Python, using the car manufacturer's libraries
and various machine learning libraries such as Tensorflow, Keras and OpenCV.

## ASSEMBLY GUIDE

As a summary, the steps to prepare the car were as follows:

1. Formatting the micro SD card in FAT32 format and installing the Raspberry Pi OS operating system.
2. Assembly of the car, following the manufacturer's instructions.
3. Installation of the necessary libraries and their dependencies.
4. Installing the necessary plugins to run the model in the accelerator. The instructions on the PyCoral website must be followed.

## REPOSITORY GUIDE

- **driver**: stores the code for driving the car
   - **autonomous_driver.py**: performs deep learning model inference and returns the steering angle of the car for a given image.
   - **hand_coded_lane_follower.py**: drives the car autonomously but programmed explicitly. It also returns the steering angle.
   - **save_training_data.py**: from a driving video, saves an image of each frame with its respective steering angle, calculated by hand_coded_lane_follower.py.
   - **smart_pi_car.py**: Drive the car in the way chosen by the user: manually or using one of the previous programs. It also allows you to save tagged images during manual driving.
- **models**: contains the code for the machine learning models and several trained models
   - **code/cnn-nvidia**: best performing model. It is based on an architecture proposed by Nvidia.
   - **models/lane-navigation-best-model**: the best model obtained, used in _autonomous_driver.py_.


*This project was made by Andrés Martínez Martínez for the Final Year Project of Computer Engineering in Polytechnic University of Valencia.*
