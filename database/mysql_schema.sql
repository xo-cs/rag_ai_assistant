CREATE DATABASE IF NOT EXISTS rag_metadata;
USE rag_metadata;

DROP TABLE IF EXISTS document_chunks;

CREATE TABLE document_chunks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chunk_id VARCHAR(128) NOT NULL,
    vector_id INT NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    page_or_section VARCHAR(64),
    chunk_text TEXT NOT NULL,
    chunk_context TEXT, -- <--- THIS WAS MISSING
    UNIQUE (chunk_id),
    INDEX (vector_id)
);