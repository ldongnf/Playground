import cv2
import time

# caputre a image
camera_port = 0
camera = cv2.VideoCapture(camera_port)
time.sleep(0.1)
return_value, image = camera.read()
cv2.imwrite("output.png", image)
camera.release()

# record a video
camera = cv2.VideoCapture(camera_port)
w = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
h = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

fps = 15.0
record_time = 2

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4',fourcc, fps, (int(w),int(h)))
start_time = time.time()
while camera.isOpened() and time.time() - start_time < record_time:
	return_value, image = camera.read()
	out.write(image)
camera.release()
out.release()
