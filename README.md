# SMART PI CAR
#### Un proyecto para construir un coche de conducción autónomo en miniatura 

## EL HARDWARE

Sun Founder PiCar-V kit 
![image](https://user-images.githubusercontent.com/74978050/189338200-6830eb05-ace2-41a8-995a-be26a52df5c1.png)

Raspberry Pi Model 3B+ 
![image](https://user-images.githubusercontent.com/74978050/189338829-ff91b5ce-db12-42d2-994b-6d7aa143d27d.png)

Acelerador Coral Edge TPU 
![image](https://user-images.githubusercontent.com/74978050/189338830-47b72149-811e-47d0-9358-f1a2c3cdd8c4.png)

Complementos:
- 2 baterías 18650 y un cargador
- Tarjeta micro SD

## EL SOFTWARE

El código está programado en Python, empleando las bibliotecas del fabricante del coche 
y diversas bibliotecas de aprendizaje automático como Tensorflow, Keras y OpenCV.

## GUÍA DE MONTAJE

A modo de resumen orientativo, los pasos a seguir para la preparación del coche son sido los siguientes:

1. Formateo de la tarjeta micro SD en formato FAT32 e instalación del sistema operativo Raspberry Pi OS
2. Montaje del coche, siguiendo las instrucciones del fabricante
3. Instalación de las bibliotecas necesarias y sus dependencias
4. Instalación de los complementos necesarios para ejecutar el modelo en el acelerador. Deben seguirse las instrucciones de la web de PyCoral.

## GUÍA DEL REPOSITORIO

- **DRIVER**: contiene los programas que permiten conducir el coche
   - **autonomous_driver.py**: realiza la inferencia del modelo de aprendizaje profundo y devuelve el ángulo de giro del coche para una imagen dada.
   - **hand_coded_lane_follower.py**: conduce el coche de forma autónoma pero programado esxplícitamente. También devuelve el ángulo de giro.
   - **save_training_data.py**: a partir de un video de conducción, guarda una imagen de cada fotograma con su respectivo ángulo de giro, calculado mediante hand_coded_lane_follower.py.
   - **smart_pi_car.py**: realiza la conducción del coche de la forma escogida por el usuario. Puede ser mediante el teclado o mediante los programas anteriores. También permite guardar imágenes etiquetadas durante la conducción manual.

- **MODELS**: contiene los distintos modelos de aprendizaje profundo entrenados y el código empleado


*This project is made by Andrés Martínez Martínez for the Final Year Project of Computing Engineering in Polytechnic University of Valencia.*
