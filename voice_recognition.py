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
        self.write(bytes(sentence+"\n\n",ENCODING))
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

    def getSubtitles(self, outName=None,phrase_time_limit=30,timeout=1,fix_time=False):
        lastTime = orgTime = datetime(100, 1, 1, 0, 0, 0)+timedelta(seconds=self.start)
        if not outName:
            outName = os.path.splitext(self.filename)[0]+".srt"
        progressBar=createProgressBar(total=self.duration)
        currentSecond=0
        old_res=""
        old_data=b""
        with StrWriter(outName, "w") as f:
            with self as audioFile:
                while True:
                    
                    try:
                        data: sr.AudioData = listener.listen(
                            audioFile, timeout=timeout,phrase_time_limit=phrase_time_limit)
                        data.frame_data=old_data+data.frame_data
                        if self.stream.currentFrame>self.stream.numFrames:
                            break
                        res:str = listener.recognize_google(data)
                        if fix_time and res and res.replace(" ","") !=old_res.replace(" ",""):
                            old_res+=res+" "
                            old_data=data.frame_data
                            continue
                    except sr.UnknownValueError:
                        pass
                    except sr.WaitTimeoutError:
                        pass
                    except Exception as e:
                        print(str(e))
                    if (fix_time): 
                        res = old_res
                        
                    currentSecond = int(self.stream.currentFrame*(1/self.fps))
                    time = orgTime+timedelta(seconds=currentSecond)
                    if res:
                        f.add_time(res, lastTime, time)
                    old_data=b""
                    old_res=""
                    progressBar(currentSecond)
                    lastTime = time
        print("\n finished")



