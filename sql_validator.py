import re


class SQLValidationError(Exception):
    pass


class SQLValidator:
    def __init__(self, database_name: str = "university_erp"):
        self.database_name = database_name.lower()

    def validate(self, sql: str) -> None:
        sql_clean = sql.strip().lower()

        if not sql_clean:
            raise SQLValidationError("Empty SQL query")

        # Block multiple statements
        if ";" in sql_clean[:-1]:
            raise SQLValidationError("Multiple SQL statements are not allowed")

        operation = self._detect_operation(sql_clean)

        # Block dangerous operations
        if operation in ("drop", "alter", "truncate", "create"):
            raise SQLValidationError(f"{operation.upper()} operation is not allowed")

        # DELETE must have WHERE
        if operation == "delete" and "where" not in sql_clean:
            raise SQLValidationError("DELETE without WHERE is not allowed")

        # UPDATE must have WHERE
        if operation == "update" and "where" not in sql_clean:
            raise SQLValidationError("UPDATE without WHERE is not allowed")

    def _detect_operation(self, sql: str) -> str:
        match = re.match(r"^(select|insert|update|delete|create|drop|alter|truncate)", sql)
        if not match:
            raise SQLValidationError("Unsupported SQL operation")
        return match.group(1)