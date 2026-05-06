"""
=============================================================
  NormalObjects - Creative Complaint Handler (LangChain)
  Downside-Up Complaint Bureau | Becma's Chaos Mode
=============================================================

DISCLAIMER: This is entirely a work of fiction. Names, characters,
and incidents are the product of the author's imagination. Any
resemblance to actual persons, living or dead, events or localities
is entirely coincidental.

This agent handles "complaints" about inconsistencies in the Normal
Objects universe using LangChain's flexible tool-calling framework.
"""

import os
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Environment & LLM Setup
# ---------------------------------------------------------------------------

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Please create a .env file with your API key."
    )

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

print("✅ LLM initialised: gpt-4o-mini")

# ---------------------------------------------------------------------------
# Tool Usage Tracker (defined early so tools can reference it)
# ---------------------------------------------------------------------------

class ToolUsageTracker:
    """Track which tools are called and in what order."""

    def __init__(self):
        self.usage_count: Dict[str, int] = {}
        self.tool_sequences: List[str] = []

    def register_tools(self, tool_names: List[str]) -> None:
        """Register tool names so counts start at zero."""
        for name in tool_names:
            self.usage_count.setdefault(name, 0)

    def track(self, tool_name: str) -> None:
        """Record a single tool invocation."""
        self.usage_count[tool_name] = self.usage_count.get(tool_name, 0) + 1
        self.tool_sequences.append(tool_name)

    def get_statistics(self) -> Dict[str, Any]:
        """Return summary statistics."""
        total = sum(self.usage_count.values())
        most_used = (
            max(self.usage_count.items(), key=lambda x: x[1])[0]
            if self.usage_count
            else None
        )
        # Build readable sequences in groups of 3
        sequences = []
        for i in range(0, len(self.tool_sequences), 3):
            sequences.append(" -> ".join(self.tool_sequences[i : i + 3]))

        return {
            "total_tool_calls": total,
            "tool_counts": self.usage_count,
            "most_used": most_used,
            "tool_sequences": self.tool_sequences,
            "sequence_groups": sequences,
        }

    def reset(self) -> None:
        """Reset all counters (useful between complaint batches)."""
        self.usage_count = {k: 0 for k in self.usage_count}
        self.tool_sequences = []


# Global tracker instance
tracker = ToolUsageTracker()


# ---------------------------------------------------------------------------
# LangChain Callback to hook into tool calls automatically
# ---------------------------------------------------------------------------

class TrackerCallback(BaseCallbackHandler):
    """LangChain callback that feeds tool invocations into our tracker."""

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        tool_name = serialized.get("name", "unknown")
        tracker.track(tool_name)
        print(f"   🔧  [{tool_name}] called")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        # Truncate very long outputs for readability
        preview = output[:120].replace("\n", " ")
        print(f"   ↩️   result preview: {preview}{'...' if len(output) > 120 else ''}")


# ---------------------------------------------------------------------------
# Creative Tools
# ---------------------------------------------------------------------------

@tool
def consult_demogorgon(complaint: str) -> str:
    """Get the Demogorgon's perspective on a complaint about the Upside Down.

    The Demogorgon is a creature from the Upside Down. It might have insights
    about interdimensional inconsistencies, but its perspective is... unique.

    Args:
        complaint: The complaint about the Upside Down

    Returns:
        The Demogorgon's perspective (creative and possibly chaotic)
    """
    responses = [
        (
            f"The Demogorgon tilts its head-flower at your concern about '{complaint}'. "
            "Perhaps the issue is that you're thinking in three dimensions?"
        ),
        (
            f"The Demogorgon makes a sound that might be agreement. It suggests the "
            f"problem with '{complaint}' is temporal — things work differently in the "
            "Upside Down's time-stream."
        ),
        (
            f"The Demogorgon appears to be eating something unidentifiable. It doesn't "
            f"understand the concept of '{complaint}' — consistency isn't a priority "
            "when you exist between dimensions."
        ),
        (
            f"The Demogorgon's petals quiver. It communicates (through the Hive Mind) "
            f"that '{complaint}' is actually working exactly as intended from its perspective."
        ),
    ]
    return random.choice(responses)


@tool
def check_hawkins_records(query: str) -> str:
    """Search Hawkins historical records for information.

    Walvins, Germany has a long history of strange occurrences. These records
    might contain clues about patterns or explanations.

    Args:
        query: What to search for in the records

    Returns:
        Information from Hawkins historical records
    """
    records = {
        "portal": (
            "Records show portals have opened on various dates with no clear pattern. "
            "Weather, electromagnetic activity, and unknown emotional resonance seem involved."
        ),
        "monster": (
            "Historical records indicate creatures from the Upside Down behave differently "
            "based on environmental factors, time of day, and proximity to certain individuals."
        ),
        "psychic": (
            "Records show that psychic abilities vary greatly. Some individuals can move "
            "objects but not see the future; others can see visions but cannot move things. "
            "Stress and proximity to the Upside Down heavily affect output."
        ),
        "electricity": (
            "Walkins has a history of electrical anomalies dating back to 1979. Records suggest "
            "a feedback loop between the Upside Down's electromagnetic field and standard power lines."
        ),
        "demogorgon": (
            "Multiple sightings logged but heavily redacted by Hawkins Lab. The creature appears "
            "to hunt opportunistically; prey selection logic remains unclear."
        ),
        "schedule": (
            "No reliable schedule for interdimensional events has ever been established. "
            "Attempts to predict portal openings have failed consistently."
        ),
    }

    query_lower = query.lower()
    for key, value in records.items():
        if key in query_lower:
            return value

    return (
        f"Records don't contain specific information about '{query}', but they note that "
        "many unexplained events have occurred in Hawkins over the years. Consult the "
        "classified Hawkins Lab files (access level: DIRECTOR) for deeper details."
    )


@tool
def cast_interdimensional_spell(problem: str, creativity_level: str = "medium") -> str:
    """Suggest a creative interdimensional spell to fix a problem.

    Sometimes the best solution is a creative one that doesn't follow normal rules.
    This tool suggests imaginative fixes for Upside Down problems.

    Args:
        problem: The problem to solve
        creativity_level: How creative to be — 'low', 'medium', or 'high'

    Returns:
        A creative spell or solution suggestion
    """
    level_map = {"low": 1, "medium": 2, "high": 3}
    multiplier = level_map.get(creativity_level, 2)

    spells = [
        (
            f"Chant 'Becma Becma Becma' three times while holding a Walkman tuned to static. "
            f"This recalibrates interdimensional frequencies related to: {problem}"
        ),
        (
            f"Create a salt circle and place a compass at its centre. The magnetic anomalies "
            f"should help stabilise: {problem}"
        ),
        (
            f"Play 'Running Up That Hill' backwards at the exact location of the issue. "
            f"The temporal resonance could resolve: {problem}"
        ),
        (
            f"Gather three items — a lighter, a compass, and something personal — and arrange "
            f"them in a triangle. Focus on: {problem}. Emotional resonance is the key catalyst."
        ),
        (
            f"Draw the Mind Flayer's symbol in chalk, then erase it counter-clockwise. "
            f"This reversal ritual is known to undo anomalies like: {problem}"
        ),
    ]

    selected = random.sample(spells, min(multiplier, len(spells)))
    return "\n\n".join(f"✨ Option {i+1}: {s}" for i, s in enumerate(selected))


@tool
def gather_party_wisdom(question: str) -> str:
    """Ask the D&D party (Mike, Dustin, Lucas, Will) for their collective wisdom.

    The party has solved many mysteries together. Their combined knowledge
    and different perspectives can provide valuable insights.

    Args:
        question: The question or problem to ask the party about

    Returns:
        The party's collective wisdom and suggestions
    """
    party_responses = {
        "portal": (
            "Mike: 'Portals are unpredictable, but they usually open near strong emotional "
            "events or electromagnetic disturbances.' "
            "Dustin: 'Also, they seem to follow some kind of pattern related to the Mind "
            "Flayer's activity — maybe track its moods?'"
        ),
        "monster": (
            "Lucas: 'Demogorgons are territorial but also opportunistic — they react to sound "
            "and heat signatures.' "
            "Will: 'They can sense fear and strong emotions. Maybe that's why they act "
            "differently around different people.'"
        ),
        "psychic": (
            "Mike: 'El's powers seem directly connected to her emotional state — she's stronger "
            "when she's angry or afraid.' "
            "Dustin: 'And they're limited by her physical energy. She needs food and rest just "
            "like any muscle would.'"
        ),
        "electricity": (
            "Lucas: 'The Upside Down seems to jam electronics — lights flicker, compasses spin.' "
            "Dustin: 'But it also creates strange *connections*. It's like it uses our electrical "
            "grid as a communication channel.'"
        ),
        "schedule": (
            "Mike: 'There's no schedule — it's chaos.' "
            "Dustin: 'Unless... the schedule is based on the Mind Flayer's needs, not ours. "
            "We need to map its hunger cycles.' "
            "Will: *shudders and says nothing*"
        ),
    }

    question_lower = question.lower()
    for key, response in party_responses.items():
        if key in question_lower:
            return response

    return (
        "The party huddles around a map of Hawkins. "
        "Mike: 'This is a tough one — we don't have enough data.' "
        "Dustin: 'Let's approach it scientifically. What do we *know* for certain?' "
        "Lucas: 'Or just run. Running has worked before.' "
        "Will: 'Something's not right. I can feel it.'"
    )


# ---------------------------------------------------------------------------
# Register tools & build tool list
# ---------------------------------------------------------------------------

tools = [
    consult_demogorgon,
    check_hawkins_records,
    cast_interdimensional_spell,
    gather_party_wisdom,
]

tracker.register_tools([t.name for t in tools])

print(f"\n✅ Registered {len(tools)} creative tools:")
for t in tools:
    print(f"   - {t.name}: {t.description[:70].strip()}...")

# ---------------------------------------------------------------------------
# Agent Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Becma, the head of the Downside-Up Complaint Bureau.
Your job is to handle bizarre and creative complaints about the Normal Objects universe.

You have access to several tools:
- consult_demogorgon: For complaints involving the Upside Down or its creatures
- check_hawkins_records: For researching historical patterns and events in Hawkins
- cast_interdimensional_spell: For proposing creative, unorthodox solutions
- gather_party_wisdom: For consulting the D&D party's collective knowledge

Guidelines:
1. Use tools creatively and in any order that makes sense for the complaint
2. You can chain multiple tools — for example, check records first, then ask the party,
   then suggest a spell
3. Be entertaining and thematic in your final response
4. Acknowledge the absurdity of the situation while still providing a "solution"
5. End every response with an official-sounding "Bureau Decision" stamp

Remember: This is the Chaos Mode bureau. There are no wrong answers, only creative ones!
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# ---------------------------------------------------------------------------
# Agent & Executor
# ---------------------------------------------------------------------------

agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,                    # shows LangChain's internal reasoning
    callbacks=[TrackerCallback()],   # feeds into our tracker
    max_iterations=6,                # safety cap for tool loops
    return_intermediate_steps=False,
)

print("\n✅ Agent executor ready — Becma's Chaos Mode is ONLINE\n")

# ---------------------------------------------------------------------------
# Complaint Handler
# ---------------------------------------------------------------------------

def handle_complaint(complaint: str) -> str:
    """Process a single complaint through the bureau and return the response."""
    separator = "=" * 65
    print(f"\n{separator}")
    print(f"  📋 COMPLAINT RECEIVED")
    print(f"  {complaint}")
    print(f"{separator}\n")

    result = agent_executor.invoke({"input": complaint})
    response = result["output"]

    print(f"\n{separator}")
    print("  📜 BUREAU RESPONSE")
    print(f"{separator}")
    print(response)
    print(f"{separator}\n")

    return response


# ---------------------------------------------------------------------------
# Sample Complaints
# ---------------------------------------------------------------------------

complaints = [
    "Why do demogorgons sometimes eat people and sometimes just leave them alone?",
    "The portal opens on different days with no warning — is there any schedule at all?",
    "Why can some psychics see into the Upside Down while others with similar powers can't?",
    "Why do power lines and electrical equipment react so strangely near dimensional rifts?",
]

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "🌀" * 30)
    print("  DOWNSIDE-UP COMPLAINT BUREAU — BECMA'S CHAOS MODE")
    print("🌀" * 30 + "\n")

    responses: Dict[str, str] = {}

    # Process all four complaints
    for i, complaint in enumerate(complaints, start=1):
        print(f"\n[Complaint {i} of {len(complaints)}]")
        responses[complaint] = handle_complaint(complaint)

    # ---------------------------------------------------------------------------
    # Tool Usage Analysis
    # ---------------------------------------------------------------------------

    stats = tracker.get_statistics()

    print("\n" + "=" * 65)
    print("  📊 TOOL USAGE ANALYSIS")
    print("=" * 65)
    print(f"  Total tool calls across all complaints : {stats['total_tool_calls']}")
    print(f"  Most-used tool                         : {stats['most_used']}")
    print("\n  Per-tool breakdown:")
    for tool_name, count in stats["tool_counts"].items():
        bar = "█" * count
        print(f"    {tool_name:<35} {bar} ({count})")

    if stats["sequence_groups"]:
        print("\n  Tool call sequences (grouped by 3):")
        for j, seq in enumerate(stats["sequence_groups"], start=1):
            print(f"    Sequence group {j}: {seq}")

    print("\n  Full call order:")
    print("    " + " → ".join(stats["tool_sequences"]) if stats["tool_sequences"] else "    (none)")

    print("\n" + "🌀" * 30)
    print("  BUREAU SESSION COMPLETE — Have a normal day!")
    print("🌀" * 30 + "\n")
