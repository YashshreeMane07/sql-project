from sql_generator import generate_sql


def generate_explanation(sql: str, user_question: str):
    """
    Uses the same LLM used for SQL generation
    to generate a natural language explanation.
    """

    prompt = f"""
You are a database expert.

Explain the SQL query in simple and clear English.

Rules:
- Do NOT generate SQL.
- Do NOT modify the query.
- Do NOT add markdown.
- Keep explanation concise.
- Explain what tables are used and what data is returned.

User Question:
{user_question}

SQL Query:
{sql}

Explanation:
"""

    explanation = generate_sql(prompt)

    return explanation.strip()