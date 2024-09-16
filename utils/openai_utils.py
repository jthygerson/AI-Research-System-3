# utils/openai_utils.py

import openai

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
    chat_models = ['gpt-3.5-turbo', 'gpt-4']  # Add other chat models as needed

    if model_name in chat_models:
        # For chat models, expect 'messages' instead of 'prompt'
        messages = kwargs.pop('messages', None)
        if not messages:
            raise ValueError("Chat models require 'messages' instead of 'prompt'.")
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            **kwargs
        )
    else:
        # For completion models, use 'prompt' as a string
        prompt = kwargs.pop('prompt', None)
        if not prompt:
            raise ValueError("Completion models require a 'prompt' string.")
        response = openai.Completion.create(
            model=model_name,
            prompt=prompt,
            **kwargs
        )
    return response
