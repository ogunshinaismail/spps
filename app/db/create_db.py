import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="root",
    password="root",
    # dbname="spps_db"
)

conn.autocommit = True  # Enable autocommit mode

cur = conn.cursor()
cur.execute("CREATE DATABASE spps_db;")
# cur.execute("USE spps_db;")

# cur.execute("""
#             INSERT INTO public.users (first_name,last_name,email,gender,date_of_birth,user_id,"password",department,"role") VALUES
#             ('James','Bond','test@gmail.com','male','12/07/1664','20210294061','1234567','Computer Science','student'),
#             ('John','Doe','test@gmail.com','male','12/07/1664','john.doe','1234567','Computer Science','lecturer');
#             """)
# cur.execute("""
#             INSERT INTO public.courses (course_code,course_title,lecturer_id) VALUES
# 	 ('STA 429','Statistics', 'john.doe'),
# 	 ('COM 101','Intro to Computer', 'john.doe'),
# 	 ('MTH 101','Into to Math', 'john.doe'),
# 	 ('GNS 101','Citizenship Education', 'john.doe');
#             """)
# cur.execute("""
#             INSERT INTO public.student_offered_courses (user_id,course_id,semester,"session") VALUES
# 	 ('20210294061',1,'1st','20/21'),
# 	 ('20210294061',2,'1st','20/21'),
# 	 ('20210294061',3,'1st','20/21'),
# 	 ('20210294061',4,'1st','20/21'),
# 	 ('20210294061',1,'1st','20/21'),
# 	 ('20210294061',2,'1st','20/21'),
# 	 ('20210294061',3,'1st','20/21'),
# 	 ('20210294061',4,'1st','20/21');
#             """)

cur.close()
conn.close()