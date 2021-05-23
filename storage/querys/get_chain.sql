SELECT bindex, bhash, previous_hash, meanwhile, createtime FROM Block b
INNER JOIN (
WITH RECURSIVE split(bindex, hashpath, nexthashes) AS (
    SELECT bindex, '', hashpath||';' FROM (
        WITH RECURSIVE cte AS (
            SELECT bindex, bhash, previous_hash, cast(bhash AS CHAR(99999999999999999)) AS hashpath, 1 AS n
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
    substr(nexthashes, 0, instr(nexthashes, ';')),
    substr(nexthashes, instr(nexthashes, ';')+1)
    FROM split WHERE nexthashes!=''
) 
SELECT hashpath as hash
FROM split
WHERE hashpath!='') sq ON b.bhash = sq.hash
ORDER BY bindex