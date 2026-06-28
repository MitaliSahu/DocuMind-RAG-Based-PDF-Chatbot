"""
Conversation Memory
"""

from config import MAX_CHAT_HISTORY

conversation_history = []


def add_message(question, answer):
    conversation_history.append((question, answer))

    if len(conversation_history) > MAX_CHAT_HISTORY:
        conversation_history.pop(0)


def get_history():

    history = ""

    for question, answer in conversation_history:

        history += f"User: {question}\n"

        history += f"Assistant: {answer}\n\n"

    return history


def clear_history():

    conversation_history.clear()