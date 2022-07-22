import cv2
import random
import numpy as np
from pycv2.tools import video_saver
from typing import Any, Iterable, Tuple


def crop_img_with_mouse(img,showcrosshair=False):
    roi=(0,0,0,0)
    while roi==(0,0,0,0):
        roi=cv2.selectROI("crop img with mouse",img,showCrosshair=showcrosshair,)
        cv2.destroyWindow("crop img with mouse")
        roi =int(roi[0]),int(roi[1]),int(roi[2]),int(roi[3])
    return roi

def process(savingPath,video,roi,size=3,range:Iterable=((200,200,200),(255,255,255)),
            radius:int=2,flags=cv2.INPAINT_TELEA,
            fourcc: Any = cv2.VideoWriter_fourcc("m", "p", "4", "v")
            , start_time: int = 0, end_time: float = float("inf"), fps_v: Any = None):
    x,y,w,h=roi
    KERNEL=np.ones((size,size),np.uint8)
    def process_data(frame:np.ndarray,*_,**__):
        cropped_img=frame[y:y+h,x:x+w]
        mask=cv2.inRange(cropped_img,*range)
        opening = cv2.dilate( mask,KERNEL)
        cropped_img=cv2.inpaint(cropped_img,opening,radius,flags)
        cv2.imshow("Mask",mask)
        cv2.imshow("opening",opening)
        frame[y:y+h,x:x+w]=cropped_img
        cv2.imshow("FRAME",frame)
        cv2.waitKey(1)
        return frame
    video_saver(savingPath,video,fourcc,start_time,end_time,fps_v,process_data)
    
