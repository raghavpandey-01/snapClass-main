from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import io
import streamlit as st
import librosa


@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()

def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()

# audio_bytes = raw file content in memory
# io.BytesIO(audio_bytes) = “pretend these bytes are a file”


# “If I already have audio_bytes, why not pass it directly to the encoder?”

# Because the encoder does not want raw file-format bytes like WAV/MP3 headers
# It wants the actual waveform signal.
# So first we must decode the file.

        audio, sr = librosa.load(io.BytesIO(audio_bytes))
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        st.error('Voice recog error')
        return None

#sample rate means how many audio samples recorded per second
# waveform : is audio signal represented as amplitude over time

def identify_speaker(new_embedding, candidate_dict, threshold=0.65):
    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidate_dict.items():
        if stored_embedding:
            similarity = np.dot(new_embedding, stored_embedding)
            if similarity > best_score:
                best_score = similarity
                best_sid = sid

    if best_score>= threshold:
        return best_sid, best_score
    
    return None, best_score

def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    try:

        encoder = load_voice_encoder()

        audio,sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments = librosa.effects.split(audio, top_db=30)

        identified_results = {}

        for start,end in segments:
            if(end-start) < sr*0.5:
                continue
            segmented_audio = audio[start:end]
            wav = preprocess_wav(segmented_audio)
            embedding = encoder.embed_utterance(wav)

            sid, score = identify_speaker(embedding , candidates_dict, threshold)

            if sid:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score

        return identified_results
    
    except Exception as e:
        st.error('Bulk processor error')

