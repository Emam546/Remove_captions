from Remove_Caption import *
import random


def crop_img_with_mouse(img, showcrosshair=False):
    roi = (0, 0, 0, 0)
    while roi == (0, 0, 0, 0):
        roi = cv2.selectROI("crop img with mouse", img,
                            showCrosshair=showcrosshair,)
        cv2.destroyWindow("crop img with mouse")
        roi = int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3])
    return roi


# FILENAME="./[EgyBest].Deadpool.2.2018.BluRay.240p.x264.mp4"
FILENAME = r"G:\Videos\[EgyBest].Batman.V.Superman.Dawn.Of.Justice.2016.BluRay.240p.x264.mp4"
# FILENAME=r"D:\Projects\Remove_captions\[EgyBest].Deadpool.2.2018.BluRay.240p.x264.mp4"
FILENAME = r"G:\Videos\[EgyBest].Green.Book.2018.BluRay.240p.x264.mp4"
video = RemoveCaptionFileClip(FILENAME)
# FILENAME=r"D:\Projects\Remove_captions\[EgyBest].Deadpool.2.2018.BluRay.240p.x264.mp4"
savingpath = "./result.mp4"
dauration = video.reader.nframes/video.reader.fps
startTime = random.randint(0, int(dauration-(10*60)))
endTime = startTime+(0.5*60)

print("SELECTING WANTED REGION")
frame = video.get_frame(random.randint(0, int(video.reader.duration)))
frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
roi = crop_img_with_mouse(frame)
video.initialize(roi, size=8, radius=5, range=(
    (210, 210, 210), (255, 255, 255)))
#video: RemoveCaptionClip = video.subclip(startTime, endTime)
video.write_videofile(savingpath)
