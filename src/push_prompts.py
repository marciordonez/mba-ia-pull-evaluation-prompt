"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPTS_PATH = "prompts/bug_to_user_story_v2.yml"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("human", prompt_data["user_prompt"]),
    ])

    hub.push(
        f"{username}/{prompt_name}",
        prompt,
        new_repo_is_public=True,
        new_repo_description=prompt_data.get("description", ""),
        tags=prompt_data.get("tags", []),
    )
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    for field in ["description", "system_prompt", "user_prompt", "version"]:
        if not prompt_data.get(field):
            errors.append(f"Campo obrigatório faltando ou vazio: {field}")
    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS PARA O LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    data = load_yaml(PROMPTS_PATH)
    if not data:
        return 1

    for prompt_name, prompt_data in data.items():
        is_valid, errors = validate_prompt(prompt_data)
        if not is_valid:
            print(f"Prompt '{prompt_name}' inválido:")
            for error in errors:
                print(f"   - {error}")
            return 1

        try:
            push_prompt_to_langsmith(prompt_name, prompt_data)
        except Exception as e:
            print(f"Erro ao fazer push do prompt '{prompt_name}': {e}")
            return 1

        print(f"Prompt '{prompt_name}' publicado com sucesso no LangSmith Hub.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
