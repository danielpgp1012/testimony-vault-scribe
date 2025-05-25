import os
import io
import hashlib
from typing import Tuple, Optional
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

def get_audio_metadata(file_bytes: bytes, file_name: str = "audio") -> Tuple[Optional[int], Optional[str]]:
    """
    Extract basic audio metadata and generate a fingerprint hash from file bytes.
    
    Returns:
        Tuple containing (duration_ms, file_hash)
        Any value can be None if extraction fails
    """
    try:
        # Create a file-like object from the bytes
        file_obj = io.BytesIO(file_bytes)
        
        # Get file extension from name
        ext = os.path.splitext(file_name)[1].lower()
        if not ext:
            ext = ".mp3"  # Default
            
        # Extract audio metadata using pydub
        audio = AudioSegment.from_file(file_obj, format=ext.lstrip('.'))
        
        # Generate hash of the first 30 seconds (or whole file if shorter)
        # This helps identify duplicate content even if filenames are different
        segment_to_hash = audio[:min(30000, len(audio))]
        segment_hash = hashlib.md5(segment_to_hash.raw_data).hexdigest()
        
        return len(audio), segment_hash
    except Exception as e:
        print(f"ERROR getting metadata: {e}")
        return None, None
        
def calculate_audio_hash(file_bytes: bytes) -> Optional[str]:
    """Calculate MD5 hash of audio file bytes"""
    try:
        return hashlib.md5(file_bytes).hexdigest()
    except Exception as e:
        print(f"ERROR calculating file hash: {e}")
        return None 