import torch
import numpy as np
import torch.nn.functional as F
import uuid

from resemblyzer import VoiceEncoder
import numpy as np



def embed_pcm(pcm: bytes) -> np.ndarray:
    # Convert PCM bytes to float array [-1,1]
    
    return embedding 

class SpeakerEmbedder:
    def __init__(self, chunk_size: int, sample_rate: int):
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.encoder = VoiceEncoder()
        self.buffer = []
        self.samples_collected = 0
        self.conclusion = None
        self.embedding_map = dict()
        self.equivalance_threshold = 0.7
        self.current_embedding = None

    def speaker_conclusion(self, emb1 = None):
        if not emb1:
            if self.current_embedding is not None:
                emb1 = self.current_embedding
            else:
                return None
        for owner, emb2 in self.embedding_map.items():
            print(f"Checking {owner}")
            similarity = self.embedding_equals_embedding(emb1, emb2)
            if similarity > self.equivalance_threshold:
                self.embedding_map[owner] = emb2
                print(f"{owner} = TRUE!")
                return owner
            print(f"{owner} = FALSE! ({similarity})")
        new_owner = str(uuid.uuid4())
        self.embedding_map[new_owner] = emb1
        return new_owner

    def embedding_equals_embedding(self, emb1, emb2):
        emb1 = emb1 / np.linalg.norm(emb1)
        emb2 = emb2 / np.linalg.norm(emb2) 
        sim = np.dot(emb1, emb2)   
        print(f"Comparing {emb1} to {emb2} is {sim}")
        return sim

    def embed(self, pcm_bytes: bytes):
        """
        pcm_bytes: raw int16 mono PCM from PyAudio stream.read()
        """
        audio_int16 = np.frombuffer(pcm_bytes, dtype=np.int16)
        audio_float = audio_int16.astype(np.float32) / 32768.0

        # Compute embedding
        embedding = self.encoder.embed_utterance(audio_float)
        self.current_embedding = embedding
    
    def collect_buffer(self):
        full_audio = np.concatenate(self.buffer)
        try:
            self.embed(full_audio.tobytes())
            self.buffer = []
            self.samples_collected = 0
        except Exception as e:
            print(f"Could not embed voice: {e}")
            

    def add_chunk(self, pcm_bytes):
        audio_np = np.frombuffer(pcm_bytes, dtype=np.int16)
        self.buffer.append(audio_np)
        self.samples_collected += len(audio_np)
        return None
        if self.samples_collected >= self.sample_rate:  # 1 second
            print(f"Buffer bigenough - calculating speaker...")
            self.collect_buffer()
            

        