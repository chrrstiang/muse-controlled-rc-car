## 🏎️ RC Car Controlled w/ Motor Imagery Classification & Gyroscope

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=%white)
![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Arduino](https://img.shields.io/badge/-Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white)
![PlatformIO](https://img.shields.io/badge/platformio-%23000.svg?style=for-the-badge&logo=platformio&logoColor=F5822A)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

## ℹ️ Overview

### Purpose
Brain-computer interfaces (BCIs) serve as a tool for many aspects, one particular application being through assistive technology. This project serves as a proof-of-concept for low intrusive BCIs to be used for BCIs to power self-controlled wheelchairs, particularly for paralyzed individuals without the ability to move themselves.

Though highly intrusive BCIs may serve as a better technology for EEG data, they are expensive and not usable in everyday life. By controlling an RC Car with motor imagery classification using a low intrusive consumer BCI such as a Muse 2 headband, we can apply the same classification to steering a wheelchair using a BCI wearable in everyday life.

### Instructions

**Steer Left** - Turn head to left & left-hand motor imagery  
**Steer Right** - Turn head to right & right-hand motor imagery  
**Speed Forward** - Focus & tilt head up  
**Slow** - Relax & tilt head down  

### Accuracies
Muse 2 Headband’s accelerometer & gyroscope allow head movement detection to power the reliable controls for the car. Accuracies are expected to be from **95-99%** for head movement instructions. 

Focus instructions are hoepfully in the **90%+** range since Muse has sensors in prefrontal cortex so signal recognition should be reliable.

Motor Imagery is most recognizble through motor cortex (top of head), which the Muse 2 headband can't accurately detect due to the lack of an EEG sensor at the top of the head. We are aiming to achieve **~80%** with proper training and sufficient data.

## Installation (Pending)

## ✍️ Authors

Hi! I'm Christian Garcia, an undergraduate student at Northeastern University. Check out my links 👇

- [github.com/chrrstiang](https://github.com/chrrstiang)
- https://www.chrrstiang.com
- https://www.linkedin.com/in/christiangarcia9558/

## 💭 Feedback and Contributing

I am accepting any sort of feedback on the application. Feature ideas, bug fixes, design ideas anything.

Email me at cg0712860@gmail.com and I'll be sure to check!
