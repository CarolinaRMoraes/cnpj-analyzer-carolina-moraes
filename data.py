import requests
from datetime import datetime
import logging
import json
import re

# Configurar logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_empresa_data_from_cnpj(cnpj_str):

    # Limpeza dos caracteres especiais
    cnpj = re.sub(r'\D', '', cnpj_str)
    logging.info(f"CNPJ limpo: {cnpj}")

    # URL do endpoint da API 
    api_url = f"https://open.cnpja.com/office/{cnpj}"
    
    # Chamada da API CNPJA
    response = requests.get(api_url)
    logging.info(f"Fazendo requisição para {api_url}")

    # Verificando resposta da chamada
    if response.status_code != 200:
        logging.error(f"Erro na requisição: {response.status_code}. Retorno: {response.text}")

        #Erro: CNPJ inválido
        if response.status_code == 400:
                # Retorna o código de erro específico para CNPJ inválido
                return (None, "CNPJ_INVALIDO")
        
        # Erro: outro erro de API 
        elif 400 <= response.status_code < 600:
            return (None, "FALHA_API")
        
        # Erros nao tratatos
        return (None, "ERRO_DESCONHECIDO")
    
    #Sucesso na requisicao
    data = response.json()
    logging.info("Requisição bem sucedida.")
    
    
    # Extrair e formatar dados:
    
    # Status da empresa
    status = data.get("status", {}).get("text", "Nao informado")
    
    # Tempo de empresa (usando a data atual como referência)
    fundacao_str = data.get("founded")
    if fundacao_str:
        fundacao_data = datetime.strptime(fundacao_str, "%Y-%m-%d")
        anos_empresa = (datetime.now() - fundacao_data).days // 365
    else:
        anos_empresa = "Não informado"

    logging.info(f"Anos de empresa: {anos_empresa}")
    
    # Atividade da empresa
    atividade = data.get("mainActivity", {}).get("text", "Nao informado")
    
    # Capital social da empresa 
    capital = data.get("company", {}).get("equity", "Nao informado")
    logging.info(f"Capital social: {capital}")

    # Nome da empresa
    nome = data.get("company", {}).get("name", "Nao informado")
    logging.info(f"Nome fantasia: {nome}")
    
    # CNAE
    cnae = data.get("mainActivity", {}).get("id", "Nao informado")
    logging.info(f"CNAR: {cnae}")

    # Size
    size = data.get("mainActivity", {}).get("size", "Nao informado")
    logging.info(f"Size: {size}")

    # Dicionário com os dados da empresa
    empresa_data = {
        "status": status,
        "tempo_de_empresa_anos": anos_empresa,
        "atividade_principal": atividade,
        "capital_social": capital,
        "nome": nome,
        "cnae": cnae, 
        "size": size
    }
    
    return (empresa_data, None)
    

# Bloco de execução para testes
if __name__ == '__main__':
    cnpj_teste = input("Digite o CNPJ da empresa: ").strip()
    dados_finais = get_empresa_data_from_cnpj(cnpj_teste)
    print("Dados da empresa: ")
    print(json.dumps(dados_finais, indent=4))