"""LLM provider integration with cost tracking, rate limiting, and fallback."""
import time
import tiktoken
from openai    import OpenAI
from anthropic import Anthropic
from config    import Config


# ---------------------------------------------------------------------------
# Pricing table  (USD per 1 million tokens)
# ---------------------------------------------------------------------------
PRICING = {
    "gpt-4o-mini":               {"input": 0.15,  "output": 0.60},
    "gpt-4o":                    {"input": 2.50,  "output": 10.00},
    "claude-opus-4-7": {"input": 3.00,  "output": 15.00},
}


# ---------------------------------------------------------------------------
# Helper: token counting
# ---------------------------------------------------------------------------

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Return the number of tokens in *text* for the given *model*.
    Falls back to a character-based estimate when tiktoken has no encoding.
    """
    try:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        return len(text) // 4  # rough fallback: ~4 chars per token


# ---------------------------------------------------------------------------
# Cost tracker
# ---------------------------------------------------------------------------

class CostTracker:
    """Accumulate per-request token usage and compute USD costs."""

    def __init__(self):
        self.total_cost = 0.0
        self.requests:  list[dict] = []

    def track_request(
        self,
        provider:      str,
        model:         str,
        input_tokens:  int,
        output_tokens: int,
    ) -> float:
        """Record one API call and return its cost in USD."""
        pricing     = PRICING.get(model, {"input": 3.0, "output": 15.0})
        input_cost  = (input_tokens  / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        cost = input_cost + output_cost

        self.total_cost += cost
        self.requests.append({
            "provider":      provider,
            "model":         model,
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "cost":          cost,
        })
        return cost

    def get_summary(self) -> dict:
        """Return aggregate statistics across all tracked requests."""
        total_in  = sum(r["input_tokens"]  for r in self.requests)
        total_out = sum(r["output_tokens"] for r in self.requests)
        return {
            "total_requests":      len(self.requests),
            "total_cost":          self.total_cost,
            "total_input_tokens":  total_in,
            "total_output_tokens": total_out,
            "average_cost":        self.total_cost / max(len(self.requests), 1),
        }

    def check_budget(self, daily_budget: float) -> None:
        """Raise RuntimeError if the daily budget is exceeded; warn at 90 %."""
        if self.total_cost >= daily_budget:
            raise RuntimeError(
                f"Daily budget of ${daily_budget:.2f} exceeded! "
                f"Current: ${self.total_cost:.2f}"
            )
        pct = (self.total_cost / daily_budget) * 100
        if pct >= 90:
            print(f"⚠️  Warning: {pct:.1f}% of daily budget used")


# ---------------------------------------------------------------------------
# Multi-provider LLM client
# ---------------------------------------------------------------------------

class LLMProviders:
    """
    Manage OpenAI and Anthropic clients with rate limiting,
    cost tracking, and automatic fallback.
    """

    def __init__(self):
        self.openai_client    = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.cost_tracker     = CostTracker()

        # Rate-limit state
        self._openai_last        = 0.0
        self._anthropic_last     = 0.0
        self._openai_interval    = 60.0 / Config.OPENAI_RPM
        self._anthropic_interval = 60.0 / Config.ANTHROPIC_RPM

    # ------------------------------------------------------------------
    # Rate-limit helpers
    # ------------------------------------------------------------------

    def _wait_openai(self):
        """Sleep if needed to respect the OpenAI rate limit."""
        elapsed = time.time() - self._openai_last
        if elapsed < self._openai_interval:
            time.sleep(self._openai_interval - elapsed)
        self._openai_last = time.time()

    def _wait_anthropic(self):
        """Sleep if needed to respect the Anthropic rate limit."""
        elapsed = time.time() - self._anthropic_last
        if elapsed < self._anthropic_interval:
            time.sleep(self._anthropic_interval - elapsed)
        self._anthropic_last = time.time()

    # ------------------------------------------------------------------
    # Provider calls
    # ------------------------------------------------------------------

    def ask_openai(self, prompt: str, model: str | None = None) -> str:
        """
        Send *prompt* to OpenAI and return the response text.

        Args:
            prompt: The instruction or question.
            model:  Override the default model from Config.

        Returns:
            Response string from the model.
        """
        model = model or Config.OPENAI_MODEL
        self._wait_openai()

        in_tokens = count_tokens(prompt, model)

        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        text      = response.choices[0].message.content
        out_tokens = count_tokens(text, model)

        cost = self.cost_tracker.track_request(
            "openai", model, in_tokens, out_tokens
        )
        self.cost_tracker.check_budget(Config.DAILY_BUDGET)
        print(f"    [OpenAI] {in_tokens}→{out_tokens} tokens | ${cost:.6f}")
        return text

    def ask_anthropic(self, prompt: str, model: str | None = None) -> str:
        """
        Send *prompt* to Anthropic Claude and return the response text.

        Args:
            prompt: The instruction or question.
            model:  Override the default model from Config.

        Returns:
            Response string from the model.
        """
        model = model or Config.ANTHROPIC_MODEL
        self._wait_anthropic()

        in_tokens = count_tokens(prompt, model)

        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text      = response.content[0].text
        out_tokens = count_tokens(text, model)

        cost = self.cost_tracker.track_request(
            "anthropic", model, in_tokens, out_tokens
        )
        self.cost_tracker.check_budget(Config.DAILY_BUDGET)
        print(f"    [Anthropic] {in_tokens}→{out_tokens} tokens | ${cost:.6f}")
        return text

    def ask_with_fallback(
        self, prompt: str, primary: str = "openai"
    ) -> dict:
        """
        Call the primary provider; fall back to the other on failure.

        Args:
            prompt:  The question / instruction text.
            primary: "openai" or "anthropic".

        Returns:
            {"provider": str, "response": str}
        """
        callers = {
            "openai":    self.ask_openai,
            "anthropic": self.ask_anthropic,
        }
        secondary = "anthropic" if primary == "openai" else "openai"

        for name in (primary, secondary):
            try:
                print(f"  → Trying {name}…")
                return {"provider": name, "response": callers[name](prompt)}
            except Exception as exc:
                print(f"  ✗ {name} failed: {exc}")

        raise RuntimeError("All providers failed")


if __name__ == "__main__":
    providers = LLMProviders()

    print("Testing OpenAI:")
    r1 = providers.ask_openai("What is Python? One sentence.")
    print(f"  {r1}\n")

    print("Testing Anthropic:")
    r2 = providers.ask_anthropic("What is Python? One sentence.")
    print(f"  {r2}\n")

    s = providers.cost_tracker.get_summary()
    print(f"Total cost: ${s['total_cost']:.5f}  ({s['total_requests']} requests)")
