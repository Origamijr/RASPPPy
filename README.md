# RASPPPy (Real-time Audio and Signal Processing Patcher for Python)

A toolkit for creating and running audio (and potentially other multimedia) real-time applications created in Python.

With the rapid developments in audio processing (ASR, TTS, SV, VC, etc), we now have access to many more powerful components that can be used in larger application. However, creating applications using these new models can take long times to prototype for different applications. In the realm of audio, [Pure Data](https://puredata.info/) allows for the rapid prototyping of various audio applications, but interfacing Pd with these newer audio processing tools is quite difficult, since most newer tools are developed and implemented with python and pytorch.

RASPPPy is being developed to try to emulate the rapid prototyping for audio applications of Pure Data, while staying in a python environment for easier integration of newer models. Being written in only python, there are some severe limitations on DSP capabilities, but it's of workable quality for prototypes. The pure python codebase is not a deliberate design decision, but moreso a skill issue on my part as I would have like to have C/C++ parts, but I don't really understand how to get the languages to interface.

## Installation

First install [pytorch](https://pytorch.org/) using an appropriate method.

```
pip install -r requirements.txt
```
Adjust paths and settings in `config.toml` as necessary.

Installation is still very primitive, and I'll get that working in the future.

## Running

IN PROGRESS

## Features

### Implemented
- saving and loading patches
- some basic math and dsp
- audio input/output

### Planned for near future
- Built in models for VAD, ASR, TTS, and VC (also maybe Llama as an extension)
- GUI (looking into Flask for a web interface)
- Replicating most of the Pd library of basic blocks
- Refining installation/execution process

### Planned for far future
- Faster dsp backend (may or may not be possible)
- Pytorch library of objects for possibly training within the interface
- Wider Multimedia capabilities (e.g. Video using OpenCV)