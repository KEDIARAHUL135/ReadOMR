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

import GetAnswers as GA

# Size after cropping
RESIZE_TO = (600, 800)

EXPAND_BY_PIXEL = 20

MIN_SCORE_REQ = 5
# Threshold length of corner circle
## It means that the corner circle must be present at what max distance from the boundary(Keep this value small).
ThreshLengthCC = 90

# Macros for HoughCircle
dp = 1.3
MinRadius = 0
MaxRadius = 20

# Threshold Image at this value:
ThresholdImageAt = 75

# Expand the total area of OMR Sheet after detecting corners
EXPAND_INITIAL_POINTS = 0           # 1 for yes and 0 for no
EXPAND_BY = (0, 20, 0, 20)            # Size in pixel by which to want to expand rectangle
                                    # (It can be negative also to contract size).
                                    # First element to expand wrt left edge,
                                    # Second element to expand wrt top edge,
                                    # Third element to expand wrt right edge &
                                    # Last element to expand wrt bottom edge.


# List of alphabets and numbers
## Last character is '_' for empty answer(Blank space/No answer).
Alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
            'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
            'Y', 'Z', '_']
Numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '_']
