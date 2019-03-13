import os
import sys
import cv2
import pathlib
import subprocess



network_length = int(sys.argv[1])

curr_pat = "*.avi"


classes = []
for root,dirs,file in os.walk("./kth"):
    for dir_name in dirs:
        classes.append(dir_name)
print(classes)


dirName = 'processed'
if not os.path.exists(dirName):
    os.mkdir(dirName)
    print("Pre-processing completed")
    for curr_class in classes:
        os.mkdir(dirName+"/"+curr_class)
        curr_dir = pathlib.Path('./kth/'+curr_class)
        for curr_file in curr_dir.glob(curr_pat):
            count = 0
            vidObj = cv2.VideoCapture(str(curr_file))
            try :
                frames = int(subprocess.check_output("ffmpeg -i "+str(curr_file)+" -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep 'frame=' | cut -f 3 -d ' '", shell=True))
            except ValueError:
                continue
            else :
                for x in range(network_length):
                    vidObj.set(2,(x+))

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
