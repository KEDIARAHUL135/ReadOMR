###############################################################################
# File          : macros.py
# Created by    : Rahul Kedia
# Created on    : 10/01/2020
# Project       : ReadOMR
# Description   : This file contains the modifiable macros (variables)
#                 used in the main source code. By playing with these
#                 variables only, one can modify the main source code
#                 to adapt to different types of OMR Sheets and we can
#                 also enhance the output of the code.
################################################################################


# Input Image Path
InputImagePath = "InputImages/Filled1.1.jpeg"


# Size of OMR Sheet - square of length -> Size
Size = 800  # DONOT CHANGE THIS


# Thershold length of corner circle
## It menas that the corner circle must be present at what max distance from the boundary
ThreshLengthCC = 90


# Macros for HoughCircle
dp = 1.3
MinRadius = 0
MaxRadius = 20


# Rectangle Top Left Corner's Coordinates, length, and width for different answers
class ROI_Answer:
    def __init__(self, Corner_X, Corner_Y, Width, Length):
        self.C_X = Corner_X
        self.C_Y = Corner_Y
        self.Width = Width
        self.Length = Length


StN = ROI_Answer(30, 51, 497, 460)              # Student's Name
MN = ROI_Answer(548, 234, 212, 178)             # Mobile Number
Class = ROI_Answer(591, 446, 147, 17)           # Class
Branch = ROI_Answer(82, 634, 649, 29)           # Branch
BN = ROI_Answer(549, 27, 213, 129)              # Booklet Number
ScN = ROI_Answer(125, 602, 606, 31)             # School Name
Section = ROI_Answer(613, 478, 148, 38)         # Section
FN = ROI_Answer(124, 664, 607, 29)              # Father's Name
A_1t5 = ROI_Answer(66, 720, 81, 80)             # Answers - 1 to 5
A_6t10 = ROI_Answer(188, 720, 80, 80)           # Answers - 6 to 10
A_11t15 = ROI_Answer(309, 719, 79, 81)          # Answers - 11 to 15
A_16t20 = ROI_Answer(429, 719, 79, 81)          # Answers - 16 to 20
A_21t25 = ROI_Answer(549, 719, 80, 81)          # Answers - 21 to 25
A_26t30 = ROI_Answer(671, 720, 81, 80)          # Answers - 26 to 30

