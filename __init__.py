import cv2
import numpy as np
from typing import  Iterable
from moviepy.editor import VideoClip ,VideoFileClip


def process(roi, size=3, range: Iterable = ((200, 200, 200), (255, 255, 255)),
            radius: int = 2, flags=cv2.INPAINT_TELEA,):
    x, y, w, h = roi
    KERNEL = np.ones((size, size), np.uint8)

    def process_data(frame: np.ndarray, *_, **__):
        #frame=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
        frame=frame.copy()
        cropped_img = frame[y:y+h, x:x+w]
        mask = cv2.inRange(cropped_img, *range)
        opening = cv2.dilate(mask, KERNEL)
        cropped_img = cv2.inpaint(cropped_img, opening, radius, flags)
        frame[y:y+h, x:x+w] = cropped_img
        return frame
    return process_data




class RemoveCaptionClip(VideoClip):
    def initialize(self, roi, size=3, range: Iterable = ((200, 200, 200), (255, 255, 255)),
                   radius: int = 2, flags=cv2.INPAINT_TELEA):
        org = self.make_frame
        processData = process(roi, size, range, radius, flags)
        self.make_frame = lambda t: processData(org(t))


class RemoveCaptionFileClip(VideoFileClip, RemoveCaptionClip):
    pass

