from sqlalchemy import create_engine,text


engine = create_engine("mysql+pymysql://:ztwr1k1ijs2pictfcrq7:pscale_pw_E476YzhtOvyYnJuYnvbahWah9k4xz9zhYD272bzbafm@aws.connect.psdb.cloud/dashboard?charset=utf8mb4")

# with engine.connect() as conn:
#     result = conn.execute(text("select * from accounts"))
#     print(result.all())

#connect_args= {"ssl":{/etc/ssl/certs/ca-certificates.crt}}
