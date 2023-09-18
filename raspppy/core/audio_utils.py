from core.config import config
CONFIG = config('audio')

match CONFIG['analysis_lib']:
    case 'librosa':
        import librosa
    case 'audioflux':
        import audioflux
    case _:
        import librosa
        import audioflux


def resample_librosa(x, orig_sr, target_sr):
    return librosa.resample(x, orig_sr=orig_sr, target_sr=target_sr)

def resample_audioflux(x, orig_sr, target_sr):
    return audioflux.resample(x, orig_sr, target_sr)

match CONFIG['analysis_lib']:
    case 'librosa':
        resample = resample_librosa
    case _:
        resample = resample_audioflux