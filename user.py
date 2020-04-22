from database import DB
from errors import ApplicationError

class User:
	def __init__(self, username, password, user_id=None):
		self.id = user_id
		self.username = username
		self.password = password

	def to_dict(self):
		user_data = self.__dict__
		del user_data["password"] 
		return user_data


	def save(self):
		with DB() as db:
		    cursor = db.execute(self.__get_save_query())
		    self.id = cursor.lastrowid
		return self


	@staticmethod
	def find(user_id):
		result = None
		with DB() as db:
		    result = db.execute(
		            "SELECT username, password, id FROM user WHERE id = ?",
		            (user_id,))
		user = result.fetchone()
		if user is None:
		    raise ApplicationError(
		            "User with id {} not found".format(user_id), 404)
		return User(*user)


		    
	@staticmethod
	def delete(user_id):
		result = None
		with DB() as db:
		    result = db.execute("DELETE FROM user WHERE id = ?",
		            (user_id,))
		if result.rowcount == 0:
		    raise ApplicationError("No value present", 404)

	

	def __get_save_query(self):
		query = "{} INTO user {} VALUES {}"
		if self.id == None:
		    args = (self.username, self.password)
		    query = query.format("INSERT", "(username, password)", args)
		else:
		    args = (self.username, self.password, self.id)
		    query = query.format("REPLACE", "(username, password, id)", args)
		return query
