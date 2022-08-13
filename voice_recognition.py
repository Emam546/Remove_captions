import os
from moviepy.editor import AudioClip, AudioFileClip, VideoFileClip
import speech_recognition as sr
from moviepy.audio.io.AudioFileClip import FFMPEG_AudioReader
import audioop
import numpy as np
import io
from datetime import datetime, timedelta
from pycv2.tools import createProgressBar
listener = sr.Recognizer()
ENCODING="utf-8"

class AudioFileStream(object):
    def __init__(self, audio_reader, channels,
                 sampleWidth, duration, fps):
        # an audio file object (e.g., a `wave.Wave_read` instance)
        self.audio_reader = audio_reader
        self.channels = channels
        self.sampleWidth = sampleWidth
        self.numFrames = duration*fps
        self.currentFrame = 1

    def read(self, size=-1):
        buffer = self.audio_reader()
        if not isinstance(buffer, bytes):
            buffer = b""  # workaround for https://bugs.python.org/issue24608
        # workaround for https://bugs.python.org/issue12866
        if self.channels != 1:  # stereo audio
            # convert stereo audio data to mono
            buffer = audioop.tomono(buffer, self.sampleWidth, 1, 1)
        self.currentFrame += (len(buffer)/self.channels)
        if(self.currentFrame >= self.numFrames):
            print("OUT OF FRAMES")
            return b""
        return buffer


class StrWriter(io.FileIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentChunk = 0

    def add_time(self, sentence:str, startt: datetime, endt: datetime):
        time_str = bytes(f"{str(startt.time())} --> {str(endt.time())}\n",ENCODING)

        self.write(bytes(str(self.currentChunk)+"\n",ENCODING))
        self.write(time_str)
        self.write(bytes(sentence+"\n",ENCODING))
        self.currentChunk += 1


class CutOut(AudioFileClip, sr.AudioSource):
    def __init__(self, filename, buffersize=200000, nbytes=2, fps=44100):
        super().__init__(filename, buffersize, nbytes, fps)

        self.SAMPLE_RATE = self.fps
        self.CHUNK = 4096

        self.SAMPLE_WIDTH = self.reader.nbytes
        self.FRAME_COUNT = self.reader.nframes
        self.DURATION = self.FRAME_COUNT / float(self.SAMPLE_RATE)

    def __enter__(self):
        self.reader.initialize(self.start)
        L = self.nchannels*self.CHUNK*self.reader.nbytes
        self.stream = AudioFileStream(lambda: self.reader.proc.stdout.read(
            L), self.nchannels, self.SAMPLE_WIDTH, self.duration, self.fps,)
        return super().__enter__()

    def getSubtitles(self, filename=None):
        lastTime = orgTime = datetime(100, 1, 1, 0, 0, 0)+timedelta(seconds=self.start)
        if not filename:
            filename = os.path.splitext(self.filename)[0]+".srt"
        progressBar=createProgressBar(total=self.duration)
        currentSecond=0
        with StrWriter(filename, "w") as f:
            with self as audioFile:
                while True:
                    res = ""
                    try:
                        print("START_SECONDS: ",currentSecond/60)
                        data: sr.AudioData = listener.listen(
                            audioFile, timeout=1,)
                        if self.stream.currentFrame>self.stream.numFrames:
                            break
                        currentSecond = int(self.stream.currentFrame*(1/self.fps))
                        print("SENDING DATA :",currentSecond/60)
                        res = listener.recognize_google(data)
                    except sr.UnknownValueError:
                        print("unknown audio")
                    except sr.WaitTimeoutError:
                        print("time out")
                    except Exception as e:
                        print(str(e))
                    time = orgTime+timedelta(seconds=currentSecond)
                    if res:
                        print("add subtitle")
                        f.add_time(res, lastTime, time)
                    progressBar(currentSecond)
                    lastTime = time
        print("\n finished")


def main():
    # 'wav':  {'type':'audio', 'codec':['pcm_s16le', 'pcm_s24le', 'pcm_s32le']},
    FILENAME = r"./testing/sample_film.mp4"
    with CutOut(FILENAME) as audioFile:
        audioFile.getSubtitles()
        #print(audioFile.reader.nframes)
    # CutOut(FILENAME).write_speakingFile("new_file.mp3")


if __name__ == "__main__":
    main()
