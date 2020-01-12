# ReadOMR

This project aims to read information from a scanned OMR sheet.


### Installation

Installation procedure is given in the file InstalltionProcess_python&opencv.pdf.
Ignore last 2-3 points in which ask you to check the version from another file.
PS - This installation process file was obtained in a competition of IIT Bombay recently named E-Yantra. The installation was a part of Task 0.1.

After installing python and OpenCV on your desktop as shown, clone/download this repository and navigate to src folder.
Right click on main.py file and select Edit with IDLE.
Now run main.py file. 
If a error arrises stating -
`import src.macros as M
ModuleNotFoundError: No module named 'src'`
Then simply remove "src." from `$ import src.macros as M` thus making it -
`$ import macros as M`

### About the project

This project aims to read scanned images of OMR Sheet and extract details like name, father's name, answer sheet number, school name, branch, mobile number and answers to questions.

#### Approach

First we will find the four boundary circles of the OMR Sheet so that we can use them to allign the image and resize it according to our demand and then read data from it. By doing this, we will be sure that particular data is located at specific places.
Then we will make bounding boxes for each answer. In other words we will crop out rectangles from the places where answers are filled and then look in those rectangles for the answer.
After that, for each answer we will make a grid across the answer image so that in each grid box, there is a option circle approximately. Now the image is converted to thresholded grayscale so that for every darkened circle, maximum colour of that grid box becomes black. From this the histogram matrix is found for the grid. For each answer character, we will see go through that particular col/row in the histogram matrix and find the element corresponding to the maximum number of black pixels. The answer character is estimated to be corresponding to that element and thus the answer is found.


### Assumptions

* The OMR Sheet image should be erect and properly illuminated in the input.
* No extra boundary(noise) is expected in the input OMR Sheet image and the four corner circles must be near the corners of the image(about less that 90 pixel from respective corner).
* Answers should be properly darkened.


### Project Pending

* Answers to questions School's Name, Branch, Father's Name and Booklet Number is not extracted but the images corresponding to those questions is cropped and stored in suitable variables. Another algo for reading text is to be applied on those images to get answer.
* Answers to other questions are not stored in json file yet. They are just being printed in the terminal.


### Bugs

* In the Student's Name, total number of rows is 26 but the number of rows as input is given to be 25 for correct answer. Due to this the letter Z will probably not be detected.
* Options of Class are starting from 4 due to which the answer output is comming 4 less than the original output.
* If Section H to M are selected, the program will not be able to tell the proper answer as apart from other questions' options, in this question, the option are split into two rows.
* For the Answers of questions 1 to 30, mostly the answers are detected correctly but sometimes the answers to 1 or 2 question are comming incorrect. This is due to the fact that answer coloured overshoots the assigned circle and enters the area of answer below or above that. Also another major reason to this is that the bottom two corner circles are too close to the answer options of the bottommost questions(5, 10, 15, 20, 25, 30) due to which the grid are not formed properly.

If I had more time, all the bugs would be solved and answer would be stored in json file.

### References
The project is made completely by me with the help in some pre-defined function from open source website link opencv.org, stackoverflow, we3shools, etc.
