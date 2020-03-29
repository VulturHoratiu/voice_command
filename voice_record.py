#!/usr/bin/python

import sys
import getopt
import random
import subprocess
import deepspeech
import wave
import numpy
from pathlib import Path
from gtts import gTTS

base = '/root/Sw/voice_command/webcrawler/tutorial/tutorial'

def readjoke(filename):
    f = Path("%s/jokes-%s" % (base, filename))
    if (not f.is_file()):
        print("file %s not found" % filename)

    with open("%s/jokes-%s" % (base, filename)) as f:
        content = f.readlines()
        joke = content[random.randint(0, len(content))]
        return joke

def execute(command):
    if not command:
        subprocess.call("mpg123 unknown.mp3", shell = True)
        return

    joke = readjoke('dad')
    print(joke)
    tts = gTTS(joke)
    tts.save('joke.mp3')
    subprocess.call("mpg123 joke.mp3", shell = True)
    os.remove("joke.mp3")

def main():
    #subprocess.call("arecord -D hw:0,0 -f cd -t wav -d 3 -r 44100 test.wav", shell = True)
    subprocess.call("arecord -D hw:3,0 -f cd -t wav -d 3 -r 16000 --channels 1 test.wav", shell = True)

    model_file_path = '/root/Downloads/deepspeech-0.6.0-models/output_graph.pbmm'
    beam_width = 500
    model = deepspeech.Model(model_file_path, beam_width)

    lm_file_path = '/root/Downloads/deepspeech-0.6.0-models/lm.binary'
    trie_file_path = '/root/Downloads/deepspeech-0.6.0-models/trie'
    lm_alpha = 0.75
    lm_beta = 1.85
    model.enableDecoderWithLM(lm_file_path, trie_file_path, lm_alpha, lm_beta)

    #filename = '/root/Downloads/audio/8455-210777-0068.wav'
    filename = '/root/Sw/voice_command/test.wav'
    w = wave.open(filename, 'r')
    rate = w.getframerate()
    frames = w.getnframes()
    buffer = w.readframes(frames)

    print(rate)
    print(model.sampleRate())

    data16 = numpy.frombuffer(buffer, dtype=numpy.int16)
    text = model.stt(data16)
    execute(text)

main()

