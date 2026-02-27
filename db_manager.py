import mysql.connector


class DBManager:
    def __init__(self, host="localhost", user="root", password="", database="university_erp", port=3306):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port
        }

    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)

            if connection.is_connected():
                return connection

        except mysql.connector.Error as e:
            raise Exception(f"MySQL Connection Failed: {str(e)}")

    def test_connection(self):
        try:
            conn = self.get_connection()
            conn.close()
            return True, "Connected to university_erp successfully!"
        except Exception as e:
            return False, str(e)