# About RASPPPy

RASPPPy is written with a python backend and a javascript frontend, making it entirely dynamic. This enables easily creating and integrating new types of objects without the need to compile.

This is NOT meant to be a performant environment to build applications upon (although that's what I'll be personally doing). If you're just doing audio stuff, Pure Data is more performant. If you already have an application in mind with technologies determined, better to just write that as it's own application and avoid the overhead of RASPPPy. 

Being written in only python, there are some severe limitations on DSP capabilities, but it's of workable quality for prototypes. The pure python codebase is not a deliberate design decision, but moreso a skill issue on my part as this would probably benefit to have C/C++ parts.

This library is being written by just me (Kevin Huang) in my free time.