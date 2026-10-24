"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask "LoRAとは何ですか？" --models gemini-3.5-flash-lite,gemini-3.1-flash
    uv run python -m app.ask --interactive --models gemini-3.5-flash-lite,gemini-3.1-flash
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
import time

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def _parse_models(value: str) -> list[str]:
    models = [model.strip() for model in value.split(",")]
    if not models or any(not model for model in models):
        raise argparse.ArgumentTypeError("モデル名をカンマ区切りで指定してください")
    return models


def ask(question: str, model: str) -> str:
    client = genai.Client(api_key=get_api_key())
    started_at = time.perf_counter()
    response = client.models.generate_content(model=model, contents=question)
    response_time = time.perf_counter() - started_at

    _print_usage(response, response_time)

    return response.text


def _print_usage(response, response_time: float) -> None:
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count if usage else None
    output_tokens = usage.candidates_token_count if usage else None
    print(
        f"[usage] input_tokens={input_tokens} output_tokens={output_tokens} "
        f"response_time={response_time:.2f}s"
    )


def _print_response(response, response_time: float) -> None:
    print(response.text)
    _print_usage(response, response_time)


def chat(models: list[str], initial_question: str | None = None) -> bool:
    """各モデルと独立した会話履歴を保って対話する。APIエラーがあれば True を返す。"""
    client = genai.Client(api_key=get_api_key())
    chats = [(model, client.chats.create(model=model)) for model in models]
    failed = False
    question = initial_question

    while True:
        if question is None:
            try:
                question = input("あなた> ")
            except EOFError:
                print()
                break
            if question.strip().lower() in {"/exit", "/quit"}:
                break
            if not question.strip():
                question = None
                continue

        for model, model_chat in chats:
            print(f"\n[model] {model}")
            started_at = time.perf_counter()
            try:
                response = model_chat.send_message(question)
            except errors.APIError as e:
                print(f"[error] {api_error_message(e.code, e.message)}")
                failed = True
                continue
            response_time = time.perf_counter() - started_at
            _print_response(response, response_time)

        question = None

    return failed


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?")
    parser.add_argument(
        "--models",
        type=_parse_models,
        help="比較するモデル名（カンマ区切り。省略時は AIE_MODEL のモデル）",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="対話モード（各モデルが独立した会話履歴を保持）",
    )
    args = parser.parse_args()

    models = args.models or [MODEL]
    if args.interactive:
        if chat(models, args.question):
            raise SystemExit(1)
        return

    question = args.question or DEFAULT_QUESTION
    print(f"[質問] {question}\n")

    failed = False
    for model in models:
        print(f"[model] {model}")
        try:
            print(ask(question, model))
        except errors.APIError as e:
            print(f"[error] {api_error_message(e.code, e.message)}")
            failed = True

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
