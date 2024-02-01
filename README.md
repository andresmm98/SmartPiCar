# SMART PI CAR
#### Un pequeño coche atónomo capaz de seguir trazados no vistos previamente

https://github.com/andresmm98/Smart-Pi-Car/assets/74978050/1ff6c54e-181c-475f-b72f-86e8466ac119

## HARDWARE EMPLEADO

Sun Founder PiCar-V kit

<img src="https://user-images.githubusercontent.com/74978050/189338200-6830eb05-ace2-41a8-995a-be26a52df5c1.png" alt="CAR" width="300"/>

Raspberry Pi Model 3B+ 

<img src="https://user-images.githubusercontent.com/74978050/189338829-ff91b5ce-db12-42d2-994b-6d7aa143d27d.png" alt="drawing" width="300"/>

Acelerador Coral Edge TPU 

<img src="https://user-images.githubusercontent.com/74978050/189338830-47b72149-811e-47d0-9358-f1a2c3cdd8c4.png" alt="drawing" width="300"/>

Complementos:
- 2 baterías 18650 y un cargador
- Tarjeta micro SD

## SOFTWARE EMPLEADO

El código está programado en Python, empleando las bibliotecas del fabricante del coche 
y diversas bibliotecas de aprendizaje automático como Tensorflow, Keras y OpenCV.

## GUÍA DE MONTAJE

A modo de resumen, los pasos para la preparación del coche han sido los siguientes:

1. Formateo de la tarjeta micro SD en formato FAT32 e instalación del sistema operativo Raspberry Pi OS
2. Montaje del coche, siguiendo las instrucciones del fabricante
3. Instalación de las bibliotecas necesarias y sus dependencias
4. Instalación de los complementos necesarios para ejecutar el modelo en el acelerador. Deben seguirse las instrucciones de la web de PyCoral.

## GUÍA DEL REPOSITORIO

- **driver**: contiene los programas de conducción
   - **autonomous_driver.py**: realiza la inferencia del modelo de aprendizaje profundo y devuelve el ángulo de giro del coche para una imagen dada.
   - **hand_coded_lane_follower.py**: conduce el coche de forma autónoma pero programado esxplícitamente. También devuelve el ángulo de giro.
   - **save_training_data.py**: a partir de un video de conducción, guarda una imagen de cada fotograma con su respectivo ángulo de giro, calculado mediante hand_coded_lane_follower.py.
   - **smart_pi_car.py**: conduce el coche de la forma escogida por el usuario: manualmente o empleando uno de los programas anteriores. También permite guardar imágenes etiquetadas durante la conducción manual.
- **models**: contiene el código de los modelos de aprendizaje automático y varios modelos entrenados
   - **code/cnn-nvidia**: modelo con mejor rendimiento. Está basado en una arquitectura propuesta por Nvidia.
   - **models/lane-navigation-best-model**: modelo con mejores resultados, utilizado en _autonomous_driver.py_.

*This project is made by Andrés Martínez Martínez for the Final Year Project of Computing Engineering in Polytechnic University of Valencia.*
