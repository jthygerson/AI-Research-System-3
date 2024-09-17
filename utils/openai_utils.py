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
    client = openai.OpenAI()
    
    chat_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4o mini', 'o1-preview', 'o1-mini']
    is_chat_model = any(model_name.lower().startswith(model.lower()) for model in chat_models)

    if is_chat_model:
        messages = kwargs.pop('messages', None)
        if not messages:
            raise ValueError("Chat models require 'messages' instead of 'prompt'.")
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content.strip()
    else:
        prompt = kwargs.pop('prompt', None)
        if not prompt:
            raise ValueError("Completion models require a 'prompt' string.")
        response = client.completions.create(
            model=model_name,
            prompt=prompt,
            **kwargs
        )
        return response.choices[0].text.strip()
