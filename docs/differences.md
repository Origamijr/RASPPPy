# Differences between RASPPPy and Pure Data

Admittedly I'm not a Pure Data expert, so there's probably more differences than what I've considered, but these are the differences I've consciously implemented. I am aware MaxMSP exists, however as a poor student I haven't gotten myself to purchase a license to use it extensively beyond just the runtime, so I can't really make any educated comparisons to MaxMSP.

## Data Types

Pure data has some pretty defined data types (bang, float, symbol, list, pointer, etc...), but behaves relatively dynamically. RASPPPy is a bit more pythonic, being a bit more dynamically typed. The only types in RASPPPy are defined based on the behaviors of if and when data is propagated from one object to another. As such, there are only three types:

- Bang: Represents a pure event without any data
- Message: Any data that is processed immediately
- Signal: Any data that is processed every DSP iteration

Both messages and signals can really propagate any type, and it's really the receiving object's responsibility to do with that data what it should. The only checking that is done is on the types of wires (listed above), but no checks are performed on the data itself. For instance, the "add" object won't check for a number, and will simply do whatever python already sets the add operation to do. Would this have any consequences? idk, I hope not. I'll trust users are responsible programmers.

## Everything is an Object

Basically every entity that can be placed in a patch is an object. Even a patch itself is an extension of an object. Under this notion, all objects are serializable into a json with a common set of properties, and be initialized in the editor by typing the name of the object (or an alias). This includes objects that couldn't be initialized this way in Pure Data like the Number, Message, and Bang (note that a bang object exists in Pd already, so I just merged them into one implementation).

# Audio Block Size

The default audio block size in Pure Data is 64 with sample rate 44100 Hz. For RASPPPy, the default block size is 512 with sample rate 48000 Hz. This is of course configurable, but a larger block size is likely required to achieve good real-time performance. The backend for signal processing is handled by numpy, which if we want to take advantage of numpy's superior math performance compared to standard python, we ought to use a sizable block size. This, of course, incurs some latency, and restrictions on the minimum amount of delay for delay lines and send~ and receive blocks. However, the block size being ~10ms shouldn't cause any notable difference for most applications. There does, however, seem to be some noticeable delay in the audio relative to input, which I don't think is caused by the block size. I'll look into this if it's an issue, but I'm not sure if there's anything I can do about it.