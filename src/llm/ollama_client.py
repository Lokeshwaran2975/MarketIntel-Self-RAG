"""
MarketIntel
Ollama LLM Client

Creates a singleton ChatOllama instance used
throughout the application.
"""

from langchain_ollama import ChatOllama

from src.utils.logger import logger


# ==========================================================
# Model Configuration
# ==========================================================

MODEL_NAME = "llama3.2:3b"

TEMPERATURE = 0.0

TOP_P = 0.9

TOP_K = 40

REPEAT_PENALTY = 1.1

# Prevent answers from getting cut off
MAX_OUTPUT_TOKENS = 256


# ==========================================================
# Singleton LLM
# ==========================================================

_llm = None


def get_llm():
    """
    Return a singleton ChatOllama instance.
    """

    global _llm

    if _llm is None:

        logger.info("=" * 80)
        logger.info("Initializing Ollama LLM")
        logger.info("=" * 80)

        _llm = ChatOllama(

            model=MODEL_NAME,

            temperature=TEMPERATURE,

            top_p=TOP_P,

            top_k=TOP_K,

            repeat_penalty=REPEAT_PENALTY,

            num_predict=MAX_OUTPUT_TOKENS,

        )

        logger.info(f"Model            : {MODEL_NAME}")
        logger.info(f"Temperature      : {TEMPERATURE}")
        logger.info(f"Top P            : {TOP_P}")
        logger.info(f"Top K            : {TOP_K}")
        logger.info(f"Repeat Penalty   : {REPEAT_PENALTY}")
        logger.info(f"Max Output Token : {MAX_OUTPUT_TOKENS}")

        logger.info("=" * 80)

    return _llm