
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




WITH split(hashpath, str) AS (
     SELECT hashpath||',' FROM  (
        with recursive cte as (
      select bindex, bhash, previous_hash, cast(bhash as char(10000000)) as hashpath, 1 as n
      from Block
      where bindex = 5
      union all
      select Block.bindex, Block.bhash, Block.previous_hash, cte.hashpath || ';' || Block.bhash, n + 1
      from cte join
           Block
           on Block.bindex = cte.bindex - 1 and
              Block.bhash = cte.previous_hash
     )






WITH RECURSIVE split(bindex, hashpath, str) AS (
    SELECT bindex, '', hashpath||';' FROM (
        
                        with recursive cte as (
                            select bindex, bhash, previous_hash, cast(bhash as char(10000000)) as hashpath, 1 as n
                            from Block
                            where bindex = (SELECT max(bindex) FROM Block)
                            union all
                            select Block.bindex, Block.bhash, Block.previous_hash, cte.hashpath || ';' || Block.bhash, n + 1
                            from cte join
                                Block
                                on Block.bindex = cte.bindex - 1 and
                                    Block.bhash = cte.previous_hash
                            )


                        select * from (select cte.*, max(n) over () as max_n
                            from cte
                            ) cte
                        where n = max_n

    )
    UNION ALL SELECT
    bindex,
    substr(str, 0, instr(str, ',')),
    substr(str, instr(str, ',')+1)
    FROM split WHERE str!=''
) 
SELECT bindex, hashpath
FROM split
WHERE hashpath!='';







SELECT bindex, bhash FROM Block b
INNER JOIN (
WITH RECURSIVE split(bindex, hashpath, str) AS (
    SELECT bindex, '', hashpath||';' FROM (
        WITH RECURSIVE cte AS (
            SELECT bindex, bhash, previous_hash, cast(bhash AS CHAR(66*SELECT max(bindex))) AS hashpath, 1 AS n
            FROM Block
            WHERE bindex = (SELECT max(bindex) FROM Block)
            UNION ALL
            SELECT Block.bindex, Block.bhash, Block.previous_hash, cte.hashpath || ';' || Block.bhash, n + 1
            FROM cte JOIN
                Block ON Block.bindex = cte.bindex - 1 AND Block.bhash = cte.previous_hash)
        SELECT * FROM (SELECT cte.*, max(n) OVER () AS max_n FROM cte)
        cte WHERE n = max_n)
    UNION ALL SELECT
    bindex,
    substr(str, 0, instr(str, ';')),
    substr(str, instr(str, ';')+1)
    FROM split WHERE str!=''
) 
SELECT hashpath as hash
FROM split
WHERE hashpath!='') sq ON b.bhash = sq.hash
ORDER BY bindex












