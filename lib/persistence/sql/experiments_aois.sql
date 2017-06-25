CREATE TABLE IF NOT EXISTS `experiments_aois` (
    `experiment`        INTEGER,
    `aoi`               INTEGER,
    CONSTRAINT PK_experiments_aois PRIMARY KEY ( experiment, aoi ),
    FOREIGN KEY ( experiment ) REFERENCES experiments ( id ),
    FOREIGN KEY ( aoi ) REFERENCES aois ( id )
);
