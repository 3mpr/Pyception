CREATE TABLE IF NOT EXISTS `experiments` (
    `id`            INTEGER PRIMARY KEY,
    `subject`       INTEGER,
    `name`          VARCHAR             NOT NULL,
    `sample_rate`   REAL                NULL,
    `lasted`        REAL                NULL,
    'date'          DATETIME            NULL        DEFAULT CURRENT_TIME,
    FOREIGN KEY ( subject ) REFERENCES subjects ( id )
);
