def build_sql_prompt(user_question: str, schema: dict, db_type="MYSQL") -> str:
    
    # ---- Convert JSON schema dict to readable format ----
    schema_lines = []

    for table, columns in schema.items():
        cols = ", ".join(columns)
        schema_lines.append(f"{table}({cols})")

    schema_text = "\n".join(schema_lines)

    prompt = f"""
You are an expert database engineer.

Database type: {db_type}

FULL DATABASE SCHEMA:
{schema_text}

STRICT RULES:
- Use ONLY tables and columns from the schema above.
- Do NOT invent tables.
- Do NOT invent columns.
- If a table or column is NOT present, DO NOT use it.
- If multiple tables contain the same column name, ALWAYS prefix with table name (table.column).
- Output ONLY the SQL query.
- No explanation.
- No markdown.
- No comments.
- If the request cannot be fulfilled using the schema, output exactly:
SCHEMA_NOT_SUPPORTED

User Question:
{user_question}
"""

    return prompt.strip()