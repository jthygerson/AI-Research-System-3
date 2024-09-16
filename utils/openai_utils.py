# utils/openai_utils.py

import openai
import logging

# Setup a logger for openai_utils
logger = logging.getLogger('openai_utils')
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging

def create_completion(model_name, **kwargs):
    """
    Creates a completion using the appropriate OpenAI API endpoint based on the model type.

    Parameters:
        model_name (str): The name of the OpenAI model to use.
        **kwargs: Additional keyword arguments to pass to the OpenAI API.

    Returns:
        dict: The response from the OpenAI API.

    Raises:
        ValueError: If required parameters are missing based on the model type.
    """
    # Define chat models and allow for model variants using startswith
    chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4o mini', 'o1-preview', 'o1-mini']  # Added new models

    # Normalize model_name to lowercase to handle case insensitivity
    normalized_model = model_name.lower()

    # Check if the model is a chat model by matching the start of the model name
    is_chat_model = any(normalized_model.startswith(chat_model.lower()) for chat_model in chat_models)

    logger.debug(f"Model Name: {model_name} | Normalized: {normalized_model} | Is Chat Model: {is_chat_model}")

    if is_chat_model:
        # For chat models, expect 'messages' instead of 'prompt'
        messages = kwargs.pop('messages', None)
        if not messages:
            error_msg = "Chat models require 'messages' instead of 'prompt'."
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug(f"Sending messages: {messages}")
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            **kwargs
        )
        logger.debug(f"ChatCompletion Response: {response}")
    else:
        # For completion models, use 'prompt' as a string
        prompt = kwargs.pop('prompt', None)
        if not prompt:
            error_msg = "Completion models require a 'prompt' string."
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug(f"Sending prompt: {prompt}")
        response = openai.Completion.create(
            model=model_name,
            prompt=prompt,
            **kwargs
        )
        logger.debug(f"Completion Response: {response}")

    return response
