import os,sys
sys.path.append(os.path.abspath("."))
from voice_recognition import CutOut
def main():
    FILENAME = r"G:\Videos\hd\[EgyBest].The.Gray.Man.2022.WEB-DL.720p.x264no_caption.mp4"
    with CutOut(FILENAME) as audioFile:
        audioFile.getSubtitles(phrase_time_limit=3)
if __name__ == "__main__":
    main()