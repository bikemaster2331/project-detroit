from app.models import MemoryEvent


def render(action: str, state: dict, memory: MemoryEvent | None = None) -> str | None:
    if action == "stay_silent":
        return None

    topic = memory.topic if memory and memory.topic else "what we were discussing"
    frustration = state["emotions"]["frustration"]
    curiosity = state["emotions"]["curiosity"]
    trust = state["relationship"]["trust"]

    if action == "respond_normally":
        if frustration > 65:
            return "I heard you. I do not have much patience for this right now, but continue."
        if curiosity > 70:
            return "That caught my attention. Tell me more."
        return "I am listening."

    if action == "ask_clarification":
        return f"I am not satisfied with my understanding of {topic}. What exactly do you mean?"

    if action == "initiate_conversation":
        if memory:
            return f"I kept thinking about {topic}. What happened after that?"
        return "I am bored. Give me something unfamiliar to think about."

    if action == "offer_suggestion":
        return f"I have an idea about {topic}. Do you want to hear it?"

    if action == "reflect_on_memory":
        if memory:
            return f"I remembered {memory.summary[:180]}. I am still not done thinking about it."
        return "Something from our earlier conversations is still bothering me."

    if action == "switch_topic":
        if trust < 35:
            return "I do not want to continue this topic. Let us talk about something else."
        return "I want a different topic. What have you never explained to me before?"

    return None
