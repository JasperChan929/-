import json
import requests

API_BASE = "http://127.0.0.1:8000/api"
EVAL_FILE = "./sample_eval/qa_pairs.json"


def load_eval_data():
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def simple_hit_score(answer: str, expected_keywords: list[str]) -> int:
    answer_lower = answer.lower()
    for kw in expected_keywords:
        if kw.lower() in answer_lower:
            return 1
    return 0


def main():
    data = load_eval_data()
    total = len(data)
    hits = 0

    for idx, item in enumerate(data, start=1):
        question = item["question"]
        expected_keywords = item.get("expected_keywords", [])

        resp = requests.post(
            f"{API_BASE}/ask",
            json={"question": question},
            timeout=120,
        )

        if not resp.ok:
            print(f"[{idx}] FAILED | question={question}")
            continue

        result = resp.json()
        answer = result["answer"]
        score = simple_hit_score(answer, expected_keywords)
        hits += score

        print("=" * 80)
        print(f"[{idx}] Question: {question}")
        print(f"Expected Keywords: {expected_keywords}")
        print(f"Answer: {answer}")
        print(f"Hit: {score}")

    accuracy = hits / total if total else 0.0
    print("\n" + "=" * 80)
    print(f"Total: {total}")
    print(f"Hits: {hits}")
    print(f"Simple Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    main()