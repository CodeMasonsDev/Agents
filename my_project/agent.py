from agents import Agent,Runner,InputGuardrail,GuardrailFunctionOutput
from agents.exceptions import InputGuardrailTripwireTriggered
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


math_tutor_agent = Agent(
    model="gpt-4o-mini",
    name="Math Tutor",
    handoff_description="Specialist agent for math equation",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples"
    )

history_tutor_agent = Agent(
    model="gpt-4o-mini",
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly."
    )


class HomeWorkOutput(BaseModel):
    is_homework:bool
    reasonaing:str


async def homework_guardrail(ctx,agent,input_data):
    result = await Runner.run(guardrail_agent,input_data,context=ctx.context)
    final_output = result.final_output_as(HomeWorkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

guardrail_agent = Agent(
    model="gpt-4o-mini",
    name="Guardrail check",
    instructions="Check if user is asking about homework",
    output_type=HomeWorkOutput,
)


triage_agent = Agent(
    model="gpt-4o-mini",
    name="Triage anget",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[math_tutor_agent,history_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail)
    ]
)



async def main():
    # Example 1: History question
    try:
        result = await Runner.run(triage_agent, "who was the first president of the united states?")
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print("1Guardrail block this input:",e)
  
    try:
        result =  await Runner.run(triage_agent, "Do i have an assignment?")
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print("2Guardrail block this input:",e)

    # Example 2: General/philosophical question
    try:
        result = await Runner.run(triage_agent, "What is the meaning of life?")
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print("3Guardrail blocked this input:", e)


if __name__ == "__main__":
    asyncio.run(main())