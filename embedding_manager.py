"""
Event Embedding Database Manager using ChromaDB

This module provides functionality to create and query an embedding database
for event descriptions using ChromaDB and efficient Spanish language models.
"""

import os
import pandas as pd
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import re


class EventEmbeddingManager:
    """
    Manages embedding creation and similarity search for event descriptions.
    Uses ChromaDB for vector storage and retrieval.
    """
    
    def __init__(
        self, 
        db_path: str = "./chroma_db",
        collection_name: str = "event_descriptions",
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Initialize the Event Embedding Manager.
        
        Args:
            db_path: Path to ChromaDB storage directory
            collection_name: Name for the ChromaDB collection
            model_name: HuggingFace model name for embeddings
                       Default uses multilingual model optimized for Spanish
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.model_name = model_name
        
        self.model = SentenceTransformer(self.model_name)
        
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection = None
        self._init_collection()
        
    def _init_collection(self):
        """Initialize or get existing collection."""
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=None 
            )
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=None,
                metadata={"description": "Event descriptions embeddings for MadLife"}
            )
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and preprocess text for better embeddings.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if pd.isna(text) or not text:
            return ""
        
        # Convert to string and strip
        text = str(text).strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        return text
    
    def _prepare_event_text(self, event_row: pd.Series) -> str:
        """
        Combine relevant event fields into a single text for embedding.
        
        Args:
            event_row: Pandas series representing an event
            
        Returns:
            Combined text representation of the event
        """
        title = self._clean_text(event_row.get('TITULO', ''))
        description = self._clean_text(event_row.get('DESCRIPCION', ''))
        tipo = self._clean_text(event_row.get('TIPO', ''))
        district = self._clean_text(event_row.get('DISTRITO-INSTALACION', ''))
        
        # Combine fields with appropriate weights
        combined_text = f"{title}"
        if description:
            combined_text += f". {description}"
        if tipo:
            tipo_clean = tipo.split('/')[-1] if '/' in tipo else tipo
            combined_text += f". Categoría: {tipo_clean}"
        if district:
            combined_text += f". Distrito: {district}"
            
        return combined_text.strip()
    
    def add_events(self, df: pd.DataFrame, batch_size: int = 100) -> int:
        """
        Add events to the embedding database.
        
        Args:
            df: DataFrame containing event data
            batch_size: Number of events to process in each batch
            
        Returns:
            Number of events successfully added
        """
        
        if len(df) == 0:
            return 0
                
        added_count = 0
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            
            # Prepare texts and metadata
            texts = []
            ids = []
            metadatas = []
            
            for idx, row in batch.iterrows():
                # Create combined text
                text = self._prepare_event_text(row)
                if not text:
                    continue
                    
                texts.append(text)
                ids.append(str(row['ID-EVENTO']))
                
                # Prepare metadata
                metadata = {
                    'title': row.get('TITULO', ''),
                    'price': str(row.get('PRECIO', '')),
                    'free': str(row.get('GRATUITO', '')),
                    'date': str(row.get('FECHA', '')),
                    'time': str(row.get('HORA', '')),
                    'district': str(row.get('DISTRITO-INSTALACION', '')),
                    'venue': str(row.get('NOMBRE-INSTALACION', '')),
                    'type': str(row.get('TIPO', '')),
                    'audience': str(row.get('AUDIENCIA', ''))
                }
                metadatas.append(metadata)
            
            if texts:
                # Generate embeddings
                embeddings = self.model.encode(texts, show_progress_bar=True)
                
                # Add to collection
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                added_count += len(texts)
        
        return added_count
    
    def search_similar_events(
        self, 
        query: str, 
        n_results: int = 10,
        include_distances: bool = True,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for events similar to the given query.
        
        Args:
            query: Search query in natural language
            n_results: Number of similar events to return
            include_distances: Whether to include similarity distances
            filter_metadata: Optional metadata filters
            
        Returns:
            Dictionary containing search results
        """
        if not query or not query.strip():
            return {"results": [], "distances": [], "metadatas": []}
        
        # Clean and prepare query
        clean_query = self._clean_text(query)
        
        # Generate query embedding
        query_embedding = self.model.encode([clean_query])
        
        # Prepare where clause for filtering
        where_clause = None
        if filter_metadata:
            where_clause = {}
            for key, value in filter_metadata.items():
                if value:
                    where_clause[key] = {"$eq": str(value)}
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where=where_clause,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = {
            'query': query,
            'results': results.get('documents', [[]])[0],
            'metadatas': results.get('metadatas', [[]])[0],
            'event_ids': results.get('ids', [[]])[0],
            'distances': results.get('distances', [[]])[0] if include_distances else None
        }
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current collection.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            'total_events': count,
            'collection_name': self.collection_name,
            'model_name': self.model_name,
            'db_path': self.db_path
        }
    
    def reset_database(self) -> bool:
        """
        Reset the embedding database (delete all data).
        
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self._init_collection()
            return True
        except Exception as e:
            return False
    
    def export_similar_events_df(
        self, 
        query: str, 
        n_results: int = 10
    ) -> pd.DataFrame:
        """
        Search for similar events and return results as a DataFrame.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            DataFrame with search results
        """
        results = self.search_similar_events(query, n_results, include_distances=True)
        
        if not results['results']:
            return pd.DataFrame()
        
        # Create DataFrame from results
        data = []
        for i, (doc, metadata, event_id, distance) in enumerate(zip(
            results['results'], 
            results['metadatas'], 
            results['event_ids'], 
            results['distances']
        )):
            row = {
                'rank': i + 1,
                'event_id': event_id,
                'title': metadata.get('title', ''),
                'similarity_score': 1 - distance,  # Convert distance to similarity
                'distance': distance,
                'description_preview': doc[:200] + "..." if len(doc) > 200 else doc,
                'date': metadata.get('date', ''),
                'time': metadata.get('time', ''),
                'district': metadata.get('district', ''),
                'venue': metadata.get('venue', ''),
                'type': metadata.get('type', ''),
                'free': metadata.get('free', '')
            }
            data.append(row)
        
        return pd.DataFrame(data)


def create_embedding_database(df: pd.DataFrame, db_path: str = "./chroma_db") -> EventEmbeddingManager:
    """
    Convenience function to create embedding database from CSV file.
    
    Args:
        df: DataFrame containing event data
        db_path: Path for ChromaDB storage
        
    Returns:
        EventEmbeddingManager instance
    """
    # Load data
    
    # Create manager
    manager = EventEmbeddingManager(db_path=db_path)
    
    # Add events
    manager.add_events(df)
    
    return manager
