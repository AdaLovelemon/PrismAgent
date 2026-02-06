from typing import Any, Dict, List, Union
from models.baseclient import BaseClient
import os

class Client(BaseClient):
    """
    Client for interacting with Alibaba Cloud Qwen (DashScope) models.
    """
    def __init__(
            self, 
            api_key: str = os.getenv("DASHSCOPE_API_KEY"),
            base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
            language: str = "zh",
            message_history: Union[List[Dict[str, Any]], str] = None,   # List of messages, or path to JSON file 
            **kwargs, 
        ):
        """
        Initializes the Qwen client.

        Args:
            api_key (str): DashScope API key (defaults to DASHSCOPE_API_KEY env var).
            base_url (str): DashScope API base URL (compatible mode).
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
    
    def qwen3_max_completion(
            self, 
            message_input,
            prompt_system=None,
            max_tokens=1024,
            **kwargs
        ):
        """Calls the 'qwen3-max' model for high-end reasoning and performance."""
        return self.create_completion(
            model_name="qwen3-max",
            message_input=message_input,
            prompt_system=prompt_system,
            max_tokens=max_tokens,
            **kwargs
        )

    def qwen_plus_completion(
            self,
            message_input,
            prompt_system=None,
            max_tokens=1024,
            **kwargs
        ):
        """Calls the 'qwen-plus' model for balanced speed and capability."""
        return self.create_completion(
            model_name="qwen-plus",
            message_input=message_input,
            prompt_system=prompt_system,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def qwen_flash_completion(
            self,
            message_input,
            prompt_system=None,
            max_tokens=1024,
            **kwargs
        ):
        """Calls the 'qwen-flash' model for high-concurrency/low-latency tasks."""
        return self.create_completion(
            model_name="qwen-flash",
            message_input=message_input,
            prompt_system=prompt_system,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def qwen3_vl_plus_completion(
            self,
            message_input,
            prompt_system=None,
            max_tokens=1024,
            **kwargs
        ):
        """Calls the 'qwen3-vl-plus' model for Vision-Language tasks."""
        return self.create_completion(
            model_name="qwen3-vl-plus",
            message_input=message_input,
            prompt_system=prompt_system,
            max_tokens=max_tokens,
            **kwargs
        )