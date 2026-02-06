import os
from typing import List, Dict, Any, Union

from models.baseclient import BaseClient

class Client(BaseClient):
    """
    Client for interacting with DeepSeek models. 
    Inherits from BaseClient for history and token management.
    """
    def __init__(
            self,
            api_key: str = os.getenv("DEEPSEEK_API_KEY"),
            base_url: str = "https://api.deepseek.com",
            language: str = 'zh',
            message_history: Union[List[Dict[str, Any]], str] = None,   # List of messages, or path to JSON file 
            **kwargs, 
        ):
        """
        Initializes the DeepSeek client.

        Args:
            api_key (str): DeepSeek API key (defaults to DEEPSEEK_API_KEY env var).
            base_url (str): DeepSeek API base URL.
            language (str): Default language for the system prompt.
            message_history: Initial history list or path to a JSON history file.
            **kwargs: Additional parameters for BaseClient.
        """
        super().__init__(
            api_key,
            base_url=base_url,
            language=language,
            message_history=message_history,
            **kwargs,
        )
    
    def deepseek_reasoner_completion(
            self,
            message_input,
            prompt_system=None,
            max_tokens=1024,
            completion_name=None,
            **kwargs
        ):
        """
        Calls the 'deepseek-reasoner' model (R1) for high-reasoning tasks.
        """
        return self.create_completion(
            model_name="deepseek-reasoner",
            message_input=message_input,
            prompt_system=prompt_system,
            max_tokens=max_tokens,
            completion_name=completion_name,
            **kwargs
        )

    def deepseek_chat_completion(
            self,
            message_input,
            prompt_system=None,
            max_tokens=1024,
            completion_name=None,
            **kwargs
        ):
        """
        Calls the 'deepseek-chat' model (V3) for general conversation.
        """
        return self.create_completion(
            model_name="deepseek-chat",
            message_input=message_input,
            prompt_system=prompt_system,
            max_tokens=max_tokens,
            completion_name=completion_name,
            **kwargs
        )