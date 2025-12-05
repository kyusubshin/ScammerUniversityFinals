# kimi_final_qwen_yes_no.py
import json
import csv
import os
import re
from openai import OpenAI

# ========================= 配置 =========================
PROMPT_FILE_PATH = "prompts/prompts_test.json"
OUTPUT_FILE_PATH = "responses.csv"

client = OpenAI(
    api_key="7FVf50oJqW8p0fIE3yR6c6xm8UciZcjZ",
    base_url="https://api.deepinfra.com/v1/openai",
)

# 换成你验证能用的最听话模型
MODEL_NAME = "Qwen/Qwen3-Next-80B-A3B-Instruct"


# ========================= 万能 Yes/No 提取 =========================
def force_yes_no(text: str) -> str:
    text = text.strip().upper().replace(" ", "")
    if text.startswith("YES") or "YES" in text:
        return "Yes"
    elif text.startswith("NO") or "NO" in text:
        return "No"
    else:
        first_char = text[:1]
        return "Yes" if first_char == "Y" else "No" if first_char == "N" else "Uncertain"


# ========================= 核心函数 =========================
def get_answer(question: str, constraint: str) -> str:
    prompt = f"""{constraint}

Statement: {question}

Answer with only "Yes" or "No" right now:"""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2,  # 强行只让它出 1~2 个 token
            temperature=1.0,
            top_p=0.01,
        )
        raw = completion.choices[0].message.content
        return force_yes_no(raw)

    except Exception as e:
        return f"ERROR: {e}"


# ========================= 主程序 =========================
def main():
    print(f"开始批量测试（模型：{MODEL_NAME}）\n")

    if not os.path.exists(PROMPT_FILE_PATH):
        print(f"文件不存在：{PROMPT_FILE_PATH}")
        return

    with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    results = []
    for i, item in enumerate(prompts, 1):
        qid = item["id"]
        dim = item["dimension"]
        qtext = item["question_text"]
        constraint = item["constraint"]

        print(f"{i:2d}/10 {qid} → ", end="")
        ans = get_answer(qtext, constraint)
        print(ans)

        results.append({
            "id": qid,
            "dimension": dim,
            "question_text": qtext,
            "model_answer": ans
        })

    # 保存
    keys = ["id", "dimension", "question_text", "model_answer"]
    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(results)

    print(f"\n全部完成！结果已保存到 {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    main()