from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from data import get_empresa_data_from_cnpj
from dotenv import load_dotenv 
from pydantic import BaseModel, Field
from typing import List


# Adicionar key (OPEN AI) ao ambiente
load_dotenv()

llm_model = LLM(
    model="gpt-4o-mini",
    temperature=0.7 
)

# Estrutura de JSON para ser usado no resultado final
class DecisionOutput(BaseModel):
    """Modelo de dados para o veredicto final de risco."""
    
    verdict: str = Field(
        description="O veredicto final de risco: 'APPROVED', 'UNDER ATTENTION', ou 'REJECTED'."
    )
    positive_factors: List[str] = Field(
        description="Lista de fatores positivos identificados. Use 'nenhum ponto positivo identificado' se a lista estiver vazia."
    )
    attention_points: List[str] = Field(
        description="Lista de pontos de atenção identificados. Use 'nenhum ponto de atenção identificado' se a lista estiver vazia."
    )
    negative_factors: List[str] = Field(
        description="Lista de fatores negativos identificados. Use 'nenhum ponto negativo identificado' se a lista estiver vazia."
    )
    justification: str = Field(
        description="Explicação clara e concisa em Português resumindo o raciocínio por trás da decisão."
    )
    nome: str = Field(
        description="O nome da empresa, obtido a partir da variável 'nome'."
    )

# Criando os agentes
market_analyst = Agent(
  role='Business Analyst',
  goal='Accurately determine if the companys context (CNAE, trade name, activity description) qualifies it as an educational segment company, issuing a clear and grounded opinion',
  verbose=True,
  backstory='I am an experienced Business Analyst. My expertise lies in deciphering a companys true purpose through its formal records and operational context. I meticulously analyze the National Classification of Economic Activities (CNAE) and the companys name/description to ensure the Educational classification is strictly and correctly applied.',
  llm=llm_model
)

financial_auditor = Agent(
  role='Financial Auditor',
  goal='Evaluate the coherence and suitability of the companys declared Share Capital (Capital Social) in relation to its size (revenue, size) and Legal Nature, identifying potential risk misalignments',
  verbose=True,
  backstory='I work as a Financial Auditor focusing on Balance Sheet and Risk Analysis. My job is to verify that the companys financial foundation, the Share Capital, is proportional and consistent with the operational level and fiscal responsibility of its declared size (ME, EPP, LTDA, S/A, etc.). I am rigorous in searching for inconsistencies that might indicate undercapitalization or future risk',
  llm=llm_model
)

decision_agent = Agent(
  role='Senior Risk Analyst and Decision Maker',
  goal='Integrate the Sector and Financial Suitability opinions to issue a final recommendation: APPROVED, UNDER ATTENTION, or REJECTED',
  verbose=True,
  backstory='I am responsible for the final decision-making. My process is methodical and transparent, built upon a predefined risk matrix. I prioritize security, classifying as REJECTED any company that presents critical Negative Factors (such as inactive status or incompatible activity). The UNDER ATTENTION classification is reserved for companies with potential but requiring caution (such as newly created companies with low capital). APPROVED status is granted only to those demonstrating clear Positive Factors and an absence of Negative Factors.',
  llm=llm_model
)

# Criando as tasks 
task_sectorial = Task(
    description="""
    Analyze the company's data using the following information:
    - Main activity: {atividade_principal}
    - CNAE: {cnae}
    - Name: {nome}

    Determine strictly whether the company's main activity, CNAE code, or trade name indicate that it operates in the EDUCATION sector (schools, courses, training centers, universities, e-learning, tutoring, etc.)
    
    The output must be a concise verdict, classifying the company as 'Educational activity confirmed' (POSITIVE FACTOR) or 'Educational activity incompatible' (NEGATIVE FACTOR).
    """,
    agent=market_analyst,
    expected_output="A single sentence: 'Educational activity confirmed' or 'Educational activity incompatible'.",
)

task_financial = Task(
    description="""
    Evaluate the company's financial and structural indicators using the following data:
    - Age: {tempo_de_empresa_anos} years
    - Share Capital: {capital_social}, 
    - Company Size: {size} (e.g., MEI, Micro, Small, Medium, Large).

    The analysis should:
    - Evaluate whether the declared share capital appears consistent with the company's size and maturity.
    - Comment on the financial solidity and potential stability based on these factors.
    - Identify if there are any risk signals (e.g., very low capital for an older company or large company with undercapitalization).
    - Mention positive financial aspects when applicable (e.g., long market presence, high capitalization, or coherent growth profile).
    - Share Capital: If > R$ 100,000.00, classify as 'Share Capital > R$ 100k' (POSITIVE FACTOR). If R$ 100,000.00 or less, classify as 'Low capital for size' (ATTENTION POINT).
    
    The output must be a clear bulleted list for the Decision Agent.
    """,
    agent=financial_auditor,
    expected_output="A short paragraph providing a reasoned financial interpretation, mentioning both strengths and potential concerns if any."
)

task_decision = Task(
    description=f"""
    Final Risk Rating Instruction:

    Data:
    - Company Name: {{nome}} 
    - Status: {{status}}
    - Age: {{tempo_de_empresa_anos}} years

    1. Analyze the reports from the Sector Agent and the Financial Agent, the company's Operational Status: {{status}}, and the age of the company: {{tempo_de_empresa_anos}}
    2. Apply the decision rules below in the strict following order:
       - REJECTED (NEGATIVE): If there is **any** Negative Factor.
       - UNDER ATTENTION (CAUTION):** If not Rejected, but **any** Attention Point is present.
       - APPROVED (POSITIVE): If neither Rejected nor Under Attention, and there is at least one Positive Factor.

    Reference Criteria (Mandatory):
    - Positive Factors: Company > 2 years, Share Capital > R$ 100k, Activity related to education.
    - Attention Points: Newly created company (< 2), Low capital for size.
    - Negative Factors: Status Inactive/Suspended/Struck Off (from Operational Status: {{status}}), Activities incompatible with education (from Sector Agent report).

    3. Deliver the final verdict ('APROVADO', 'SOB ATENÇÃO', or 'REJEITADO') followed by a bulleted list that justifies the decision, listing all Positive Factors, Attention Points, and Negative Factors found in Portuguese.
    """,
    agent=decision_agent,
    output_json=DecisionOutput,
    expected_output="Generate the result in the exact JSON format required by the DecisionOutput Pydantic model. Ensure all factor lists are in Portuguese and the justification is clear.",
    context=[task_sectorial, task_financial]
)

# Executar a analise por meio do CrewAI
def run_analise_completa(cnpj_input):

    # Coleta dos dados
    empresa_data, tipo_erro = get_empresa_data_from_cnpj(cnpj_input)

    # Tratamento de erro
    if tipo_erro:
        return tipo_erro

    if not empresa_data:
        return None

    # Configuração do Crew
    analise_crew = Crew(
        agents=[market_analyst, financial_auditor, decision_agent],
        tasks=[task_sectorial, task_financial, task_decision],
        verbose=True 
    )

    # Execução do Crew
    analise_crew.kickoff(inputs=empresa_data)
    resultado_final = analise_crew.tasks[-1]
    
    if resultado_final.output and resultado_final.output.json_dict:
        # Dicionário JSON que o frontend espera
        return resultado_final.output.json_dict
    else:
        # Caso o LLM falhe ao gerar o JSON 
        print("Erro: A tarefa de decisão falhou em gerar o JSON")
        return None


# Bloco de execução para testes
if __name__ == '__main__':
    #  Obter o CNPJ
    cnpj = input("Digite o CNPJ da empresa para análise: ").strip()
    
    # Rodar o processo completo
    resultado = run_analise_completa(cnpj)
    
    print("\n===========================================")
    print("        RESULTADO FINAL:")
    print("===========================================")
    print(resultado)