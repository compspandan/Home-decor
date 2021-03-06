from flask import Blueprint, request, jsonify, Response, g
from operator import itemgetter
from psycopg2.extras import RealDictCursor
import psycopg2

projectmanager_blueprint = Blueprint('projectmanager', __name__)

# gets projectid of projects managed by given an employee id
@projectmanager_blueprint.route('/projectmanager/<string:employee_id>')
def get_projects(employee_id):
	try:
		cursor = g.db.cursor(cursor_factory=RealDictCursor)
		print("!")
		cursor.execute(f"SELECT p.projectID from project as p WHERE p.projectID IN (SELECT projectID from managedBy as m WHERE m.employeeID={employee_id});")
		res = cursor.fetchall()

		if res:
			# resjson = json.dumps(res,indent=4, sort_keys=True, default=str)
			return jsonify(res)
		else:
			return jsonify(message="no projects")
	except(Exception, psycopg2.Error) as error:
		print(error)
		return Response(error,status=500)
	finally:
		cursor.close()

# gets projectid of projects managed by given an employee id
@projectmanager_blueprint.route('/projectmanager/getfreedesigners')
def get_free_designers():
	try:
		cursor = g.db.cursor(cursor_factory=RealDictCursor)
		
		cursor.execute(f"select employeeid, empname from employee where (designation='Sr Designer' or designation='Jr Designer') and employeeid not in (select employeeid from designedBy group by employeeid having count(employeeid)>2);")
		res = cursor.fetchall()
		if res:
			return jsonify(res)
		else:
			return jsonify(message="No free designers")
	except(Exception, psycopg2.Error) as error:
		print(error)
		return Response(error,status=500)
	finally:
		cursor.close()


# creates a project also add record in managed by 
@projectmanager_blueprint.route('/projectmanager/<string:employee_id>',methods=['POST'])
def post_project(employee_id):
	try:
		data = request.json
		print(data)

		hno, street, pin, city, state, len, bred, custid, sd, ed, designerlist  = itemgetter('houseNo', 'street', 'pincode','city', 'state', 'length', 'breadth', 'customerid','startDate','estimatedEndDate', 'designerlist')(data)
		
		cursor = g.db.cursor(cursor_factory=RealDictCursor)
		cursor.execute(f"INSERT INTO siteDetails (houseno, street, pincode, city, state, length, breadth) values(\'{hno}\',\'{street}\',\'{pin}\',\'{city}\',\'{state}\',\'{len}\',\'{bred}\');")
		g.db.commit()
		cursor = g.db.cursor(cursor_factory=RealDictCursor)
		cursor.execute(f"INSERT INTO project (customerid, startdate, estimatedenddate) values(\'{custid}\',\'{sd}\',\'{ed}\');")
		g.db.commit()
		cursor = g.db.cursor(cursor_factory=RealDictCursor)
		cursor.execute(f"insert into managedBy(projectid, employeeid) select max(projectid), {employee_id} from project;")
		g.db.commit()
		cursor = g.db.cursor(cursor_factory=RealDictCursor)
		cursor.execute(f"select max(projectid) from project;")
		c = cursor.fetchone()
		new_proj_id = c['max']
		for des in designerlist:
			cursor = g.db.cursor(cursor_factory=RealDictCursor)
			cursor.execute(f"insert into designedBy(projectid, employeeid) values({new_proj_id}, {des});")
			g.db.commit()		


		return jsonify(message="success")
	except(Exception, psycopg2.Error) as error:
		print(error)
		return Response(error,status=500)
	# finally:
		# cursor.close()

# get project details given project_id
@projectmanager_blueprint.route('/projectmanager/<string:employee_id>/<string:project_id>')
def get_project_by_id(employee_id,project_id):
	try:
		cursor = g.db.cursor(cursor_factory=RealDictCursor)

		cursor.execute(f"SELECT * FROM project where projectid={project_id}")
		project = cursor.fetchone()

		cursor.execute(f"SELECT houseNo, street, pincode, city, state, length, breadth from sitedetails where siteid={project['siteid']}")
		site = cursor.fetchone()

		cursor.execute(f"SELECT customerName, customerPhNo, customerEmailID, customerAddress from customer where customerid={project['customerid']}")
		customer = cursor.fetchone()

		cursor.execute(f"SELECT customerid, feedback, feedbackdate, rating FROM customerfeedback where projectid={project_id} AND customerid={project['customerid']};")
		customer_feedback = cursor.fetchall()

		cursor.execute(f"SELECT e.employeeid, e.empname, e.empemailid FROM employee as e, designedby where designedby.projectid={project_id} AND designedby.employeeid=e.employeeid;")
		designer = cursor.fetchall()

		cursor.execute(f" SELECT c.contractorid, c.contractorname, c.typeofwork, c.contractoremail FROM contractor as c where c.contractorid in (SELECT contractorid from works WHERE projectid={project_id});")
		contractor = cursor.fetchall()

		cursor.execute(f"SELECT roomid, roomname, roomsize, designid, productid, typename, productcost, description from (SELECT * from (SELECT * from hasRoom natural join room WHERE projectID={project_id}) as x natural join designIncludesProducts) as y natural join product;")
		des_for_rooms = cursor.fetchall()
		
		return jsonify(project=project,site=site,customer=customer,customerFeedback=customer_feedback, designer=designer, contractor=contractor, des_for_rooms=des_for_rooms)
	except(Exception, psycopg2.Error) as error:
		print(error)
		return Response(error,status=500)
	finally:
		cursor.close()

# function called before request is closed
@projectmanager_blueprint.teardown_app_request
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()