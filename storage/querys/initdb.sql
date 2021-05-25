CREATE TABLE IF NOT EXISTS `Block` (
    bindex bigint NOT NULL,
    bhash varchar(255) NOT NULL,
    previous_hash varchar(255) NOT NULL,
    meanwhile varchar(255) NOT NULL,
    createtime bigint,
    PRIMARY KEY (bhash),
    FOREIGN KEY (previous_hash) REFERENCES Block(bhash)
);

CREATE TABLE IF NOT EXISTS `Transaction` (
    id varchar(255) NOT NULL,
    blockhash varchar(255) NOT NULL,
    sender_id text NOT NULL,
    recipient_id text NOT NULL,
    amount float,
    signature text NOT NULL, 
    PRIMARY KEY (id),
    FOREIGN KEY (blockhash) REFERENCES Block(bhash)
);

CREATE TABLE IF NOT EXISTS `Coinbase` (
    id varchar(255) NOT NULL,
    blockhash varchar(255) NOT NULL,
    recipient_id text NOT NULL,
    amount float,
    PRIMARY KEY (id),
    FOREIGN KEY (blockhash) REFERENCES Block(bhash)
);
