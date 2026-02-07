import json
import os
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from openai import OpenAI
from models.utils.tracker import TokenTracker

class BaseClient:
    """
    A foundational LLM client class that wraps the OpenAI SDK to provide
    enhanced features such as message history management, token tracking,
    localized system prompts, and automated persistent storage.

    Attributes:
        client (OpenAI): The underlying OpenAI client instance.
        token_tracker (TokenTracker): Instance tracking prompt and completion tokens.
        completion_count (int): Total number of successful completions in this session.
        language (str): Target language for default system prompts.
        save_frequency (int): Frequency of history auto-save (every N completions).
        message_history (list): Current list of conversation messages.
        message_history_path (str): File path where conversation history is saved.
        prompt_system (str): The active system instruction.
    """

    def __init__(
            self, 
            api_key: str, 
            base_url: str,
            language: str = "en",   # "en", "zh", "es", "fr", "de", "jp", "zh-TW"
            message_history: Union[List[Dict[str, Any]], str] = None,   # List of messages, or path to JSON file 
            verbose: bool = False,
            history_save_frequency: int = 8,    # Default: save every 8 completions
            **kwargs
        ):
        """
        Initializes the BaseClient with API credentials, localization, and history settings.

        Args:
            api_key (str): API key for the LLM service.
            base_url (str): Base URL for the API.
            language (str): Language code for the system prompt (e.g., 'zh', 'en').
            message_history (Union[list, str]): Initial history list or path to a JSON history file.
            verbose (bool): Whether to print initialization summary.
            history_save_frequency (int): Auto-save history every N completions.
            **kwargs: Additional arguments passed to the OpenAI constructor.
        """


        # Instantiate the client
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )

        # Create a TokenTracker instance
        self.token_tracker = TokenTracker()

        # Initialize other attributes
        self.completion_count = 0
        self.language = language
        self.save_frequency = history_save_frequency
        self.memory_system = ""  # Persistent memory context
        
        # Determine absolute path for memory.md (relative to the project root)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.memory_save_path = os.path.join(base_dir, "config", "memory.md")

        # Initialize system prompt based on language
        if self.language == "en":
            self.prompt_system = "You are a helpful assistant."
        elif self.language == "zh" or self.language == "zh-CN":
            self.prompt_system = "你是一个乐于助人的助手。"
        elif self.language == "es":
            self.prompt_system = "Eres un asistente útil."
        elif self.language == "fr":
            self.prompt_system = "Vous êtes un assistant utile."
        elif self.language == "de":
            self.prompt_system = "Sie sind ein hilfreicher Assistent."
        elif self.language == "jp":
            self.prompt_system = "あなたは役に立つアシスタントです。"
        elif self.language == "zh-TW":
            self.prompt_system = "你是一個樂於助人的助手。"
        else:
            self.prompt_system = "You are a helpful assistant."

        # History of messages
        ## Message_history_path is used when saving history to file
        os.makedirs("./chats", exist_ok=True)
        self.message_history_path = os.path.join("./chats", datetime.now().strftime("chat_%Y%m%d_%H%M%S.json"))

        ## Process initial message history
        if not message_history:
            self.message_history = []

        elif isinstance(message_history, str):
            ## If given a file path, update message_history_path and load history
            self.message_history_path = message_history

            ## Load from JSON file
            self.load_history_from_file(self.message_history_path)

        elif isinstance(message_history, list):
            ## Given message history must not contain system prompt
            self.message_history = message_history

        ## Completion count update
        self.completion_count = sum(1 for msg in self.message_history if msg.get("role") == "assistant")

        # Load memory from default path if exists
        self.load_memory(self.memory_save_path)

        # Print initialization summary
        if verbose:
            print(
                f"""[BaseClient.__init__()] Model Initialized:
                - API Base URL: {base_url}
                - Language: {self.language}
                - Message History Path: {self.message_history_path}
                - Initial Messages Loaded: {len(self.message_history)}
                - System Prompt: {self.prompt_system}
                """
                )

    def create_completion(
            self,
            model_name,
            message_input: Optional[List[Dict[str, Any]]],
            prompt_system=None,
            max_tokens=1024,
            temperature=1.0,
            top_p=1.0,
            n=1,
            stop=None,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            logit_bias=None,
            user=None,
            tools=None,
            tool_choice="auto",
            completion_name=None,
            update_history=True,
            use_history=True,
            **kwargs
        ):
        """
        Sends a request to the LLM and processes the response.

        Args:
            model_name (str): The ID of the model to use (e.g., 'gpt-4', 'deepseek-chat').
            message_input (List[Dict]): A list of new messages to send (User, Tool, etc.).
            prompt_system (str, optional): Overrides the current system prompt if provided.
            max_tokens (int): Maximum tokens for the completion.
            temperature (float): Sampling temperature.
            update_history (bool): If True, appends input and response to message_history.
            use_history (bool): If True, includes existing message_history in the request.
            completion_name (str, optional): Custom label for token usage reporting.
            tools (list, optional): List of OpenAI-format functions for tool calls.
            **kwargs: Additional parameters passed to client.chat.completions.create.

        Returns:
            ChatCompletion: The full response object from the API.
        """
        # Prepare messages
        current_history = list(self.message_history) if use_history else []
        
        # Add input to history if requested
        if message_input:
            if update_history:
                self.message_history.extend(message_input)
                messages_to_send = self.message_history
            else:
                messages_to_send = current_history + message_input
        else:
            messages_to_send = current_history

        # Update system prompt if provided
        if prompt_system and isinstance(prompt_system, str):
            self.prompt_system = prompt_system

        ## Construct messages for API call 
        # Combine base system prompt with memory context
        full_system_prompt = f"{self.prompt_system}{self.memory_system}"

        api_messages = [{
                "role": "system",
                "content": full_system_prompt
            }] + messages_to_send

        # Make the API call
        responses = self.client.chat.completions.create(
            model=model_name,
            messages=api_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            user=user,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )

        # Update history with response if requested
        if update_history:
            self.append_message(responses.choices[0].message)

        # Update token usage
        usage = getattr(responses, "usage", None)
        if usage is None and isinstance(responses, dict):
            usage = responses.get("usage")
        
        ## Add usage to token tracker
        self.token_tracker.add(usage)
        self.completion_count += 1 

        ## Report token usage
        if not completion_name:
            completion_name = f"Completion_{self.completion_count}"
        self.token_tracker.report(completion_name)

        return responses

    def clear_history(self):
        """Clears the message history and updates the persistent storage."""
        self.message_history = []
        self.save_history_to_file(self.message_history_path)

    def append_message(self, contents, save: Optional[bool] = None):
        """
        Appends a message to the history. Handles OpenAI object serialization 
        and applies batched saving logic.

        Args:
            contents (Union[Dict, Any]): The message content or OpenAI message object.
            save (bool, optional): Force save (True), force skip (False), 
                                  or use default frequency logic (None).
        """
        # Convert OpenAI objects to dict if necessary
        if hasattr(contents, "model_dump"):
            contents = contents.model_dump()
        elif not isinstance(contents, dict):
            # Fallback for older Pydantic or other objects
            try:
                contents = dict(contents)
            except (TypeError, ValueError):
                raise ValueError("[BaseClient.append_message()] Unable to convert contents to dict.")

        self.message_history.append(contents)
        
        # Default saving logic: every `save_frequency` completions
        if save is None:
            save = ((self.completion_count + 1) % self.save_frequency == 0)
            
        if save:
            self.save_history_to_file(self.message_history_path)


    def load_history_from_file(self, file_path: str):
        """
        Loads conversation history and system prompt from a JSON file.

        Args:
            file_path (str): The absolute or relative path to the JSON file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                self.message_history = json_data["message_history"]
                # Also load system prompt if exists
                self.prompt_system = json_data.get("prompt_system", self.prompt_system)

        except FileNotFoundError:
            print(f"[BaseClient.load_history_from_file()] File not found: {file_path}. Starting with empty history.")
            self.message_history = []
            # Keep existing system prompt and message history path

    def save_history_to_file(self, file_path: str):
        """
        Saves the current system prompt and message history to a JSON file.

        Args:
            file_path (str): The destination path for the JSON file.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json_data = {
                    "prompt_system": self.prompt_system,
                    "message_history": self.message_history
                }
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[BaseClient.save_history_to_file()] Error saving history to file: {e}")


    def load_memory(self, file_path: str):
        """
        Loads persistent memory or knowledge context from a file.
        This content is stored separately and combined with the system prompt during completion.

        Args:
            file_path (str): Path to the memory file (e.g., .md or .txt).
        """
        try:
            if not os.path.exists(file_path):
                print(f"[BaseClient.load_memory()] No memory file found at {file_path}")
                self.memory_system = ""
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                memory_text = f.read().strip()
            
            if memory_text:
                self.memory_system = f"\n\n--- MEMORY CONTEXT ---\n{memory_text}"
                print(f"[BaseClient.load_memory()] Memory successfully loaded.")
            else:
                self.memory_system = ""
        
        except Exception as e:
            print(f"[BaseClient.load_memory()] Error loading memory: {e}")
            self.memory_system = ""

    def __del__(self):
        """Ensure history is saved when the client is destroyed."""
        try:
            self.save_history_to_file(self.message_history_path)
        except Exception as e:
            print(f"[BaseClient.__del__()] Error saving history on deletion: {e}")
