# ReadOMR

This project aims to read information from a scanned OMR sheet.


### Installation

It is preffered that you run this program in  PyCharm.

#### Steps to installation:
* Clone this repository on your Desktop.
* Open Pycharm.
* From the menu, select File -> Open. In the popup, select the folder clonned and press OK. 
* Make sure that you have opencv and opencv contrib libraries installed. To do so, open terminal in pycharm and execute the following instructions:
`$ pip3 install opencv-python`
`$ pip3 install opencv-contrib-python`
* After the installation is completed, from the menu, select Run ->   Run...


### About the project

This project aims to read scanned images of OMR Sheet and extract details like name, father's name, answer sheet number, school name, branch, mobile number and answers to questions.

#### Approach

First we will find the four boundary circles of the OMR Sheet so that we can use them to allign the image and resize it according to our demand and then read data from it. By doing this, we will be sure that particular data is located at specific places.
Then we will make bounding boxes for each answer. In other words we will crop out rectangles from the places where answers are filled and then look in those rectangles for the answer.
After that, in each rectangle, we will iterate in specific rows/columns and look for filled circles. By estimating the position of the circles, we can estimate the answr filled. We will then store these answers in a json file. 
