import librosa
import numpy as np
import noisereduce as nr

def preprocess_audio(audio_file):
    audio, sr = librosa.load(audio_file, sr=None)
    audio = nr.reduce_noise(y=audio, sr=sr)
    audio = librosa.util.normalize(audio)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=52)
    mfccs = np.mean(mfccs.T, axis=0)
    mfccs = mfccs[None, :]
    
    return mfccs

def predict_from_features(model, features):
    return model.predict(np.array([features]))