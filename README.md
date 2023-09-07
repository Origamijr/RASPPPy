# RASPPPy (Real-time Audio Signal Processing Patcher for Python)

A visual programming language for creating and running audio (and potentially other multimedia) real-time applications created in Python.

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

```
python main.py
```
the `config.toml` should be in the same directory level

## Building

Admitedly a mess, will write up later. Not completely standalone yet, need to figure out how to build electron along with eel using pyinstaller (https://github.com/python-eel/Eel/issues/57#issuecomment-426069269), but that's low priority

## Features

### Implemented
- saving and loading patches
- some basic math and dsp
- audio input/output
- some advanced objects for VAD and ASR
- Basic GUI to play patches

### Planned for near future
- Dynamically loading objects from a specified directory for easy extension
- Built in models for TTS, and VC
- Actual GUI editor
- Replicating most of the Pd library of basic blocks
- Refining installation/execution process
- Building into a standalone application

### Planned for far future
- Faster dsp backend (may or may not be possible)
- Pytorch library of objects for possibly training within the interface
- Wider Multimedia capabilities (e.g. Video using OpenCV, WebGL or Live2D would be cool too)