import os
import sys
import cv2
import pathlib
import subprocess
import time
import numpy as np


def main():
	network_length = 5

	curr_pat = "*.avi"


	classes = []
	for root,dirs,file in os.walk("./kth"):
		for dir_name in dirs:
			classes.append(dir_name)
	#print(classes)

	def image_name(filename):
		#print(filename)
		lister = filename.split('/')[2].split('_')
		final_name = lister[0][6:]+lister[2]
		#print(final_name)
		return(final_name)


	dirName = 'processed'
	if not os.path.exists(dirName):
		os.mkdir(dirName)
		print("Pre-processing ...")
		for curr_class in classes:
			os.mkdir(dirName+"/"+curr_class)


		for curr_class in classes:
			
			
			curr_dir = pathlib.Path('./kth/'+curr_class)
			for curr_file in curr_dir.glob(curr_pat):
				list_arr= []
				vidObj = cv2.VideoCapture(str(curr_file))
				try :
					frames = int(subprocess.check_output("ffmpeg -i "+str(curr_file)+" -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep 'frame=' | cut -f 3 -d ' '", shell=True))
				except ValueError:
					continue
				else :
					for x in range(31,34):
						vidObj.set(1,x)
						success, image = vidObj.read()
						if success:
							if x%3 == 0:
								average = abs(one-two) + image
								#average = (one + two + image)/3        #average of 3 neighbouring frames
								print("average dim : ",average.shape)
								average = np.uint8(average)
								gray = cv2.cvtColor(average, cv2.COLOR_BGR2GRAY)
								cv2.imwrite("3.jpg" , image)
								#gray = cv2.cvtColor(average, cv2.COLOR_BGR2GRAY)
								#print("average gray : ",gray.shape)
								cv2.imwrite("avgd.jpg" , gray)

								#list_arr.append(gray)
							elif x%3 == 1 :
								one = image
								print(one.shape)
								cv2.imwrite("1.jpg" , image)
							elif x%3 == 2 :
								two = image
								print(two.shape)
								cv2.imwrite("2.jpg" , image)
					#video_array = np.stack((list_arr),axis = 0)
					
					vidObj.release()
					#print(str(curr_file)," : ",frames)
					#vidObj.release()
				break
				'''
				

				#vidObj.release()
				for x in range(network_length):
					
					success, image = vidObj.read() 
					cv2.imwrite("frame%d.jpg" % count, image) 
	
					count += 1
				'''
	print("Pre-Processing done!")



if not os.path.exists('processed'):
	main()
	
else:    
	print("Pre-processed Directory already exists.\nPlease input 'yes' to delete existing folder and start pre processing again : ")
	com = input()
	if com == 'yes':
		subprocess.check_output("rm -rf processed", shell=True)
		main()
	else:
		print("Exiting")

#ffmpeg -i 00000.avi -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep 'frame=' | cut -f 3 -d ' '
