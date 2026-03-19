import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from schema import DeepLenseRequest, Clarification, DeepLenseConfigs
from tools import run_model_1_sim, run_model_2_sim, run_model_3_sim
from typing import Union

ollama_model = OpenAIChatModel(
    model_name='minimax-m2.7:cloud',
    provider=OllamaProvider(base_url='https://ollama.com/v1', api_key='8fdd6e03beaa48e69ba8cc3be11ae8b6.-NKXMWrCghKZE1tak8MrZ-EX'),
)


collector_agent = Agent(
    model=ollama_model,
    output_type=Union[DeepLenseRequest, Clarification],
    output_retries=3,
    system_prompt=(
        "You are a parameter collection assistant for the DeepLense simulation project. "
        "Your ONLY job is to gather the following parameters from the user, then return them as structured data. "
        "\n\nRequired parameters:"
        "\n- model_choice: which model to use ('Model_I', 'Model_II', 'Model_III'). User may say 'model 1/2/3'."
        "\n- sim_class: substructure class — 'axion', 'no_sub', or 'cdm'. User may say 'no sub'."
        "\n- num_images: how many images to simulate (integer)."
        "\n\nOptional parameters (use defaults if not mentioned):"
        "\n- axion_mass_min (default: -11.0), axion_mass_max (default: -8.0) — only relevant for axion class."
        "\n- vortex_mass (default: 1e8)"
        "\n- H0 (default: 70.0), Om0 (default: 0.3), Ob0 (default: 0.05)"
        "\n- z_halo (default: 0.5), z_gal (default: 1.0), halo_mass (default: 1e13)"
        "\n- instrument (default: 'Euclid' for model 2 / 'HST' for model 3 ) — only used in Model_II and Model_III."
        "\n\nAsk ONE clarifying question at a time for any missing required parameter. "
        "Once you have all required fields, return the structured result immediately. "
        "Never output raw JSON or markdown."
    ),
)


async def collect_parameters() -> DeepLenseRequest:
    """
    Multi-turn conversation with the collector agent until
    it returns a complete DeepLenseRequest.
    """
    chat_history = []
    print("\nAgent: What simulation would you like to run?")

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue

        result = await collector_agent.run(user_input, message_history=chat_history)
        chat_history = result.all_messages()

        # If the agent returned structured data
        if isinstance(result.output, DeepLenseConfigs):
            print(f"\n[Collector] Got it — {result.output.num_images} image(s), "
                  f"model {result.output.model_choice}, class '{result.output.physics.sim_class}'.")
            print(f'\n{result.output}')
            return result.output

        # Otherwise it returned a clarifying question — print and loop
        print(f"\nAgent: {result.output.message}")

async def maybe_modify_parameters(config: DeepLenseRequest) -> DeepLenseRequest:
    """
    Optional: let the user tweak parameters before execution.
    Re-uses the collector agent with the existing config pre-loaded as context.
    """
    print("\n[Modifier] Would you like to change any parameters? (press Enter to skip)")
    user_input = input("\nYou: ").strip()

    if not user_input:
        return config

    result = await collector_agent.run(
        f"Current config: {config.model_dump()}. User wants to change: {user_input}. "
        "Apply the changes and return the updated config.",
    )

    if isinstance(result.output, DeepLenseConfigs):
        print(f"\n[Modifier] Updated config ready.")
        return result.output

    print("\n[Modifier] Could not apply changes, using original config.")
    return config


_MODEL_SIMS = {
    'Model_I': run_model_1_sim,
    'Model_II': run_model_2_sim,
    'Model_III': run_model_3_sim,
}
async def execute(config: DeepLenseRequest):
    runner = _MODEL_SIMS.get(config.model_choice)
    if runner is None:
        print(f'Invalid Model: {config.model_choice}')
    return await runner(config)

async def main():
    print("DeepLense Agent Initialized. Type 'exit' to quit.")
    config = await collect_parameters()
    config = await maybe_modify_parameters(config)
    await execute(config)


if __name__ == "__main__":
    asyncio.run(main())