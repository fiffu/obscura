CREATE TABLE records(
    id TEXT PRIMARY KEY,
    salt TEXT NOT NULL,
    variant TEXT NOT NULL,
    payload TEXT NOT NULL
);

CREATE INDEX idx_records_id_salt
ON records(id, salt);
