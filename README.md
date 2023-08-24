# RASPPPy (Real-time Audio and Signal Processing Patcher for Python)

A toolkit for creating and running audio (and potentially other multimedia) real-time applications created in Python.

With the rapid developments in audio processing (ASR, TTS, SV, VC, etc), we now have access to many more powerful components that can be used in larger application. However, creating applications using these new models can take long times to prototype for different applications. In the realm of audio, (Pure Data)[https://puredata.info/] allows for the rapid prototyping of various audio applications, but interfacing Pd with these newer audio processing tools is quite difficult, since most newer tools are developed and implemented with python and pytorch.

RASPPPy is being developed to try to emulate the rapid prototyping for audio applications of Pure Data, while staying in a python environment for easier integration of newer models. Being written in only python, there are some severe limitations on DSP capabilities, but it's of workable quality for prototypes. The pure python codebase is not a deliberate design decision, but moreso a skill issue on my part as I would have like to have C/C++ parts, but I don't really understand how to get the languages to interface.

