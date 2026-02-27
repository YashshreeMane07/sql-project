import json
from prompt_builder import build_sql_prompt
from sql_generator import generate_sql
from sql_validator import SQLValidator, SQLValidationError
from mysql_executor import MySQLExecutor
from query_explainer import generate_explanation


def run_pipeline(user_question: str):

    try:
        # -------------------------------
        # 1️⃣ Load Full Schema
        # -------------------------------
        with open("mysql_schema.json", "r") as f:
            full_schema = json.load(f)

        # -------------------------------
        # 2️⃣ Build Prompt
        # -------------------------------
        prompt = build_sql_prompt(
            user_question=user_question,
            schema=full_schema,
            db_type="MYSQL"
        )

        # -------------------------------
        # 3️⃣ Generate SQL from LLM
        # -------------------------------
        sql = generate_sql(prompt)

        if not sql or sql.strip() == "":
            return {
                "status": "error",
                "message": "SQL generation failed"
            }

        sql = sql.strip()

        if sql == "SCHEMA_NOT_SUPPORTED":
            return {
                "status": "error",
                "message": "SCHEMA_NOT_SUPPORTED"
            }

        # -------------------------------
        # 4️⃣ Validate SQL (FIREWALL)
        # -------------------------------
        validator = SQLValidator("university_erp")

        try:
            validator.validate(sql)
        except SQLValidationError as ve:
            return {
                "status": "error",
                "message": f"SQL Validation failed: {str(ve)}"
            }

        # -------------------------------
        # 5️⃣ Execute SQL
        # -------------------------------
        executor = MySQLExecutor(
            host="localhost",
            user="root",
            password="Yashshreemane0205",
            database="university_erp"
        )

        try:
            db_result = executor.execute(sql)
        except Exception as db_error:
            return {
                "status": "error",
                "message": f"Database execution failed: {str(db_error)}"
            }

        # Ensure db_result is never None
        if db_result is None:
            db_result = []

        # -------------------------------
        # 6️⃣ Generate Explanation
        # -------------------------------
        explanation = generate_explanation(sql, user_question)

        # -------------------------------
        # 7️⃣ Success Response
        # -------------------------------
        return {
            "status": "success",
            "generated_sql": sql,
            "row_count": len(db_result),
            "db_result": db_result,
            "explanation": explanation
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Pipeline failure: {str(e)}"
        }