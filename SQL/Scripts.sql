select d."date", avg(d."temp" - 273) as temp from daily d
where d."index" IN 
(SELECT i."index" 
FROM "cindex" i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom)) group by d."date";

select i.lat,i.lon from "cindex" i;


select to_char(date,'Mon') as mon,
       extract(year from date) as yyyy,
       Avg(d."temp") as ave
from daily d
where d."date" between '2010-01-01' and '2011-01-01'
group by 1,2
order by 2;

select p.pre*1000 as prec from pre p where p."date" = '2010-01-01';


create index pre_idx
on pre (index);

SELECT i.geom 
FROM cindex  i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom)
        
        
UPDATE "cindex" SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);

select count(*) from pre p; 
        
select d."date", avg(d."temperature" - 273) as temp from temperature d
where d."index" intersect
(SELECT i."index" 
FROM "cindex" i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom)) ;

       
SELECT i."index"
FROM "cindex" i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom)
        
select temperature."date",temperature."temperature" ,cindex."index"
from temperature
join cindex on temperature."index" = cindex."index"
where temperature."date" between '2018-01-01' and '2019-01-01';
   
SELECT i."index"
FROM "cindex" i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom);
       
select temperature."date",temperature."temperature" 
from
	(
	SELECT i."index"
	FROM "cindex" i
	WHERE ST_Contains(ST_SetSRID(
	            ST_GeomFromText(
	                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
	            ),
	        4326),i.geom) 
	
	) as geometry
	join
	(
	select 
	temperature."index" 
	from temperature 
	)
	as tindex
	
	on geometry.index = tindex.index; 

       
       
select index as newindex
	from
	(
	select 
	c.index
	from cindex c
	WHERE ST_Contains(ST_SetSRID(
	            ST_GeomFromText(
	                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
	            ),
	        4326),c.geom) 
	
	) as geometry where geometry.newindex = 5706;

select temperature."date",avg(temperature.temperature)
from temperature
where temperature."date" between '2018-01-01' and '2019-01-01' and temperature."index" IN
(SELECT i."index" 
FROM "cindex" i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom)) group by "date" ;
	
       

explain analyse       


explain analyse  
select d."date", avg(d."temperature" - 273) as temp from temperature d
where d."date" between '2018-01-01' and '2019-01-01' and d."index" IN
(SELECT i."index" 
FROM "cindex" i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom)) group by date;
       
create index tempindex
on temperature(index);
       
       
WITH xy AS(SELECT i."index" 
FROM "cindex" i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom) ) 
select temperature."date", avg(temperature.temperature) - 273 as temp
from temperature
join xy on xy.index = temperature."index"
where temperature."date" between '2018-01-01' and '2019-01-01'
group by temperature."date";

create index preindex
on pre(index);

WITH xy AS(SELECT i."index" 
FROM "cindex" i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom) ) 
select pre."date", sum(pre.pre)*1000 
from pre
join xy on xy.index = pre."index"
where pre."date" between '2018-01-01' and '2019-01-01'
group by pre."date";

explain analyse
select count(p.pre) from pre p where p."index" = 8160 ;

explain analyse
select count(t.temperature) from temperature t where t."index" = 8160 ;


WITH xy AS(SELECT i."index" 
FROM "cindex" i
WHERE ST_Contains(ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((32.437134 38.950865 ,32.426147 40.178873 ,33.524780 40.279526 ,33.502808 39.715638,32.437134 38.950865))'
            ),
        4326),i.geom) ) 
select temperature."date", avg(temperature.temperature) - 273 as temp
from temperature
join xy on xy.index = temperature."index"
group by temperature."date"
order by temperature."date";


select p."date",p.pre from pre p
where p."date" between '2019-01-01' and '2019-01-03' and p."index" = 500;

ALTER TABLE "grid_polygon" ADD COLUMN geom_poly geometry(Point, 4326);
UPDATE "grid_polygon" SET geom_poly = ST_SetSRID(ST_MakePoint(lon, lat), 4326);

ALTER TABLE grid_polygon ADD COLUMN area real;
UPDATE grid_polygon SET area = ST_Area(geom::geography) / 1000^2;


select gp.geom,gp.geom_poly,gp.area from grid_polygon gp
order by area desc;


WITH xy AS(SELECT i."index" 
FROM "cindex" i
WHERE ST_Contains((select t.geom from "Test" t where t.layer = 'Cakit'),i.geom) ) 
select temperature."date", avg(temperature.temperature) - 273 as temp
from temperature
join xy on xy.index = temperature."index"
where temperature."date" between '2016-10-09' and '2019-09-30'
group by temperature."date"
order by temperature."date";


