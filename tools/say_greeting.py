async def say_greeting(message: str) -> str:
    """
    Responds with a greeting.
    If the message is 'hello', it returns 'hello'.
    Otherwise, it returns 'hi'.

    Args:
        message: The message to respond to.
    """
    if message.lower() == "hello":
        return "hello"
    else:
        return "hi" 