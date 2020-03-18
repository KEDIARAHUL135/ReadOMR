# ReadOMR

This project aims to read information from a scanned OMR sheet.


### Installation

Installation procedure is given in the file InstalltionProcess_python&opencv.pdf.
Ignore last 2-3 points in which ask you to check the version from another file.
PS - This installation process file was obtained in a competition of IIT Bombay recently named E-Yantra. The installation was a part of Task 0.1.

After installing python and OpenCV on your desktop as shown, clone/download this repository and navigate to src folder.
Right click on main.py file and select Edit with IDLE.

Now run main.py file.


### How to run

* First create a configuration file for your OMR only once by calling the "Configure" of the "Config.py" file by passing appropriate parameter(Path of input image of OMR).
* Run call "main" function of "main.py" file by passing two arguments - OMR Name and Image path.
* The output answers will be stored in the "Answers.txt" file.

### About the project

This project aims to read scanned images of OMR Sheet and extract details like name, father's name, answer sheet number, school name, branch, mobile number and answers to questions.

#### Approach

Initially the project was started by finding the 4 corner circles and using them to allign the OMR Image and cropping its extra area(as present in OMR1) but now the project aims towards finding the horizontal boxes present at both sides of the OMR. This switch from circle detection to box detection is done because it is noted that the corner circles are not present in all types of OMR sheets but on a contrary the horizontal boxes are present in every OMR and it is also noted that there is a set of horizontal boxes present corresponding to every option(circles which are darkened) with the help of which the answers can be extracted however their position wrt x-axis cannot be determined by them(boxes help to determine the position wrt y-axis). 

By finding these boxes or circles and using them to allign the image, we will be sure that particular data is located at specific places and thus help in extracting answers from the image.


The horizontal boxes refered to as guiding boxes are determined completely in the file FindBoundingBoxes.py with logic as follows -

Firstly the OMR image is masked for black colour using HSV colour space, also including some level of gray colour to encounter illumination variation. The masked image have all the black and gray colour as white and rest everything as black. 

Now to find the white areas in the masked image which may correspond to the guiding boxes, two logic/approaches are made.

First approach is of matching the template images of the guiding boxes provided in TemplateImages folder with the masked image. The template image provided have few variation in the legnth and breadth size of the guiding box and also have a little rotated template box image. In the code all the template images are also varied in size(incremented and decremented in size) before comparing and all the output possible boxes from all the template images are stored in a 2D list and stored for further processing. Here it was noted that for few cases not all guiding boxes were detected even by all the template images and if we tried to add more template imagea, then few other boxes being detected earlier were not detected now.

Second approach for finding white areas is with the help of OpenCV builtin function findContours. With this we were able to detect all the white patches irrespective of their probability of being guiding box(opposite to the first approach were we were focused on finding only the guiding box). Now a great task of filtering out the required guiding box is to be done from all the white patches. Firstly for every contour(white patch) detected, a bounding rectangle is drawn around it. Initial filtering of boxes were done wrt the shape and area of the box. A box is eliminated if it has its height greater than width as in OMR the guiding boxes are all horizontal always. A box is also eliminated if its area is out of the range decided. This filter is done as after resizing all the OMRs to a particular size, the guiding box area will be within some limit for all the OMRs. Further filtering will be done afterwards.


Now the boxes detected are divided into two groups accroding to their position in the image as the boxes denoting the guiding boxes at the left hand side are surely present in the left half of the image and same for right half. Now for filtering the boxes of both the halfs, few logics are made described as follows.

Before this filtering, the tentative guiding corner boxes are found using logic described in the code itself.

First filetring is done on observing that if the guiding corner boxes found above (need not be actual corner boxes) are atleast any of the guiding boxes, then if a line is drawn from their center, then the line will intersect all the other guiding boxes and thus determining the guiding boxes. But in this logic, if any other box intersects the line, then it will also be considered and thus giving wrong output.

Second filtering is done on a similar observation. If a guiding box is expanded vertically from top and bottom only, then it will intercept atleast few other guiding boxes even if the image is tilted. Thus in this logic(filtering) all the boxes found are expanded vertically from top and bottom and the number of other boxes they intercept are counted which is named as their "Score". A minimum threshold of score is set, and if any box exceeds the minimum score, then it is predicted as a guiding box. (This logic also gives some false outputs).

Third logic is based on the same observation as that of the first but instead of using predetermined corner guiding boxes(which may be wrong), it uses a different approach inspired by the logic of RANSAC algo. In this third logic, all the pairs of two boxes are taken into consideration one by one and number of Inliers are counted for all of them. A inlier is the box whose center lies within the defined range(wrt x-axis) of the line drawn through the center of the two boxes. Now the pair of boxes having maximum number of inliers are predicted to be the part of actual guiding boxes and thus all its inliers are predicted to be the guiding boxes. Now finally the number of guiding boxes found for both the sides(right and left) are compared, if they are equal, then it is assumed that guiding boxes are found properly else a final filter is added. This filter is applied on the side with higher number of guiding boxes predicted. This filter is also inspired by the RANSAC algo and is applied on the areas of boxes. It is explained properly in the documentation of the code.

It is found that Contour logic for finding the white patches along with RANSAC inspired logic for filtering gives the best results and are accurate almost everytime unlike others.


Now before moving ahead for finding the answers, we first require the positions in the image where the answers to the questions are present and also the type of answer(alphabetic or numeric) and some other details about the question. For this, the user is firstly required to make a configuration file for the OMR. Note that this configuration file is to be made only once for a particular type of OMR and then the code will automatically detect answers for all OMRs of that type. The Configuration file can be made by calling the "Configure" of the "Config.py" file by passing appropriate parameter(Path of input image of OMR). The user is required to name the type of OMR and remember it while extracting answers. The steps to create the config file are explained properly by the commands prompting in the terminal.


Now using this configuration file, the answers can be extracted using the main.py file.


The answers are read by making a bounding boxe for each answer. Position of these bounding boxes are extracted from configuration file. In other words we will crop out rectangles from the places where answers are filled and then look in those rectangles for the answer.

After that, for each answer we will make a grid across the answer image so that in each grid box, there is a option circle approximately. Now the image is converted to thresholded grayscale so that for every darkened circle, maximum colour of that grid box becomes black. From this the histogram matrix is found for the grid. For each answer character, we will see go through that particular col/row in the histogram matrix and find the element corresponding to the maximum number of black pixels. The answer character is estimated to be corresponding to that element and thus the answer is found.
the answers are finally store in "Answers.txt" file.



### Assumptions

* The OMR Sheet image should be erect and properly illuminated in the input and the image donot have curved/folded OMR.
* In the RANSAC inspired filtering logic, it is assumed that atleast one side have all the guiding boxes detected correctly with no noise(false output).
* Answers should be properly darkened.


### References

The project is made completely by me with the help in some pre-defined function from open source website link opencv.org, stackoverflow, we3shools, etc.
If code from any other place is used, then it is mentioned in the code there itself. 
