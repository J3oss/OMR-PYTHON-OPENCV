import numpy as np
import cv2 as cv
 
def CleanGetCentroids(img,seX,seY): 
    #cleaning image
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(seX,seY))
    opening = cv.morphologyEx(255 - img, cv.MORPH_OPEN, kernel)
    ret,img = cv.threshold(opening,127,255,cv.THRESH_BINARY)
    #getting centroids of answers
    _, _, _, centroids = cv.connectedComponentsWithStats(img,connectivity=8)
    return centroids[1:]

def Getanswer(question,answer_array,startX,endX,acceptable_range,format_string):
    #treating  multiple answers or no answer at all
    if len(question) == 0 :
        out.write(format_string+"no answer\n")
    elif len(question) > 1 :
        out.write(format_string+"more than one answer\n")
    else:
        valid = 0
        #special treatment for question 2
        if question[0][0] == processed_positions[2][0][0] and question[0][1] == processed_positions[2][0][1]: #checking if this is the second question  
            for answer in range(0,len(answer_array)):
                if processed_positions[2][0][0] < startX + (answer * acceptable_range) :
                    if processed_positions[2][0][1] < 477: #checking which row of answers in question 2
                        valid = 1
                        out.write(program[answer] + "\n")
                    else :
                        if answer < 4 :
                            valid = 1
                            out.write(program[answer+7] + "\n")
                    break
        #normal flow of any other question
        else:                                                                         
            for answer in range(0,len(answer_array)):
                if question[0][0] < startX + (answer * acceptable_range) :
                    valid = 1
                    out.write(format_string+answer_array[answer] + "\n")
                    break
        if valid == 0 : #checking if there was an answer in the acceptable range
            out.write(format_string+"not a valid answer\n")

#answers Arrays
gender = ["not a valid answer","Gender : Male" , "Gender : Female"]
semster = ["not a valid answer","Semster : Fall","Semster : Spring","Semster : Summer"]
program = ["not a valid answer","program : MCTA","Program : ENVER","Program : BLDG","Program : CESS","Program : ERGY","Program : COMM","Program : MANF","Program : LAAR","Program : MATL","Program : CISE","Program : HAUD"]
answer = ["not a valid answer","Strongly Agree","Agree","Neutral","Disagree","Strongly Disagree"]

#Data Arrays
questions_positions = [294,376,477,976,1018,1058,1097,1137,1258,1298,1337,1377,1416,1456,1574,1615,1655,1776,1817,1895,2013,2054] #array for y positions of questions
processed_positions = []
for i in range(22): #preparing the 2d array
    processed_positions.append([])

#reading image & preparing output
path = raw_input("""PLEASE ENTER IMAGE NAME IN THE SAME FOLDER AS THE PROJECT...\n      WITH FILE TYPE...\n""")
img = cv.imread(path,0)
out = open(path[0:-4]+".txt", "wt")

#getting minor orientation angle
edges = cv.Canny(img,50,150,apertureSize = 3)
lines = cv.HoughLines(edges,1,np.pi/180,200)
angle = (lines[0][0][1] * 180/np.pi) - 90 #converting theta to angles and getting angle relative to x axis

#getting major orientation angle and rotating necessarily
if abs(angle) > 45 :#if magnitude of angle is greater than 45 degrees then it is a major orientation concern
    angle -= 90
    img = cv.rotate(img,0) #image is now either (upright+small angle) or (inverted+small angle)
M = cv.getRotationMatrix2D(((img.shape[1])/2.0,(img.shape[0])/2.0),angle,1) #rotation matrix to rotate and keep with same aspect ratio
img = cv.warpAffine(img,M,(img.shape[1],img.shape[0]), borderValue=(255,255,255)) #rotate and make new background white

#cleaning and getting centroids
centroids = CleanGetCentroids(img,19,19) #clean image and leave orientation boxes

#adjusting flips
#normal image has the alone box(from orientation boxes) approximatly at x = 1200 and y = 50
if (centroids[-1][0] > 400 and centroids[-1][0] < 500) and (centroids[-1][1] > 2230 and centroids[-1][1] < 3020) : #detecting inverted image using the alone box(from orientation boxes)
    img = cv.rotate(img,1) #rotate image by 180 degrees
if (centroids[-3][0] > 1130 and centroids[-3][0] < 1250) and (centroids[-3][1] > 2230 and centroids[-3][1] < 3020) : #detecting horizontally flipped image using the alone box(from orientation boxes)
    img = cv.flip(img, 0) #flip image about x-axis
if (centroids[2][0] > 400 and centroids[2][0] < 500) and (centroids[2][1] > 25 and centroids[2][1] < 75) : #detecting vertically flipped image using the alone box(from orientation boxes)
    img = cv.flip(img, 1) #flip image about y-axis

#cleaning and getting centroids
centroids = CleanGetCentroids(img,20,20) #clean image and removing orientation boxes

#filling processing array
for i in range(len(centroids)) :  
    for j in range(22) :
        if centroids[i][1] < questions_positions[j]+30 and centroids[i][1] > questions_positions[j]-30: # check if the current centroid belongs to any of the questions in the paper if not ignore this centroid
            processed_positions[j].append(centroids[i])
            break

#getting answers
Getanswer(processed_positions[0],gender,1189,1457,134,"")
Getanswer(processed_positions[1],semster,422,1220,266,"")
Getanswer(processed_positions[2],program,392,1316,132,"")

out.write("\nTeaching Session category :\n")
for processed_Position in processed_positions[3:8]:
    Getanswer(processed_Position,answer,1123,1723,100,"\t")
out.write("\nCourse/Module Support category :\n")
for processed_Position in processed_positions[8:14]:
    Getanswer(processed_Position,answer,1123,1723,100,"\t")
out.write("\nCourse/Module Organization category :\n")
for processed_Position in processed_positions[14:17]:
    Getanswer(processed_Position,answer,1123,1723,100,"\t")
out.write("\nCourse/Module Resources category :\n")
for processed_Position in processed_positions[17:20]:
    Getanswer(processed_Position,answer,1123,1723,100,"\t")
out.write("\nCourse/Module Satisfaction category :\n")
for processed_Position in processed_positions[20:22]:
    Getanswer(processed_Position,answer,1123,1723,100,"\t")

out.close()
