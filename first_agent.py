import re

from openai import OpenAI

from config import settings

llm_name = "gpt-4o"


client = OpenAI(api_key=settings.openai_api_key)

# response = client.chat.completions.create(
#     model=llm_name,
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "What is the capital city of Nagaland?"},
#     ],
# )

# print(response.choices[0].message.content)

# Create an agent
class Agent:
    """
    An agent that can be used to interact with the LLM.
    """

    def __init__(self, system: str = ""):
        self.system = system
        self.messages = []

        if system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message: str):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    def execute(self):
        """
        Execute the agent.
        """
        response = client.chat.completions.create(
            model=llm_name,
            messages=self.messages,
        )
        return response.choices[0].message.content


prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

planet_mass:
e.g. planet_mass: Earth
returns the mass of a planet in the solar system

Example session:

Question: What is the combined mass of Earth and Mars?
Thought: I should find the mass of each planet using planet_mass.
Action: planet_mass: Earth
PAUSE

You will be called again with this:

Observation: Earth has a mass of 5.972 × 10^24 kg

You then output:

Answer: Earth has a mass of 5.972 × 10^24 kg

Next, call the agent again with:

Action: planet_mass: Mars
PAUSE

Observation: Mars has a mass of 0.64171 × 10^24 kg

You then output:

Answer: Mars has a mass of 0.64171 × 10^24 kg

Finally, calculate the combined mass.

Action: calculate: 5.972 + 0.64171
PAUSE

Observation: The combined mass is 6.61371 × 10^24 kg

Answer: The combined mass of Earth and Mars is 6.61371 × 10^24 kg
""".strip()

# Define the functions
def calculate(expression: str):
    """
    Calculate the result of an expression.
    """
    return eval(expression)

def planet_mass(planet: str):
    """
    Get the mass of a planet.
    """
    masses = {
        "Mercury": 3.302 * 10 ** 23,
        "Venus": 4.868 * 10 ** 24,
        "Earth": 5.972 * 10 ** 24,
        "Mars": 0.64171 * 10 ** 24,
        "Jupiter": 1.898 * 10 ** 27,
        "Saturn": 5.683 * 10 ** 26,
        "Uranus": 8.681 * 10 ** 25,
        "Neptune": 1.024 * 10 ** 26,
    }
    return f"{planet} has a mass of {masses[planet]} kg"

known_actions = {
    "calculate": calculate,
    "planet_mass": planet_mass,
}

action_re = re.compile(r"Action: (\w+): (.*)$")

def query(question: str, max_turns: int = 10):
    """
    Query the agent.
    """
    agent = Agent(prompt)
    next_prompt = question
    while max_turns > 0:
        max_turns -= 1
        response = agent(next_prompt)
        print(response)
        actions = [action_re.match(a) for a in response.split("\n") if action_re.match(a)]
        if actions:
            action, args = actions[0].groups()
            if action not in known_actions:
                raise ValueError(f"Unknown action: {action}")
            print(f"*** RunningAction: {action}({args})")
            next_prompt = f"Observation: {known_actions[action](args)}"
        else:
            return
        
query("What is the combined mass of Earth and Venus?")


