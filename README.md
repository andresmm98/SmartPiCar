# SmartPiCar: A small car that drives itself thanks to computer vision

The car can follow circuits marked with adhesive tape over floors that it has not seen before by seeing the road with its 320x240 resolution ~$10 camera. 
It does it locally, employing a Raspberry Pi and doing the model inference in an Edge TPU. 
The work is based on [DeepPiCar](https://github.com/dctian/DeepPiCar) by dctian.

On top of Dctian's work, it adds the following capabilites:
- Achieve autonomy with the SunFounder kit camera, which has a lower quality
- Keyboard training: drive the car with the keyboard & collect labelled training images
- Autonomy over different floors: thanks to more quantity & diversity of training data
- Small tweaks to improve efficiency, like multi-threading for preprocessing
- Updated some deprecated functions (2024)

https://github.com/anmar36a/SmartPiCar/assets/74978050/43bf119e-7c05-4544-9e88-bd75f767d007

## HARDWARE USED

Sun Founder PiCar-V kit

<img src="https://user-images.githubusercontent.com/74978050/189338200-6830eb05-ace2-41a8-995a-be26a52df5c1.png" alt="CAR" width="300"/>

Raspberry Pi Model 3B+ 

<img src="https://user-images.githubusercontent.com/74978050/189338829-ff91b5ce-db12-42d2-994b-6d7aa143d27d.png" alt="drawing" width="300"/>

Coral Edge TPU Accelerator

<img src="https://user-images.githubusercontent.com/74978050/189338830-47b72149-811e-47d0-9358-f1a2c3cdd8c4.png" alt="drawing" width="300"/>

Accessories:
- 2 18650 batteries and a charger
- Micro SD card

## SOFTWARE USED

The code is programmed in Python, using the car manufacturer's libraries
and various machine learning libraries such as Tensorflow, Keras and OpenCV. The OS of the car is the Raspberry Pi OS.

## ASSEMBLY GUIDE

As a summary, the steps to build the SmartPiCar were the following:

1. Formatting of the micro SD card in FAT32 format and installation of the Raspberry Pi operating system.
2. Assembly of the car, following the [manufacturer's instructions](https://docs.sunfounder.com/projects/picar-v/en/latest/).
3. Installation of the necessary libraries and their dependencies.
4. Development of the deep learning model.
5. Development of the code to collect training data.
6. Collection and cleaning of the training data.
7. Training of the model.
9. Deployment of the model in the accelerator, following the [manufacturer's instructions](https://coral.ai/docs/edgetpu/tflite-python/#update-existing-tf-lite-code-for-the-edge-tpu).
10. Repetition of steps 4-7 until a good solution was achieved.

## MAIN DIFFICULTIES ENCOUNTERED
- Hardware malfunctioning: both the micro SD card reader and one car servo failed frequently
- Low quality camera: this was the bottleneck of the project. The angle of vision was so low
  that the lane lines had to be very close to the car and sudden turn were not possible.
- Camera positioning: since the camera is not fixed to the car & 2 degrees of variation can
  considerably affect results, there needs to be a methodology to ensure the position of the
  camera is always the same.
- Processor's speed: The Raspberry Pi struggled to handle remote development and execution
  of the code.
  
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
