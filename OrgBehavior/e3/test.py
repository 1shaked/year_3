# %%
import wave
# from scipy.io import wavfile
import os
import struct
import heapq
from collections import defaultdict
import sys
import os
import wave
import time



# %%
files = os.listdir('data')
# Open the .wav file
with wave.open(f"data/{files[0]}", "rb") as wav_file:
    # Extract audio properties
    n_channels = wav_file.getnchannels()
    sample_width = wav_file.getsampwidth()
    frame_rate = wav_file.getframerate()
    n_frames = wav_file.getnframes()
    duration = n_frames / frame_rate
    audio_frames = wav_file.readframes(n_frames)

    print(f"Channels: {n_channels}")
    print(f"Sample Width: {sample_width} bytes")
    print(f"Frame Rate (Sample Rate): {frame_rate} Hz")
    print(f"Number of Frames: {n_frames}")
    print(f"Duration: {duration:.2f} seconds")

# %%
audio_frames

# %%
# Define the format string for struct.unpack
fmt = f"<{n_frames * n_channels}{'h' if sample_width == 2 else 'B'}"
# Convert binary data to numerical audio samples
audio_samples_struct = struct.unpack(fmt, audio_frames)
# audio_frames.decode('utf-8')

# %%
print(audio_samples_struct[:10])  # Print first 10 audio samples


# %% [markdown]
# ## Compression algorithms

# %%
def run_length_encoding_bytes(data):
    encoded = []
    count = 1

    for i in range(1, len(data)):
        if data[i] == data[i - 1]:
            count += 1
        else:
            encoded.append((data[i - 1], count))
            count = 1
    encoded.append((data[-1], count))  # Add the last group

    return encoded

def rle_to_bytes(encoded):
    byte_data = b""
    for byte, count in encoded:
        byte_data += struct.pack("B", byte) + struct.pack("I", count)
    return byte_data
# run_length_encoding_bytes(audio_samples_struct)


# %%
class HuffmanNode:
    def __init__(self, byte, freq):
        self.byte = byte
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree_bytes(data):
    freq = defaultdict(int)
    for byte in data:
        freq[byte] += 1

    heap = [HuffmanNode(byte, freq) for byte, freq in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]

def build_codes_bytes(node, prefix=b"", code_map={}):
    if node is None:
        return
    if node.byte is not None:
        code_map[node.byte] = prefix
    build_codes_bytes(node.left, prefix + b"0", code_map)
    build_codes_bytes(node.right, prefix + b"1", code_map)
    return code_map

def huffman_encoding_bytes(data):
    root = build_huffman_tree_bytes(data)
    codes = build_codes_bytes(root)
    encoded_data = b"".join(codes[byte] for byte in data)
    return encoded_data, codes

def huffman_to_bytes(encoded_bits):
    byte_data = int(encoded_bits, 2).to_bytes((len(encoded_bits) + 7) // 8, byteorder="big")
    return byte_data

# # Example usage
encoded, codes = huffman_encoding_bytes(audio_frames)
bytes_data = huffman_to_bytes(encoded)
print(f"Encoded Data (truncated): {encoded[:64]}")  # Print first 64 bits
print(f"bytes_data {bytes_data}")  # Print first 64 bits
print(f"Codes: {dict(codes)}")

# %%
def lzw_compression_bytes(data):
    dictionary = {bytes([i]): i for i in range(256)}
    current_bytes = b""
    compressed = []
    next_code = 256

    for byte in data:
        combined = current_bytes + bytes([byte])
        if combined in dictionary:
            current_bytes = combined
        else:
            compressed.append(dictionary[current_bytes])
            dictionary[combined] = next_code
            next_code += 1
            current_bytes = bytes([byte])

    if current_bytes:
        compressed.append(dictionary[current_bytes])

    return compressed

# def lzw_to_bytes(encoded):
#     byte_data = b"".join(struct.pack("H", code) for code in encoded)
#     return byte_data

def lzw_to_bytes(encoded):
    # Use "I" for unsigned 32-bit integers if values exceed 65,535
    max_code = max(encoded)
    if max_code <= 65535:
        # Use unsigned short (2 bytes)
        byte_data = b"".join(struct.pack("H", code) for code in encoded)
    else:
        # Use unsigned int (4 bytes)
        byte_data = b"".join(struct.pack("I", code) for code in encoded)
    return byte_data


# Example usage
compressed = lzw_compression_bytes(audio_frames)
print(compressed)  # Print first 10 compressed codes

# %%
def compression_rate(original, compressed):
    return len(compressed) / len(original)

# %%
# Example with a string
size = sys.getsizeof(compressed)
print(f"Size of the string: {size} bytes")  # Includes overhead for Python object

# Example with a list
# compressed = lzw_compression_bytes(audio_frames)
size = sys.getsizeof(bytes_data)
print(f"Size of the list: {size} bytes")

# %% [markdown]
# ## testing and create graph

# %%


def process_audio_files(data_folder):
    results = []
    files = [f for f in os.listdir(data_folder) if f.endswith(".wav")]
    len_files = len(files)
    for i,file_name in enumerate(files):
        print('file',i+1,'/',len_files)
        filepath = os.path.join(data_folder, file_name)
        print(f"Processing file: {filepath}")
        
        # Read WAV file
        with wave.open(filepath, "rb") as wav_file:
            frame_rate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            duration = n_frames / frame_rate
            audio_frames = wav_file.readframes(n_frames)
        
        # original_size = len(audio_frames)
        original_size = sys.getsizeof(audio_frames)

        # Test each compression algorithm
        file_results = {
            "file": file_name,
            "original_size": original_size,
            "duration": duration,
        }

        # Run Length Encoding
        start_time = time.time()
        rle_encoded= run_length_encoding_bytes(audio_frames)
        rle_time = time.time() - start_time
        bytes_rle = rle_to_bytes(rle_encoded)
        rle_compressed_size = sys.getsizeof(bytes_rle)
        file_results["rle_compressed_size"] = rle_compressed_size
        file_results["rle_time"] = rle_time

        # Huffman Coding
        start_time = time.time()
        huffman_encoded, huffman_codes = huffman_encoding_bytes(audio_frames)
        bytes_data = huffman_to_bytes(huffman_encoded)
        huffman_compressed_size = sys.getsizeof(bytes_data)
        # huffman_compressed_size = len(huffman_encoded) // 8
        huffman_time = time.time() - start_time
        file_results["huffman_compressed_size"] = huffman_compressed_size
        file_results["huffman_time"] = huffman_time

        # Lempel-Ziv-Welch
        start_time = time.time()
        lzw_compressed = lzw_compression_bytes(audio_frames)
        lzw_compressed_bytes = lzw_to_bytes(lzw_compressed)
        lzw_compressed_bytes_size = sys.getsizeof(lzw_compressed_bytes)
        lzw_time = time.time() - start_time
        file_results["lzw_compressed_size"] = lzw_compressed_bytes_size
        file_results["lzw_time"] = lzw_time

        # Append results for the file
        results.append(file_results)

    return results

# Example Usage
data_folder = "data"  # Replace with your data folder path
results = process_audio_files(data_folder)
import pandas as pd
import matplotlib.pyplot as plt
df = pd.DataFrame(results)
df.to_csv("audio_compression_results.csv", index=False)

# # %%
# # Calculate averages
# avg_compression_size = {
#     "RLE": df["rle_compressed_size"].mean(),
#     "Huffman": df["huffman_compressed_size"].mean(),
#     "LZW": df["lzw_compressed_size"].mean(),
# }
# avg_compression_time = {
#     "RLE": df["rle_time"].mean(),
#     "Huffman": df["huffman_time"].mean(),
#     "LZW": df["lzw_time"].mean(),
# }

# # %%

# # Plot 1: Average Compression Size
# plt.bar(avg_compression_size.keys(), avg_compression_size.values())
# plt.title("Average Compression Size per Algorithm")
# plt.ylabel("Size (Bytes)")
# plt.xlabel("Algorithm")
# plt.show()

# # %%
# # Plot 2: Average Compression Time
# plt.bar(avg_compression_time.keys(), avg_compression_time.values())
# plt.title("Average Compression Time per Algorithm")
# plt.ylabel("Time (Seconds)")
# plt.xlabel("Algorithm")
# plt.show()


# # %%


# # %%


# # %%


# # %%


# # %%


# # %%



