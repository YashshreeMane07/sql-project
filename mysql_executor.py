import mysql.connector


class MySQLExecutor:
    def __init__(self, host="localhost", user="root", password="", database="university_erp"):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }

    def execute(self, sql_query):
        connection = None
        cursor = None

        try:
            # ---- Safety Check ----
            blocked_keywords = ["insert", "update", "delete", "drop", "truncate", "alter"]
            query_lower = sql_query.strip().lower()

            for keyword in blocked_keywords:
                if query_lower.startswith(keyword):
                    return {
                        "status": "blocked",
                        "message": f"{keyword.upper()} operations are not allowed. Only SELECT queries are permitted."
                    }

            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor(dictionary=True)

            cursor.execute(sql_query)

            # ---- Only SELECT allowed ----
            if query_lower.startswith("select"):
                rows = cursor.fetchall()
                return {
                    "status": "success",
                    "type": "select",
                    "rows": rows
                }

            # ---- Anything else blocked ----
            return {
                "status": "blocked",
                "message": "Only SELECT queries are allowed."
            }

        except mysql.connector.Error as e:
            return {
                "status": "error",
                "message": str(e)
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()