import psycopg2

c_port = <port>
c_host = <hostname>
c_user = <username>
c_pass = <password>
c_db = <dbname>

conn = psycopg2.connect(host=c_host, port=c_port, dbname=c_db, user=c_user, password=c_pass)


def exec_query(query):
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()
    cur.close()


profile_results = exec_query("SELECT adm.lea_name \
		,adm.public_adm \
		,needy.needy_pct \
		,public_schools.num_public_schools \
		,(CASE \
		    WHEN charter_names.num_schools IS NULL THEN 0 \
		    ELSE charter_names.num_schools \
		    END \
		 )AS num_charter_schools \
		,(CASE \
		    WHEN charter_names.num_schools IS NULL THEN '' \
		    ELSE charter_names.school_name \
		    END \
		 )AS charter_school_names \
		,(CASE \
		    WHEN private_schools.num_schools IS NULL THEN 0 \
		    ELSE private_schools.num_schools \
		    END \
		 )AS num_private_schools \
		,(CASE \
		    WHEN homeschools.num_schools IS NULL THEN 0 \
		    ELSE homeschools.num_schools \
		    END \
		 )AS num_homeschools \
FROM \
	(SELECT lea_id \
	,lea_name \
	,SUM(enrollment) as public_adm \
	FROM best_adm \
	WHERE school_year = '2018-19' \
	GROUP BY lea_id, lea_name \
	 ) AS adm \
LEFT JOIN (SELECT lea_id \
		   ,lea_name \
		   ,COUNT(lea_name) AS num_public_schools \
		  FROM best_adm \
		  WHERE school_year = '2018-19' \
		  GROUP BY lea_id, lea_name) as public_schools \
ON adm.lea_id = public_schools.lea_id \
LEFT JOIN needy ON adm.lea_id = needy.lea_id \
LEFT JOIN charter_names ON adm.lea_id = charter_names.lea_id \
LEFT JOIN homeschools ON adm.lea_id = homeschools.lea_id \
LEFT JOIN private_schools ON adm.lea_id = private_schools.lea_id \
WHERE (needy.school_year = '2017-18' OR needy.school_year is null) \
AND (charter_names.school_year = '2018-19' \
        OR charter_names.school_year is null) \
AND (homeschools.school_year = '2018-19' \
        OR homeschools.school_year is null) \
AND (private_schools.school_year = '2018-19' \
        OR private_schools.school_year is null)")

market_share_query = ("SELECT \
                        lea_name \
                        ,total_adm \
                        ,ROUND((total_adm * 100 / total_enrollment::numeric), 1) AS adm_pct \
                        ,charter_enrollment \
                        ,ROUND((charter_enrollment * 100 / total_enrollment::numeric), 1) AS charter_pct \
                        ,private_enrollment \
                        ,ROUND((private_enrollment * 100 / total_enrollment::numeric), 1) AS private_pct \
                        ,home_enrollment \
                        ,ROUND((home_enrollment * 100 / total_enrollment::numeric), 1) AS home_pct \
                        ,school_year \
                        ,total_enrollment \
                        FROM \
                        ( \
                        	SELECT \
                        		adm.lea_name \
                        		,adm.total_adm \
                        		,private_schools.enrollment AS private_enrollment \
                        		,charter_enrollment.enrollment AS charter_enrollment \
                        		,homeschools.enrollment AS home_enrollment \
                        		,adm.school_year \
                        		,(CASE \
                        		    WHEN \
                        		        (adm.total_adm IS NOT NULL \
                        		        AND private_schools.enrollment IS NOT NULL \
                        		        AND homeschools.enrollment IS NOT NULL \
                        		        AND charter_enrollment.enrollment IS NOT NULL) \
                        		    THEN (adm.total_adm + private_schools.enrollment \
                        		            + homeschools.enrollment + charter_enrollment.enrollment) \
                        		    ELSE (adm.total_adm + charter_enrollment.enrollment) \
                        		    END \
                        		) AS total_enrollment \
                        	FROM \
                        	( \
                        		SELECT \
                        				lea_name \
                        				,SUM(enrollment) AS total_adm \
                        				,school_year \
                        		FROM best_adm \
                        		GROUP BY lea_name, school_year \
                        	) AS adm \
                        LEFT JOIN private_schools ON adm.lea_name = private_schools.lea_name \
                        LEFT JOIN homeschools ON adm.lea_name = homeschools.lea_name \
                        LEFT JOIN charter_enrollment ON adm.lea_name = charter_enrollment.lea_name \
                        WHERE (adm.school_year = private_schools.school_year \
                                OR private_schools.school_year is null) \
                        AND (adm.school_year = homeschools.school_year \
                                OR homeschools.school_year is null) \
                        AND (adm.school_year = charter_enrollment.school_year \
                                OR charter_enrollment.school_year is null) \
                        ORDER BY lea_name ASC, school_year DESC \
                        ) AS enrollment")

state_market_share_query = ("SELECT * FROM state_marketshare \
                                    ORDER BY school_year DESC LIMIT(3)")

tip_leas_raw = exec_query("SELECT lea_name FROM lea_ids_names \
                        WHERE tipdistrict = 1")

parent_leas = {
    'Chapel Hill-Carrboro City Schools': 'Orange County Schools'
    , 'Asheville City Schools': 'Buncombe County Schools'
    , 'Elkin City Schools': 'Surry County Schools'
    , 'Clinton City Schools': 'Sampson County Schools'
    , 'Kannapolis City Schools': 'Cabarrus County Schools'
    , 'Mooresville Graded School District': 'Iredell-Statesville Schools'
    , 'Roanoke Rapids City Schools': 'Halifax County Schools'
    , 'Mount Airy City Schools': 'Surry County Schools'
    , 'Lexington City Schools': 'Davidson County Schools'
    , 'Hickory City Schools': 'Catawba County Schools'
    , 'Whiteville City Schools': 'Columbus County Schools'
    , 'Newton Conover City Schools': 'Catawba County Schools'
    , 'Thomasville City Schools': 'Davidson County Schools'
    , 'Weldon City Schools': 'Halifax County Schools'
    , 'Asheboro City Schools': 'Randolph County School System'
}
