CREATE TABLE IF NOT EXISTS `data` (
`id`            INTEGER PRIMARY KEY,
`experiment`    INTEGER,
`timestamp`     REAL                NOT NULL,
`x`             REAL                NOT NULL,
'y'             REAL                NOT NULL,
FOREIGN KEY ( experiment ) REFERENCES experiments ( id )
CONSTRAINT unicity UNIQUE ( `timestamp`, `x`, `y` )
);
