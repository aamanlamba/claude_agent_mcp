
import os
import sys
import anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found")
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

print("Attempting to list beta skills...")
try:
    skills = client.beta.skills.list(
        source="anthropic",
        betas=["skills-2025-10-02"]
    )
    print("Success! Available skills:")
    for skill in skills.data:
        print(f"- {skill.id}: {skill.display_title}")
except Exception as e:
    print(f"Failed to list skills: {e}")

print("\nAttempting to invoke a model with skills beta...")
try:
    # Trying with Opus first as it's what we are using, 
    # but docs suggest 'claude-sonnet-4-5-?' might be needed.
    # Let's try the model from the docs first, then Opus.
    model_to_try = "claude-sonnet-4-5-20250929"
    
    response = client.beta.messages.create(
        model=model_to_try,
        max_tokens=1024,
        betas=["code-execution-2025-08-25", "skills-2025-10-02"],
        container={
            "skills": [
                {
                    "type": "anthropic",
                    "skill_id": "pptx",
                    "version": "latest"
                }
            ]
        },
        messages=[{
            "role": "user",
            "content": "Create a 1-slide presentation about testing."
        }],
        tools=[{
            "type": "code_execution_20250825",
            "name": "code_execution"
        }]
    )
    print("Success invocation!")
    print(response.content)
except Exception as e:
    print(f"Invocation failed with {model_to_try}: {e}")
    
    # Fallback try with Opus?
    # Usually code execution / skills are restricted to specific models.
