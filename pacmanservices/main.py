import pymysql
from app import app
from tables import Results
from db_config import mysql
from flask import flash, render_template, request, redirect
from werkzeug import generate_password_hash, check_password_hash

@app.route('/new_user')
def add_user_view():
	return render_template('add.html')
		
@app.route('/add', methods=['POST'])
def add_user():
	try:		
		_name = request.form['name']
		_score = int(request.form['score'])
		_level = int(request.form['level'])
		_id = int(request.form['id'])
		# validate the received values
		if _name and _score and _level and request.method == 'POST':
			insert = "INSERT INTO player(user_name, score, level) VALUES(%s,%s,%s)"
			update = "UPDATE player set score=%s,level=%s WHERE user_id=%s and score < %s"
			# save edits
			sql = insert if _id == 0 else update 
			data = (_name, _score, _level,) if _id==0 else (_score, _level, _id, _score)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			id = conn.insert_id() if _id == 0 else _id
			conn.commit()
			flash('User added successfully!')
			return {"id":id}, 200
		else:
			return 'Error while adding user'
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/highscore', methods=['GET'])
def highscore():
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM player ORDER BY score DESC")
		rows = cursor.fetchall()
		return {'data':rows}, 200
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
		
if __name__ == "__main__":
    app.run(host='0.0.0.0')
