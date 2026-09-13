# Offline HuggingFace Cache

Populate this folder ONCE while online:

    python3 -c "from sentence_transformers import SentenceTransformer; 
    SentenceTransformer('clip-ViT-B-32')"
    mkdir -p models/hf_cache
    cp -R ~/.cache/huggingface/* models/hf_cache/

After this, the CLIP embedding model loads locally with zero internet.
