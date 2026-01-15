CREATE DATABASE IF NOT EXISTS rag_metadata;
USE rag_metadata;

CREATE TABLE IF NOT EXISTS document_chunks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chunk_id VARCHAR(64) NOT NULL,
    vector_id INT NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    page_or_section VARCHAR(64),
    chunk_text TEXT NOT NULL,
    UNIQUE (chunk_id),
    INDEX (vector_id)
);