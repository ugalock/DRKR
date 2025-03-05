# app/tasks/research_processing.py

from datetime import datetime
import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from celery import Celery, chord, group
from sqlalchemy import select, func
import openai
from pinecone import Pinecone
import nltk
from nltk.tokenize import sent_tokenize
import logging
import redis
from redis.exceptions import LockError
import hashlib

from app.config import settings
from app.models import (
    DeepResearch, 
    ResearchChunk, 
    ResearchSummary, 
    ResearchSource, 
    DomainCoOccurrence
)
from app.db import get_db_sync

# Configure logging
logger = logging.getLogger(__name__)

CELERY_BROKER_URL = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/2"
CELERY_RESULT_BACKEND = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/1"
# Initialize Celery
app = Celery('research_tasks', 
             broker=CELERY_BROKER_URL,
             backend=CELERY_RESULT_BACKEND)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_time_limit=1800,
    worker_concurrency=4,
)

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

# Initialize Pinecone
pc = Pinecone(
    api_key=settings.PINECONE_API_KEY
)
index = pc.Index(host=f"https://{settings.PINECONE_INDEX_NAME}{settings.PINECONE_HOST_SUFFIX}")

# Download NLTK resources if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# Initialize Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True  # For string keys/values
)

# Redis utility functions:
def get_processing_lock(key, timeout=60):
    """Acquire a distributed lock to prevent parallel processing of the same item"""
    lock_key = f"lock:{key}"
    return redis_client.set(lock_key, "1", nx=True, ex=timeout)

def set_task_status(research_id, task_name, status, metadata=None):
    """Store task status in Redis"""
    key = f"research:{research_id}:task:{task_name}"
    data = {"status": status, "updated_at": datetime.now().isoformat()}
    if metadata:
        data.update(metadata)
    redis_client.hset(key, mapping=data)
    redis_client.expire(key, 86400)  # Expire after 24 hours

def cache_embedding(text_hash, embedding, ttl=86400*7):
    """Cache embeddings to avoid redundant API calls"""
    if not embedding:
        return
    key = f"embedding:{text_hash}"
    redis_client.set(key, json.dumps(embedding), ex=ttl)
    
def get_cached_embedding(text_hash):
    """Retrieve cached embedding"""
    key = f"embedding:{text_hash}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

# Main entry point task
@app.task(name="research.process_data")
def process_research_data(research_id: int):
    """
    Main task that orchestrates the processing of research data.
    Uses Celery chords to ensure tasks run in the correct sequence.
    """
    # Try to get a lock to prevent duplicate processing
    if not get_processing_lock(f"research:{research_id}"):
        logger.warning(f"Research ID {research_id} is already being processed")
        return {"status": "already_processing", "research_id": research_id}
    
    # Set initial status
    set_task_status(research_id, "process_data", "started")
    logger.info(f"Starting processing for research ID: {research_id}")
    
    # All independent tasks in a single group
    parallel_tasks = group(
        chunk_prompt.s(research_id),
        chunk_report.s(research_id),
        generate_document_embeddings.s(research_id),
        create_summaries.s(research_id),
        process_domain_cooccurrences.s(research_id)
    )
    parallel_tasks.apply_async()
    
    return {
        "status": "processing_started", 
        "research_id": research_id
    }

# Task 1a: Chunk the prompt text
@app.task(name="research.chunk_prompt")
def chunk_prompt(research_id: int):
    """
    Task to process the prompt text into semantic chunks.
    Each chunk is stored in the database and an embedding is created.
    """
    logger.info(f"Processing prompt chunks for research ID: {research_id}")
    
    # Get the research record and chunk the prompt
    with get_db_sync() as session:
        try:
            research = session.query(DeepResearch).filter(DeepResearch.id == research_id).one()
            prompt_text = research.prompt_text
            
            # Generate semantic chunks
            chunks = create_semantic_chunks(prompt_text)
            logger.info(f"Created {len(chunks)} prompt chunks")
            
            # Process each chunk
            for idx, chunk_text in enumerate(chunks):
                # Store chunk in database
                chunk = ResearchChunk(
                    deep_research_id=research_id,
                    chunk_index=idx,
                    chunk_type="prompt",
                    chunk_text=chunk_text
                )
                session.add(chunk)
                session.flush()
                
                # Create embedding for chunk
                embedding = create_embedding(chunk_text)
                
                # Store in Pinecone with metadata
                vector_id = f"prompt_chunk_{research_id}_{idx}"
                metadata = {
                    "research_id": research_id,
                    "chunk_id": chunk.id,
                    "chunk_type": "prompt",
                    "chunk_index": idx,
                    "text": chunk_text[:1000]  # Truncate for metadata limit
                }
                store_in_pinecone(vector_id, embedding, metadata)
            
            session.commit()
            return {
                "status": "success", 
                "task": "chunk_prompt", 
                "chunks_created": len(chunks)
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error in chunk_prompt: {str(e)}")
            raise

# Task 1b: Chunk the report text
@app.task(name="research.chunk_report")
def chunk_report(research_id: int):
    """
    Task to process the report text into semantic chunks.
    Each chunk is stored in the database and an embedding is created.
    """
    logger.info(f"Processing report chunks for research ID: {research_id}")
    
    # Similar implementation to chunk_prompt but for report text
    with get_db_sync() as session:
        try:
            research = session.query(DeepResearch).filter(DeepResearch.id == research_id).one()
            report_text = research.final_report
        
            # Generate semantic chunks
            chunks = create_semantic_chunks(report_text)
            logger.info(f"Created {len(chunks)} report chunks")
            
            # Process each chunk
            for idx, chunk_text in enumerate(chunks):
                # Store chunk in database
                chunk = ResearchChunk(
                    deep_research_id=research_id,
                    chunk_index=idx,
                    chunk_type="report",
                    chunk_text=chunk_text
                )
                session.add(chunk)
                session.flush()
                
                # Create embedding for chunk
                embedding = create_embedding(chunk_text)
                
                # Store in Pinecone with metadata
                vector_id = f"report_chunk_{research_id}_{idx}"
                metadata = {
                    "research_id": research_id,
                    "chunk_id": chunk.id,
                    "chunk_type": "report",
                    "chunk_index": idx,
                    "text": chunk_text[:1000]
                }
                store_in_pinecone(vector_id, embedding, metadata)
            
            session.commit()
            return {
                "status": "success", 
                "task": "chunk_report", 
                "chunks_created": len(chunks)
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error in chunk_report: {str(e)}")
            raise

# Task 2: Generate document-level embeddings
@app.task(name="research.generate_document_embeddings")
def generate_document_embeddings(research_id: int, chunk_results=None):
    """
    Generate embeddings for the entire prompt and report.
    Store these in the DeepResearch record.
    """
    logger.info(f"Generating document embeddings for research ID: {research_id}")
    
    with get_db_sync() as session:
        try:
            research = session.query(DeepResearch).filter(DeepResearch.id == research_id).one()
            
            # Generate embeddings for full texts
            prompt_embedding = create_embedding(research.prompt_text)
            report_embedding = create_embedding(research.final_report)
            
            # Update research record with embeddings
            research.prompt_embedding = prompt_embedding
            research.report_embedding = report_embedding
            
            # Also update the TSV fields for full-text search
            research.prompt_tsv = func.to_tsvector('english', research.prompt_text)
            research.report_tsv = func.to_tsvector('english', research.final_report)
            
            session.commit()
            return {
                "status": "success", 
                "task": "generate_document_embeddings"
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error in generate_document_embeddings: {str(e)}")
            raise

# Task 3: Create summaries
@app.task(name="research.create_summaries")
def create_summaries(research_id: int, embedding_result=None):
    """
    Create summaries of different lengths based on content size.
    For each summary, store it in the database and create an embedding.
    
    Summary length decision rules:
    - Very short (100 words): All reports
    - Short (250 words): Reports >= 1000 words
    - Medium (500 words): Reports >= 2000 words
    - Long (1000 words): Reports >= 3000 words
    
    For prompts:
    - Short (100 words): Prompts >= 200 words
    """
    logger.info(f"Creating summaries for research ID: {research_id}")
    
    with get_db_sync() as session:
        try:
            research = session.query(DeepResearch).filter(DeepResearch.id == research_id).one()
            
            # Count words in report and prompt
            report_word_count = len(research.final_report.split())
            prompt_word_count = len(research.prompt_text.split())
            
            summaries_created = 0
            
            # Determine which report summaries to create
            if report_word_count >= 200:
                # Define summary configurations based on word count
                summary_configs = [
                    ("report", "veryshort", 100, "gpt-3.5-turbo")  # Always create a very short summary
                ]
                
                if report_word_count >= 1000:
                    summary_configs.append(("report", "short", 250, "gpt-3.5-turbo"))
                
                if report_word_count >= 2000:
                    summary_configs.append(("report", "medium", 500, "gpt-4"))
                
                if report_word_count >= 3000:
                    summary_configs.append(("report", "long", 1000, "gpt-4"))
                
                if report_word_count >= 4000:
                    summary_configs.append(("report", "verylong", 2000, "gpt-4"))
                
                # Create each configured summary
                for scope, length_name, target_length, model in summary_configs:
                    summary_text = create_summary(
                        research.final_report, target_length, model
                    )
                    
                    # Store in database
                    summary = ResearchSummary(
                        deep_research_id=research_id,
                        summary_scope=scope,
                        summary_length=length_name,
                        summary_text=summary_text
                    )
                    session.add(summary)
                    session.flush()
                    
                    # Create embedding
                    embedding = create_embedding(summary_text)
                    
                    # Store in Pinecone
                    vector_id = f"summary_{research_id}_{scope}_{length_name}"
                    metadata = {
                        "research_id": research_id,
                        "summary_id": summary.id,
                        "summary_scope": scope,
                        "summary_length": length_name,
                        "text": summary_text[:1000]
                    }
                    store_in_pinecone(vector_id, embedding, metadata)
                    
                    summaries_created += 1
            
            # Create prompt summary if needed
            if prompt_word_count >= 200:
                # Define summary configurations based on word count
                summary_configs = [
                    ("prompt", "veryshort", 100, "gpt-3.5-turbo")  # Always create a very short summary
                ]
                
                if prompt_word_count >= 1000:
                    summary_configs.append(("prompt", "short", 250, "gpt-3.5-turbo"))
                
                if prompt_word_count >= 2000:
                    summary_configs.append(("prompt", "medium", 500, "gpt-4"))
                
                if prompt_word_count >= 3000:
                    summary_configs.append(("prompt", "long", 1000, "gpt-4"))
                
                if prompt_word_count >= 4000:
                    summary_configs.append(("prompt", "verylong", 2000, "gpt-4"))
                
                # Create each configured summary
                for scope, length_name, target_length, model in summary_configs:
                    summary_text = create_summary(
                        research.final_report, target_length, model
                    )
                    
                    # Store in database
                    summary = ResearchSummary(
                        deep_research_id=research_id,
                        summary_scope=scope,
                        summary_length=length_name,
                        summary_text=summary_text
                    )
                    session.add(summary)
                    session.flush()
                    
                    # Create embedding
                    embedding = create_embedding(summary_text)
                    
                    # Store in Pinecone
                    vector_id = f"summary_{research_id}_{scope}_{length_name}"
                    metadata = {
                        "research_id": research_id,
                        "summary_id": summary.id,
                        "summary_scope": scope,
                        "summary_length": length_name,
                        "text": summary_text[:1000]
                    }
                    store_in_pinecone(vector_id, embedding, metadata)
                    
                    summaries_created += 1
            
            session.commit()
            return {
                "status": "success", 
                "task": "create_summaries", 
                "summaries_created": summaries_created
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error in create_summaries: {str(e)}")
            raise

# Task 4: Process domain co-occurrences
@app.task(name="research.process_domain_cooccurrences")
def process_domain_cooccurrences(research_id: int, summary_result=None):
    """
    Process domain co-occurrences from the research sources.
    For each pair of domains that appear together, update co-occurrence counts.
    """
    logger.info(f"Processing domain co-occurrences for research ID: {research_id}")
    
    with get_db_sync() as session:
        try:
            # Get all sources for this research
            sources = (
                session.query(ResearchSource)
                .filter(ResearchSource.deep_research_id == research_id)
                .all()
            )
            
            # Extract unique, non-empty domains
            domains = list({source.domain for source in sources if source.domain})
            
            pairs_processed = set()
            
            # Process each unique pair of domains
            for i in range(len(domains)):
                for j in range(i+1, len(domains)):
                    # Ensure alphabetical ordering for consistency
                    domain_a, domain_b = sorted([domains[i], domains[j]])
                    if (domain_a, domain_b) not in pairs_processed:
                        # Check if this co-occurrence already exists
                        co_occurrence = (
                            session.query(DomainCoOccurrence)
                            .filter(
                                DomainCoOccurrence.domain_a == domain_a,
                                DomainCoOccurrence.domain_b == domain_b
                            )
                            .first()
                        )
                        
                        if co_occurrence:
                            # Update existing record
                            co_occurrence.co_occurrence_count += 1
                        else:
                            # Create new record
                            co_occurrence = DomainCoOccurrence(
                                domain_a=domain_a,
                                domain_b=domain_b,
                                co_occurrence_count=1
                            )
                            session.add(co_occurrence)
                        
                        pairs_processed.add((domain_a, domain_b))
            
            session.commit()
            return {
                "status": "success", 
                "task": "process_domain_cooccurrences", 
                "pairs_processed": len(pairs_processed)
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error in process_domain_cooccurrences: {str(e)}")
            raise

# Utility functions
def create_semantic_chunks(text: str, max_chunk_size: int = 1000, overlap: int = 50) -> List[str]:
    """
    Split text into semantic chunks with a specified maximum size.
    Uses sentence boundaries to create coherent chunks with optional overlap.
    
    Args:
        text: The text to chunk
        max_chunk_size: Maximum number of words per chunk
        overlap: Number of words to overlap between chunks
    
    Returns:
        List of text chunks
    """
    # Use NLTK to split into sentences
    sentences = sent_tokenize(text)
    
    # Get word counts for each sentence
    sentence_word_counts = [len(s.split()) for s in sentences]
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    overlap_sentences = []
    
    for i, (sentence, word_count) in enumerate(zip(sentences, sentence_word_counts)):
        # If adding this sentence would exceed the limit and we already have content
        if current_word_count + word_count > max_chunk_size and current_chunk:
            # Store the current chunk
            chunks.append(" ".join(current_chunk))
            
            # Start a new chunk with overlap sentences
            current_chunk = overlap_sentences.copy()
            current_word_count = sum(len(s.split()) for s in overlap_sentences)
            
            # Reset overlap sentences
            overlap_sentences = []
        
        # Add the sentence to the current chunk
        current_chunk.append(sentence)
        current_word_count += word_count
        
        # Update overlap sentences (keep sentences that fit within overlap word count)
        overlap_sentences.append(sentence)
        overlap_word_count = sum(len(s.split()) for s in overlap_sentences)
        
        while overlap_word_count > overlap and len(overlap_sentences) > 1:
            overlap_word_count -= len(overlap_sentences[0].split())
            overlap_sentences.pop(0)
    
    # Add the final chunk if there's anything left
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def create_embedding(text: str) -> List[float]:
    """
    Create an embedding vector for the given text using OpenAI's API.
    
    Args:
        text: The text to embed
        
    Returns:
        Embedding vector as a list of floats
    """
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Check cache first
    cached = get_cached_embedding(text_hash)
    if cached:
        return cached
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=text,
            dimensions=3072  # Match dimension in DeepResearch model
        )
        embedding = response.data[0].embedding
        # Cache the result before returning
        cache_embedding(text_hash, embedding)
        return embedding
    except Exception as e:
        logger.error(f"Error creating embedding: {str(e)}")
        # Return a zero vector as fallback
        return [0.0] * 3072

def store_in_pinecone(vector_id: str, embedding: List[float], metadata: Dict[str, Any]):
    """
    Store an embedding vector in Pinecone with metadata.
    
    Args:
        vector_id: Unique identifier for the vector
        embedding: The embedding vector
        metadata: Additional metadata to store with the vector
    """
    try:
        index.upsert(
            vectors=[{
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            }]
        )
    except Exception as e:
        logger.error(f"Error storing in Pinecone: {str(e)}")

def create_summary(text: str, target_length: int, model: str) -> str:
    """
    Create a summary of the given text using OpenAI's API.
    
    Args:
        text: Text to summarize
        target_length: Target length in words
        model: OpenAI model to use
        
    Returns:
        Summarized text
    """
    try:
        prompt = f"""Summarize the following text in approximately {target_length} words. 
        Preserve the key points, main conclusions, and important details:
        
        {text}"""
        
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert summarizer. Create concise, accurate summaries that capture the essential information and maintain the tone of the original text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=target_length * 4,  # Provide enough tokens for the response
            temperature=0.3  # Lower temperature for more deterministic output
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error creating summary: {str(e)}")
        # Return a truncated version as fallback
        words = text.split()
        return " ".join(words[:target_length])