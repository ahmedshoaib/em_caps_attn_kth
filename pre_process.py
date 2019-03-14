import os
import sys
import cv2
import pathlib
import subprocess



network_length = 5

curr_pat = "*.avi"


classes = []
for root,dirs,file in os.walk("./kth"):
    for dir_name in dirs:
        classes.append(dir_name)
print(classes)

def image_name(filename):
    lister = filename[18:-11].split('_')
    return(lister[0]+lister[2])


dirName = 'processed'
if not os.path.exists(dirName):
    os.mkdir(dirName)
    print("Pre-processing completed")
    for curr_class in classes:
        os.mkdir(dirName+"/"+curr_class)
        for y in range(1,6):
            os.mkdir(dirName+"/"+curr_class+"/"+str(y))
        curr_dir = pathlib.Path('./kth/'+curr_class)
        for curr_file in curr_dir.glob(curr_pat):
            count = 0
            vidObj = cv2.VideoCapture(str(curr_file))
            try :
                frames = int(subprocess.check_output("ffmpeg -i "+str(curr_file)+" -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep 'frame=' | cut -f 3 -d ' '", shell=True))
            except ValueError:
                continue
            else :
                for x in range(1,16):
                    vidObj.set(1,x)
                    success, image = vidObj.read()
                    if success:
                        if x%3 == 0:
                            average = (one + two + image)/3        #average of 3 neighbouring frames
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            if cv2.imwrite("./processed/"+curr_class+"/"+str(x//3)+"/"+image_name(str(curr_file))+".jpg", gray):
                                pass
                            else:
                                print("Cannot Write file at : "+"./processed/"+curr_class+"/"+str(x//3)+"/"+image_name(str(curr_file))+".jpg")
                        elif x%3 == 1 :
                            one = image
                        else :
                            two = image
                vidObj.release()
                #print(str(curr_file)," : ",frames)
                #vidObj.release()
            
            '''
            

            #vidObj.release()
            for x in range(network_length):
                
                success, image = vidObj.read() 
                cv2.imwrite("frame%d.jpg" % count, image) 
  
                count += 1
            '''




else:    
    print("Pre-processed Directory already exists")

#ffmpeg -i 00000.avi -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep 'frame=' | cut -f 3 -d ' '
