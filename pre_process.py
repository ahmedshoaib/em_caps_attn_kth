import os
import cv2
import pathlib
import subprocess



network_length = int(sys.argv[1])

curr_pat = "*.avi"


classes = []
for root,dirs,file in os.walk("./kth"):
	for dir_name in dirs:
		classes.append(dir_name)



dirName = 'processed'
if not os.path.exists(dirName):
    os.mkdir(dirName)
    print("Pre-processing completed")
    for curr_class in classes:
    	os.mkdir(dirName+"/"+curr_class)
    	curr_dir = pathlib.Path('./'+curr_class)
    	for curr_file in currentDirectory.glob(currentPattern):
    		success = 1
    		count = 0
    		vidObj = cv2.VideoCapture(curr_file)
    		frames = os.system("ffmpeg -i "+curr_file+" -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep 'frame=' | cut -f 3 -d ' '")

    		#vidObj.release()
    		for x in range(network_length):
	        	
	        	success, image = vidObj.read() 
        		cv2.imwrite("frame%d.jpg" % count, image) 
  
        		count += 1




else:    
    print("Pre-processed Directory already exists")

#ffmpeg -i 00000.avi -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep 'frame=' | cut -f 3 -d ' '