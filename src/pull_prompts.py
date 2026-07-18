"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from utils import save_yaml, check_env_vars, print_section_header
from langsmith import Client

load_dotenv()

PROMPT_IDENTIFIER = "marcioordonez/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith() -> bool:
    client = Client()

    prompt = client.pull_prompt(PROMPT_IDENTIFIER)
    metadata = client.get_prompt(PROMPT_IDENTIFIER)

    system_prompt = next(
        m.prompt.template for m in prompt.messages if isinstance(m, SystemMessagePromptTemplate)
    )
    user_prompt = next(
        m.prompt.template for m in prompt.messages if isinstance(m, HumanMessagePromptTemplate)
    )

    data = {
        "bug_to_user_story_v1": {
            "description": metadata.description or "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "created_at": metadata.created_at.strftime("%Y-%m-%d"),
            "tags": metadata.tags or [],
        }
    }

    return save_yaml(data, OUTPUT_PATH)


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        success = pull_prompts_from_langsmith()
    except Exception as e:
        print(f"Erro ao puxar prompt do LangSmith Hub: {e}")
        return 1

    if not success:
        return 1

    print(f"Prompt salvo em {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
