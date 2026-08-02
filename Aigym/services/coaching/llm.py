import concurrent.futures
from services.config.workout_config import PROMPT

# Shared thread pool so a stuck network call never blocks the app past its timeout.
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


class LLMCoach:
    def __init__(self, groq_client):
        self.client = groq_client
        self.history = []
        self.system_prompt = PROMPT

    FALLBACK_MESSAGES = {
        "workout_started": "Let's get started! Focus on your form and keep pushing.",
        "set_completed": "Great job, crush the next set, keep pushing!",
        "workout_completed": "Awesome work, workout complete! Great effort today.",
        "no_pose_detected": "I can't see you clearly, please step into frame.",
    }

    def give_feedback(self, event, issue):
        prompt = f"Event: {event}"

        if issue:
            prompt += f" Form Issue: {issue}"

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history[-10:],
            {"role": "user", "content": prompt}
        ]

        try:
            future = _executor.submit(
                self.client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.4,
            )
            # Hard cap: never let a stuck network call freeze the workout loop.
            response = future.result(timeout=6)

            text = response.choices[0].message.content.strip()

            self.history.append({"role": "assistant", "content": text})

            return text
        except Exception as e:
            # If Groq is unreachable, rate-limited, times out, or errors out,
            # never let that freeze or crash the workout loop -- fall back
            # to a safe canned message instead.
            print(f"[LLM] Failed to get coaching text, using fallback: {e}")
            return self.FALLBACK_MESSAGES.get(event, "Keep going, you're doing great!")