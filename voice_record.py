#!/usr/bin/python

import sys
import getopt
import random
import subprocess
import deepspeech
import wave
import numpy
import argparse
from pathlib import Path
from gtts import gTTS

base = '/root/Sw/voice_command/webcrawler/tutorial/tutorial'
thresh = 10.0

def readjoke(filename):
    f = Path("%s/jokes-%s" % (base, filename))
    if (not f.is_file()):
        print("file %s not found" % filename)

    with open("%s/jokes-%s" % (base, filename)) as f:
        content = f.readlines()
        joke = content[random.randint(0, len(content))]
        return joke

def run_command(command):
    if not command:
        subprocess.call("mpg123 unknown.mp3", shell = True)
        return

    joke = readjoke('dad')
    print(joke)
    tts = gTTS(joke)
    tts.save('joke.mp3')
    subprocess.call("mpg123 joke.mp3", shell = True)
    os.remove("joke.mp3")

def decode_wav(filename):
    #filename = '/root/Downloads/audio/8455-210777-0068.wav'
    #filename = '/root/Sw/voice_command/test.wav'

    w = wave.open(filename, 'r')
    rate = w.getframerate()
    frames = w.getnframes()
    buffer = w.readframes(frames)

    print(rate)

    data16 = numpy.frombuffer(buffer, dtype=numpy.int16)
    return data16

def record():
    subprocess.call("arecord -D hw:0,0 -f cd -t wav -d 3 -r 44100 test.wav", shell = True)
    #subprocess.call("arecord -D hw:3,0 -f cd -t wav -d 3 -r 16000 --channels 1 test.wav", shell = True)

def just_noise(filename):
    subprocess.call("sox test.wav -n stats -s 16 2>&1 | awk '/^Max level/ {print $3}' > stats", shell = True)
    with open("stats") as f:
        content = f.readlines()
        if float(content[0]) < thresh:
            return True

    return False

def prepare_model():
    model_file_path = '/root/Downloads/deepspeech-0.6.0-models/output_graph.pbmm'
    beam_width = 500
    model = deepspeech.Model(model_file_path, beam_width)

    lm_file_path = '/root/Downloads/deepspeech-0.6.0-models/lm.binary'
    trie_file_path = '/root/Downloads/deepspeech-0.6.0-models/trie'
    lm_alpha = 0.75
    lm_beta = 1.85
    model.enableDecoderWithLM(lm_file_path, trie_file_path, lm_alpha, lm_beta)

    return model

def prepare_argparse():
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('--continuous', action='store_true',
                        help='continous monitoring')
    parser.add_argument('--thresh', type=float, help='threshold')
    return parser

def main():
    parser = prepare_argparse()
    model = prepare_model()

    args = parser.parse_args()

    while True:
        record()

        if just_noise('test.wav'):
            continue

        data16 = decode_wav('test.wav')
        text = model.stt(data16)
        run_command(text)

        if not args.continuous:
            break

main()

