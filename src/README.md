# src

This folder contains the source code of the project and other required folders for the project.


### Folder Structure

`CheckBrightness.py` file checks the brightness level of the image and passes the value of upper limit of "Value" for masking of the image.

`ConfigFiles` folder contains the configuration files created for each type of OMR.

`InputImages` folder contains the sample input images for the code.

`TemplateImages` folder contains the template images of guiding boxes used in the project runtime.

`Answers.txt` file contains the output of the code(Answers to the questions marked in the OMR).

`Config.py` file contains the code for configuration of the OMR sheet.

`CropOMR.py` file contains the code for cropping the OMR from appropriate positions and realligning and resizing it for further use.

`FindBoundingBoxes.py` file contains the code for finding the bounding boxes of the OMR.

`GetAnswers.py` file contains the code for extracting the answer for a question from the OMR image provided.

`macros.py` file contains the macros/variables for the source code which can be adjusted to find good results.

`main.py` file contains the main source code of the project. Everything is documented properly.

`ReadConfig.py` file contains the code to read and pass the parameters for a OMR from the config files.

