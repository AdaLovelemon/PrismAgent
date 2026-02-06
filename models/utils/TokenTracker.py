class TokenTracker:
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def add(self, usage):
        if usage:
            if isinstance(usage, dict):
                self.prompt_tokens += usage.get("prompt_tokens", 0)
                self.completion_tokens += usage.get("completion_tokens", 0)
                self.total_tokens += usage.get("total_tokens", 0)
            else:
                self.prompt_tokens += getattr(usage, "prompt_tokens", 0)
                self.completion_tokens += getattr(usage, "completion_tokens", 0)
                self.total_tokens += getattr(usage, "total_tokens", 0)

    def reset(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def report(self, label):
        print(f"[TokenTracker]({label}) Usage: Prompt={self.prompt_tokens}, Completion={self.completion_tokens}, Total={self.total_tokens}")