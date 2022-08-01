import os
import cv2
import sys
import shutil
import pathlib
import subprocess

##Variables
current_dir = os.getcwd()

cdi = current_dir + '/input'
cdo = current_dir + '/output'

##Functions

def check(folder_path): # Checking if the input and output folder exists
	if not os.path.exists(folder_path):
		print("The", folder_path, " directory doesn't exist.. creating a new one")
		os.mkdir(folder_path)
		print(folder_path, "directory is created in", current_dir, ".")
	else:
		print(folder_path, "directory exists in", current_dir, ".")
		

def getvidinfo(video_location, video_name):  #Getting resolution and fps from video
	global vidfps, vidwidth, vidheight, videodurationminutes, color_settings_vid, color_settings_png
	video = cv2.VideoCapture(video_location)	

	vidfps = float(video.get(cv2.CAP_PROP_FPS))
	vidframes = (video.get(cv2.CAP_PROP_FRAME_COUNT))		#FPS and frames
	print(video_name + " has %s fps." % vidfps)
	
	videodurationseconds = int(vidframes / vidfps)								#Video duration in minutes
	videodurationminutes = float(videodurationseconds / 60)
			
	vidwidth = int(video.get(cv2.CAP_PROP_FRAME_WIDTH ))	#Resolution
	vidheight = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT ))
	print(video_name + " has a resolution of %s x %s" % (vidwidth, vidheight))

	color_info = os.popen("ffprobe -v error -show_entries stream=pix_fmt,color_space,color_range,color_transfer,color_primaries -of default=noprint_wrappers=1 " + video_location).read().splitlines()
	
	pixel_format = color_info[0][8:]
	if not pixel_format == 'unknown':
		color_settings_vid = "-pix_fmt " + pixel_format
	else:
		color_settings_vid = "-pix_fmt yuv420p"
	color_settings_png = "-pix_fmt rgb24"

	color_space = color_info[2][12:]
	if not color_space == 'unknown':
		color_settings_vid += " -colorspace " + color_space
		color_settings_png += " -colorspace " + color_space

	color_primaries = color_info[4][16:]
	if not color_primaries == 'unknown':
		color_settings_vid += " -color_primaries " + color_primaries
		color_settings_png += " -color_primaries " + color_primaries


def mktmpdir(temporary_directory_location_and_name): #Checking and making temporary directory
	global tempdir, tempinput, tempoutput
	tempdir = temporary_directory_location_and_name
	tempinput = tempdir + '/in'
	tempoutput = tempdir + '/out'
	
	if os.path.exists(tempdir):
		shutil.rmtree(tempdir)
		
	
	os.mkdir(tempdir)
	os.mkdir(tempinput)
	os.mkdir(tempoutput)
	
	'''
	Variable used outside function:
		- tempdir = temporary directory
		- tempinput = input in temporary directory
		- tempoutput = output in temporary directory
	'''
	

def vidextract(input_directory, video_name):	#Extracting audio from video, and checking if there is an audio file afterwards.
						#Extracting video to pngs in temporary folder
						#WARNING, mktmpdir() function must be runned before, for the tempdir variable!!
	global audioencoding
	print("\nExtracting audio from video...\n")
	extract_audio = "ffmpeg -i " + input_directory + "/" + str(video_name) + " -vn -c:a aac " + tempdir + "/audio.m4a"
	os.system(extract_audio)
	
		#Double checking audio file
	audioencoding = "-i " + tempdir + "/audio.m4a -c:a copy "
	if not os.path.exists(tempdir + "/audio.m4a"):
		audioencoding = ""
		
		
	print("\nExtracting all frames from video...\n")
	os.system("ffmpeg -i " + input_directory + "/" + video_name + " -r " + str(vidfps) + " " + color_settings_png + " " + tempinput + "/%08d.png")	

	'''
	Variable used outside function:
		- audioencoding = ffmpeg setting for getting audio back to the new file
	'''


def denoiserun():		#Denoise the images, it will also scale up the image x2, but ffmpeg will scale it back down.

	
	print("\nRunning SRMD to denoise the video")
	os.chdir("AIs/")
	SRMD_command = "./srmd-ncnn-vulkan -i " + tempinput + " -o " + tempoutput + " -n 8 -s 2"
	os.system(SRMD_command)

	shutil.rmtree(tempinput)
	os.rename(tempoutput, tempinput)
	os.mkdir(tempoutput)
	os.chdir("..")
	print("Finished running SRMD.\n")
	
	if (vidwidth <= 960 and vidheight <= 540) or (vidwidth <= 540 and vidheight <= 960):
		print("Keeping the scaled up images from the denoising process due to the original's low resolution\n")
	else:	
		print("Scaling down the temporary images to its original form")
		os.system("ffmpeg -i " + tempinput + "/%08d.png -vf \"scale=iw*0.5:ih*0.5\" " + tempoutput + "/%08d.png")
		shutil.rmtree(tempinput)
		os.rename(tempoutput, tempinput)
		os.mkdir(tempoutput)


def riferun(normal_crfvalue_in_string, uhd_crfvalue_in_string):
			#Estimating if the interpotalion is x2 or x4
	global vidfps_intered, crfvalue		
	extra_inter = False
	if vidfps < 50:				#Below 50
		print("\nThe video's FPS is below 50, so RIFE is going to run twice.")
		extra_inter = True
	elif vidfps > 50.00000000000001:	#Over 50
		print("\nThe video's FPS is over 50, so RIFE is going to run only once.")
		extra_inter = False


		#Estimating if RIFE needs UHD mode
		
	uhd = " -m rife-v3.1" 	#This displays nothing, but if it's over 1080p, it will add "-u"
	crfvalue = normal_crfvalue_in_string
	
	if (vidwidth >= 1921 and vidheight >= 1081) or (vidwidth >= 1081 and vidheight >= 1921):
		print("Ultra HD mode for RIFE is enabled.")
		uhd = " -u -m rife-v3.1"
		crfvalue = uhd_crfvalue_in_string
	else:
		print("Ultra HD mode for RIFE is disabled.")
		uhd = " -m rife-v3.1"
		crfvalue = normal_crfvalue_in_string
	
	
		#Running RIFE
	print("Running RIFE")
	os.chdir("AIs/")
	RIFE_command = "./rife-ncnn-vulkan -i " + tempinput + " -o " + tempoutput + uhd
	os.system(RIFE_command)
	
	if extra_inter == True:
		vidfps_intered = vidfps * 4
		print("Running RIFE for a second time")
		shutil.rmtree(tempinput)
		os.rename(tempoutput, tempinput)
		os.mkdir(tempoutput)
		
		os.system(RIFE_command)
		print("Finished running RIFE\n")
	elif extra_inter == False:
		vidfps_intered = vidfps * 2
		print("Finished running RIFE\n")
		
	os.chdir('..')
	print("The final framerate will be %s\n" % vidfps_intered)
	
	
	'''
	Variable used outside function:
		- vidfps_intered = number of frames per second for the new video
		- crfvalue = crf value for encoding
	'''

def videncode(input_directory, output_directory, video_name):
	os.system("ffmpeg -framerate " + str(vidfps_intered) + " -i " + tempoutput + "/%08d.png " + audioencoding + "-c:v libx265 -crf " + crfvalue + " -preset veryslow " + color_settings_vid + " " + output_directory + "/" + video_name[:-4] + "n.mp4")
	os.system("ffmpeg -i " + input_directory + "/" + video_name + " -i " + output_directory + "/" + video_name[:-4] + "n.mp4 -map 1 -c copy -map_metadata 0 -tag:v hvc1 " + output_directory + "/" + video_name[:-4] + ".mp4")
	os.remove(output_directory + "/" + video_name[:-4] + "n.mp4")


		
def inter_auto(input_directory, output_directory, temporary_directory, normal_crfvalue_in_string, uhd_crfvalue_in_string):
	
	check(input_directory)
	check(output_directory)

	numofvids = len(os.listdir(input_directory))

	if numofvids == 0:
		print("Since there's no files, the script is being terminated.")
		sys.exit(0)
	else:
		print("There are %s videos in the input directory." %numofvids)

	firstlist = os.listdir(input_directory)
	count = 0
	inlower = firstlist[count].lower()
	for numofvids in firstlist:	
		if inlower.endswith('.avi') and not inlower.startswith(".") or inlower.endswith('.mp4') and not inlower.startswith(".") or inlower.endswith('.mov') and not inlower.startswith(".") or inlower.endswith('.wmv') and not inlower.startswith(".") or inlower.endswith('.3gp') and not inlower.startswith(".") or inlower.endswith('.mpg') and not inlower.startswith(".") or inlower.endswith('.leotmv') and not inlower.startswith('.'):
		
				#Getting resolution and fps from video	
			getvidinfo(input_directory + "/" + firstlist[count], firstlist[count])

				#Checking and making temporary directory
			mktmpdir(temporary_directory)
			
				#Checking if video is more than 5 minutes, if so, it's seperated by 5 minutes
			if videodurationminutes > 2:
				newcdi = tempdir + '/vidinput'
				newcdo = tempdir + '/vidoutput'
				os.mkdir(newcdi)
				os.mkdir(newcdo)
				
				firstlistsuffix = pathlib.Path(input_directory + firstlist[count]).suffix
				os.system("ffmpeg -i " + input_directory + "/" + firstlist[count] + " -c:v copy -segment_time 00:02:00.00 -f segment -reset_timestamps 1 " + newcdi + "/%03d" + firstlistsuffix)
				anothernumofvids = len(os.listdir(newcdi))
				secondlist = (os.listdir(newcdi))
				secondlist.sort()
				count2 = 0
				
				print("\nExtracting audio from video...\n")
				extract_audio = "ffmpeg -i " + input_directory + "/" + str(firstlist[count]) + " -vn -c:a aac " + tempdir + "/audio.m4a"
				os.system(extract_audio)	
					#Double checking audio file
				audioencoding = "-i " + tempdir + "/audio.m4a -c copy -map 0:v -map 1:a "
				if not os.path.exists(tempdir + "/audio.m4a"):
					audioencoding = ""
				
				filelist = open("temporary_file.txt", "x")
				filelist.close()
				for anothernumofvids in secondlist:
					filelist = open("temporary_file.txt", "a")
					newfilelocation = "AIs/temp/vidoutput/" + secondlist[count2][:-4] + ".mp4"
					filelist.write("file '%s'\n" %newfilelocation)
					filelist.close()
					
					os.system("ffmpeg -i " + newcdi + "/" + secondlist[count2] + " -r " + str(vidfps) + " " + color_settings_png + " " + tempinput + "/%08d.png")
					if (vidwidth <= 720 and vidheight <= 480) or (vidwidth <= 480 and vidheight <= 720):
						denoiserun()
					else:
						print("The resolution is more than 480p, skipping denoise process...")
					riferun(normal_crfvalue_in_string, uhd_crfvalue_in_string)
					os.system("ffmpeg -framerate " + str(vidfps_intered) + " -i " + tempoutput + "/%08d.png -c:v libx265 -crf " + crfvalue + " -preset veryslow " + color_settings_vid + " " + newcdo + "/" + secondlist[count2][:-4] + ".mp4")
					
					shutil.rmtree(tempinput)
					shutil.rmtree(tempoutput)
					os.mkdir(tempinput)
					os.mkdir(tempoutput)
					count2 += 1

				
				os.system("ffmpeg -f concat -safe 0 -i temporary_file.txt -c copy " + output_directory + "/" + firstlist[count][:-4] + "a.mp4")
				os.system("ffmpeg -i " + output_directory + "/" + firstlist[count][:-4] + "a.mp4 " + audioencoding + " -c:v copy " + output_directory + "/" + firstlist[count][:-4] + "n.mp4")
				os.system("ffmpeg -i " + input_directory + "/" + firstlist[count] + " -i " + output_directory + "/" + firstlist[count][:-4] + "n.mp4 -map 1 -c copy -map_metadata 0 -tag:v hvc1 " + output_directory + "/" + firstlist[count][:-4] + ".mp4")
				os.remove(output_directory + "/" + firstlist[count][:-4] + "a.mp4")
				os.remove(output_directory + "/" + firstlist[count][:-4] + "n.mp4")
				shutil.rmtree(tempdir)
				os.remove("temporary_file.txt")
			else:
					
			
					#Extracting audio and decoding all frames
				vidextract(input_directory, firstlist[count])
					
				if (vidwidth <= 720 and vidheight <= 480) or (vidwidth <= 480 and vidheight <= 720):
					denoiserun()
				else:
					print("The resolution is more than 480p, skipping denoise process...")
				
					#Running RIFE
				riferun(normal_crfvalue_in_string, uhd_crfvalue_in_string)
				
					#Encoding interpolated frames with audio
				videncode(input_directory, output_directory, firstlist[count])
				
				shutil.rmtree(tempdir)
			
			count += 1

		elif inlower.startswith("."):
			print("Skipping files starting with a dot")
			count += 1
				

##Code
	


inter_auto(cdi, cdo, current_dir + '/AIs/temp', "19", "26")
