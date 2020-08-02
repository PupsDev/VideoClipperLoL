import cv2
import subprocess as sp
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import numpy as np
import sys, getopt
import json

   
frames = 600

def applyMask(img1, img2, mask):

	img1 = cv2.bitwise_and(img1,  cv2.bitwise_not(mask))
	img2 = cv2.bitwise_and(img2,  cv2.bitwise_not(mask))

	# convert the images to grayscale
	img1  = cv2.cvtColor(img1.astype('uint8') * 255 , cv2.COLOR_BGR2GRAY)
	img2  = cv2.cvtColor(img2.astype('uint8') * 255 , cv2.COLOR_BGR2GRAY)

	
	return mse(img1, img2)
	
def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;

	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	if err<100:
		print("MSE between the two pictures are " + str(err))
	return err

def getKeyFrame(command, reference ,mask):
	pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=-1)
	time = 0

	for i in range(frames):
		# Capture frame-by-frame
		raw_image = pipe.stdout.read(1920*1080*3)

		if raw_image :
			# transform the byte read into a numpy array
			image = np.fromstring(raw_image, dtype='uint8')
			image = image.reshape((1080,1920,3)) 

			if applyMask(image,reference, mask) < 100 : #mse margin for same pictures 
				print("Found in frame " + str(i) + " !")
				time = i
				pipe.terminate()
	

	return time

def getTimeStamp(frames, source, reference, mask, start):

	
	FFMPEG_BIN = "ffmpeg"
	command = [ FFMPEG_BIN,
	'-ss', str(start),
	'-i', source, # fifo is the named pipe
	'-pix_fmt', 'bgr24', # opencv requires bgr24 pixel format.
	'-vcodec', 'rawvideo',
	'-an','-sn', # we want to disable audio processing (there is no audio)
	'-t', str(frames),
	'-hide_banner',
	'-loglevel', 'warning',
	'-vf',
	'fps=0.5',
	'-f', 'image2pipe', '-']


	frame = getKeyFrame(command, reference, mask)

	#fps=0.5 -> 1frame per 2 seconds
	return timedelta(seconds = frame*2)

#return start and duration timedelta
def getKeyTuplet(timeStampGame,source,start, frames=200):
	reference = cv2.imread("images/start_reference.png")
	maskIntro = cv2.imread("images/mask/start.png")

	reference2 = cv2.imread("images/end_reference.png")
	maskEnd = cv2.imread("images/mask/end.png")
	
	print("Searching for loading screen..")
	timeStart = getTimeStamp(frames,source, reference, maskIntro,start)
	

	print("Searching for ending screen..")
	timeEnd = getTimeStamp(frames,source, reference2, maskEnd, start+timeStampGame)

	delta = (timeEnd+timeStampGame)-(timeStart+start)#might be buggy

	return (timeStart,delta)



def getLength(filename):
    result = sp.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=sp.PIPE,
        stderr=sp.STDOUT)
    return float(result.stdout)

def stringToDeltaTime(string):
	t = datetime.strptime(string,"%H:%M:%S")
	delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
	return delta
def clipper(data,source):

	#total length of the video
	videoLength = timedelta(seconds=getLength(source))

	#where we start first -> date of creation of the game from riotapi relative to postion in the video
	currentTime = stringToDeltaTime(data["creation"][0])
	i=0

	
	for gameDuration in data['duration']:
		print("\n")
		print("Processing game " +str(i)+ " ...")
		if(videoLength>stringToDeltaTime(gameDuration)+currentTime):
			game = getKeyTuplet(stringToDeltaTime(gameDuration), source, currentTime, frames)

			#current time in the video + start of loading
			start = str(game[0]+currentTime)

			#currentTime + start of loading + inner delta
			duration = str(game[1]+game[0]+currentTime)

			print("(Start,Duration) --> (" + start +", " + duration +")")
			print("\n")
			
			print("Extracting game " + str(i) + " ...")
			FFMPEG_BIN = "ffmpeg"
			command3 = [ FFMPEG_BIN,
			'-ss', start,
			'-i', source,
			'-to', duration,
			'-y',
			'-hide_banner',
			'-loglevel', 'warning',
			'-c','copy',
			'game'+str(i)+'.mp4']
			sp.call(command3)

			print("Complete !")
			print("\n")
			print("##############################")

			cv2.destroyAllWindows() 
			i+=1
			if i < len(data["creation"]):
				currentTime = stringToDeltaTime(data["creation"][i])

		else :
			print("Error ! Video duration not long enough")
			break
	print("\n")
	print(str(i) + " clip(s) have been made !" ) 


def main(argv):

	try:
	  opts, args = getopt.getopt(argv,"hi:o:",["input=","output="])
	except getopt.GetoptError:
	  print ('clipper.py -i <inputfile> -o <output>')
	  sys.exit(2)
	for opt, arg in opts:
	  if opt == '-h':
	     print ('clipper.py -i <inputfile> -o <output>')
	     sys.exit()
	  elif opt in ("-i", "--input"):
	     source = arg
	  elif opt in ("-o", "--output"):
	     output = arg

	     
	with open('gamesDuration.json', 'r') as json_file:
		data = json.load(json_file)

	clipper(data,source)

if __name__ == "__main__":

	main(sys.argv[1:])

