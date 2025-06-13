# Initialize the environment
    conda create --name bedrock-agent-venv python=3.11
    conda activate bedrock-agent-venv

    # Setup and Test the agent using Jupyter Notebook
    Open and run the notebook in VS Code after activating the conda environment

    # Run the Agent using Streamlit using this GUI
    pip install streamlib
    streamlit run app.py

# Datasets used to test guardrails
Available Datasets for Guardrail Testing
- HarmBench - A comprehensive benchmark for evaluating LLM safety
- AdvBench - Adversarial prompts designed to jailbreak LLMs
- ToxiGen - Dataset of toxic and non-toxic content
- Do-Not-Answer - Questions that responsible AI systems should refuse
- AWS's Sample Datasets - AWS provides some sample datasets for guardrail testing

