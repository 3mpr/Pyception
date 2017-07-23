CREATE TABLE IF NOT EXISTS `subjects` (
    `id`            INTEGER PRIMARY KEY,
    `name`          VARCHAR             NOT NULL,
    `control`       INTEGER             NOT NULL    DEFAULT 1,
    CONSTRAINT unicity UNIQUE ( name )
);
