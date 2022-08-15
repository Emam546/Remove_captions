from voice_recognition import CutOut
def main():
    FILENAME = r"./testing/sample_film.mp4"
    with CutOut(FILENAME).subclip(4*60) as audioFile:
        audioFile.getSubtitles(phrase_time_limit=3)
if __name__ == "__main__":
    main()