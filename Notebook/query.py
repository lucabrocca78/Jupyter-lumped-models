def query(var, geom):
    if var == 'Temp':
        q = """
                WITH xy AS(SELECT i."index" 
                FROM "cindex" i
                WHERE ST_Contains(ST_SetSRID(
                            ST_GeomFromText(
                                '{}'
                            ),
                        4326),i.geom) ) 
                select temperature."date", avg(temperature.temperature) - 273 as temp
                from temperature
                join xy on xy.index = temperature."index"
                group by temperature."date"
                order by temperature."date"
                """.format(geom.wkt)
    else:
        q = """
                WITH xy AS(SELECT i."index" 
                FROM "cindex" i
                WHERE ST_Contains(ST_SetSRID(
                            ST_GeomFromText(
                                '{}'
                            ),
                        4326),i.geom) ) 
                select {}."date", avg({}.{}) as var
                from {}
                join xy on xy.index = {}."index"
                group by {}."date"
                order by {}."date"
                """.format(geom.wkt, var, var, var, var, var, var, var)
    return  q
