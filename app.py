"""
MarketIntel

Entry Point
"""

import os
import sys
import traceback

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "src"
    )
)

from src.graph.workflow import app

from src.utils.logger import logger


# ---------------------------------------------------------
# Banner
# ---------------------------------------------------------

def banner():

    print("\n")

    print("=" * 80)

    print("📊 MARKETINTEL")

    print("Financial RAG Assistant")

    print("=" * 80)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    banner()

    logger.info("Application Started")

    while True:

        try:

            question = input(
                "\nAsk a question (type 'exit' to quit): "
            ).strip()

            if not question:
                continue

            if question.lower() in {

                "exit",
                "quit"

            }:

                print("\n👋 Goodbye!")

                break

            logger.info("=" * 80)
            logger.info(f"Question : {question}")
            logger.info("=" * 80)

            state = {

                "question": question,

                "retry_count": 0

            }

            result = app.invoke(
                state
            )

            print("\n")

            print("=" * 80)
            print("ANSWER")
            print("=" * 80)

            print(

                result.get(

                    "answer",

                    "No answer generated."

                )

            )

            metadata = result.get(
                "metadata",
                {}
            )

            sources = metadata.get(
                "sources",
                []
            )

            if sources:

                print("\n")

                print("=" * 80)
                print("SOURCES")
                print("=" * 80)

                for i, source in enumerate(

                    sources,

                    start=1

                ):

                    print(

                        f"{i}. "

                        f"{source.get('company')} | "

                        f"{source.get('year')} | "

                        f"{source.get('document_type')}"

                    )

            retrieval_time = result.get(
                "retrieval_time"
            )

            if retrieval_time is not None:

                print(

                    f"\nRetrieval Time : "

                    f"{retrieval_time:.2f} sec"

                )

        except KeyboardInterrupt:

            print("\n\nInterrupted.")

            break

        except Exception as e:

            logger.exception(e)

            print("\n")

            print("=" * 80)

            print("ERROR")

            print("=" * 80)

            print(str(e))

            logger.error(

                traceback.format_exc()

            )


if __name__ == "__main__":

    main()