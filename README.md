# OmniSeekers
## Description
This project presents an implementation of a swarm of omnidirectional robots with the aim of carrying out Search-and-Rescue tasks without the use of GPS or mapping such as SLAM. For this reason, we have based ourselves on exploration techniques based on Bug Algorithms, specifically on the Swarm Gradient Bug Algorithm (SGBA), presented in the article ["Minimal navigation solution for a swarm of tiny flying robots to explore an unknown environment"¹](https://www.science.org/doi/10.1126/scirobotics.aaw9710). The objective of this project is to present an efficient solution for the search for victims and targets in indoor environments where human access can pose a risk. To carry out the coverage of an extensive space in a consistent time, we have considered that the use of techniques developed in the field of Swarm Robotics is very suitable for distributing the exploration task among different entities with relatively simple objectives. Furthermore, this approach allows us to use affordable controllers that in other cases where computation would be more expensive. For the recognition of victims and the global coordination of the robots, a central server will be used from which computer vision techniques and odometry handling will be applied. 

We designed a 3-wheel omnidirectional robot base for our swarm of robots because it uses fewer components, is lighter in weight, and provides full mobility for the robots. We chose the ESP32 chipset as the robots' controller for both video transmission and robot control. This enables the robots to communicate with each other and the server efficiently, offering a fast and cost-effective implementation. 

## Install

```
pip install -r requirements.txt
```

## Libraries

The following libraries are essential for the project:

  * **[CoppeliaSim](https://manual.coppeliarobotics.com/en/remoteApiClientSide.htm):** For robot simulation.
  * **[OpenCV](https://opencv.org/):** For computer vision and image processing.
  * **[NumPy](https://numpy.org/):** For numerical computations.
  * **[Scipy](https://www.scipy.org/):** For scientific computing.”
  * **[matplotlib](https://matplotlib.org/):** For plotting and visualizing data.

## To do

## References

- 1. McGuire, K. N., De Wagter, C., Tuyls, K., Kappen, H. J., & de Croon, G. C. H. E. (2019). [Minimal navigation solution for a swarm of tiny flying robots to explore an unknown environment. Science Robotics](https://www.science.org/doi/10.1126/scirobotics.aaw9710)
