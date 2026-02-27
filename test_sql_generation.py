import json
from prompt_builder import build_sql_prompt
from sql_generator import generate_sql


def test_sql_pipeline():
    user_query = "list all system users email"

    # Load full schema
    with open("mysql_schema.json", "r") as f:
        full_schema = json.load(f)

    prompt = build_sql_prompt(user_query, full_schema)

    print("\n----- PROMPT SENT TO LLM -----")
    print(prompt)
    print("-----------------------------\n")

    sql = generate_sql(prompt)

    print("Generated SQL:")
    print(sql)


if __name__ == "__main__":
    test_sql_pipeline()