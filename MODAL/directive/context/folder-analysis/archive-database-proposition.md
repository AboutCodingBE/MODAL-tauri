-- Archive Analysis Database Schema
-- Design decisions incorporated from discussion

-- ============================================================================
-- ARCHIVES TABLE
-- ============================================================================
-- Stores metadata about each archive being analyzed
-- Design decisions:
-- - analysis_status enum instead of boolean for better state tracking
-- - file_count/directory_count/total_size calculated after analysis (kept for performance)
-- - Timestamps track when analysis started and completed

CREATE TABLE archives (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name VARCHAR(255) NOT NULL,
root_path VARCHAR(1000) NOT NULL UNIQUE,

    -- Analysis tracking
    analysis_status VARCHAR(20) NOT NULL DEFAULT 'pending',
        -- Values: 'pending', 'in_progress', 'completed', 'failed'
    analysis_started_at DATETIME,
    analysis_completed_at DATETIME,
    error_message TEXT,
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    
    -- Calculated statistics (updated after analysis completes)
    file_count INTEGER DEFAULT 0,
    directory_count INTEGER DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    
    -- Constraints
    CHECK (analysis_status IN ('pending', 'in_progress', 'completed', 'failed'))
);

-- Index for common queries
CREATE INDEX idx_archives_status ON archives(analysis_status);
CREATE INDEX idx_archives_created ON archives(created_at);


-- ============================================================================
-- FILES TABLE
-- ============================================================================
-- Stores every file and directory discovered in an archive
-- Design decisions:
-- - Both full_path AND relative_path stored (easier queries vs SQL reconstruction)
-- - is_directory boolean (simpler, no symlinks expected)
-- - sha256_hash for future duplicate detection
-- - extension stored separately for easy filtering
-- - File system timestamps preserved

CREATE TABLE files (
id INTEGER PRIMARY KEY AUTOINCREMENT,
archive_id INTEGER NOT NULL,
parent_id INTEGER,  -- NULL for root-level items

    -- File identification
    name VARCHAR(500) NOT NULL,
    full_path VARCHAR(2000) NOT NULL,      -- Complete absolute path
    relative_path VARCHAR(2000) NOT NULL,  -- Path relative to archive root
    
    -- File type and metadata
    is_directory BOOLEAN NOT NULL DEFAULT 0,
    extension VARCHAR(50),  -- NULL for directories, populated for files
    
    -- File properties (NULL for directories)
    size_bytes BIGINT,
    sha256_hash VARCHAR(64),  -- For duplicate detection later
    
    -- Filesystem timestamps
    created_at DATETIME,
    modified_at DATETIME,
    
    -- System tracking
    discovered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (archive_id) REFERENCES archives(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES files(id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (
        (is_directory = 1 AND extension IS NULL AND size_bytes IS NULL) OR
        (is_directory = 0)
    )
);

-- Indexes for performance
CREATE INDEX idx_files_archive ON files(archive_id);
CREATE INDEX idx_files_parent ON files(parent_id);
CREATE INDEX idx_files_path ON files(archive_id, relative_path);
CREATE INDEX idx_files_extension ON files(extension) WHERE extension IS NOT NULL;
CREATE INDEX idx_files_hash ON files(sha256_hash) WHERE sha256_hash IS NOT NULL;
CREATE INDEX idx_files_type ON files(is_directory);

