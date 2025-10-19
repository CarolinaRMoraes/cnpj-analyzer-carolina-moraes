
from crew import run_analise_completa, Agent, Crew, Process, Task, LLM
import tkinter as tk
from tkinter import ttk, messagebox

# frontend_app.py

import tkinter as tk
from tkinter import messagebox, ttk
from crew import run_analise_completa # Importa a função de execução do CrewAI/Mock

class AnaliseCNPJApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Análise de CNPJ - Carolina Moraes")
        self.geometry("700x750")
        self.configure(bg='#f0f0f0')

        # Variáveis de Controle
        self.cnpj_var = tk.StringVar(value="00.000.000/0000-00") 
        self.veredicto_var = tk.StringVar(value="Resultado Final: Aguardando análise...")
        self.nome_empresa_var = tk.StringVar(value="Empresa: N/A")

        # Configuração da Interface 
        input_frame = ttk.Frame(self, padding="10 10 10 10")
        input_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(input_frame, text="CNPJ para análise:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Entry(input_frame, textvariable=self.cnpj_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Botoes (execucao e limpeza)
        ttk.Button(input_frame, text="Executar Análise", command=self.executar_analise, style='TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(input_frame, text="Limpar", command=self._limpar_tudo).pack(side=tk.LEFT, padx=10)

        # Configuração da Interface
        ttk.Label(self, text="Resultados da análise de risco", font=('Arial', 12, 'italic')).pack(pady=(10, 5))

        self.veredicto_label = ttk.Label(self, 
                                        textvariable=self.veredicto_var, 
                                        font=('Arial', 18, 'bold'),
                                        foreground='gray')
        self.veredicto_label.pack(pady=5)
        
        self.nome_empresa_label = ttk.Label(self, textvariable=self.nome_empresa_var, font=('Arial', 11))
        self.nome_empresa_label.pack(pady=5)

        # Widgets para justificativa 
        ttk.Label(self, text="Justificativa:", font=('Arial', 11, 'bold')).pack(pady=(10, 0))
        self.justificativa_text = tk.Text(self, height=5, width=80, wrap=tk.WORD, font=('Arial', 10), state=tk.DISABLED, relief=tk.FLAT, bg='#e5e5e5')
        self.justificativa_text.pack(padx=20)

        # Widgets para fatores detalhados
        ttk.Label(self, text="Fatores Detalhados:", font=('Arial', 11, 'bold')).pack(pady=(10, 0))
        self.fatores_text = tk.Text(self, height=15, width=80, wrap=tk.WORD, font=('Courier New', 10), state=tk.DISABLED, relief=tk.FLAT, bg='#ffffff')
        self.fatores_text.pack(padx=20)

    def executar_analise(self):
        cnpj = self.cnpj_var.get().strip()
        
        if not cnpj:
            messagebox.showwarning("Atenção", "Por favor, insira um CNPJ válido.")
            return

        # Limpa os resultados anteriores
        self._limpar_resultados()
        
        try:
            # Chama a função de backend
            resultado_dict = run_analise_completa(cnpj) 
            
            # Tratamento de erros
            if isinstance(resultado_dict, str):
                if resultado_dict == "CNPJ_INVALIDO":
                    msg = "CNPJ não encontrado ou inválido. Por favor, verifique o número inserido."
                elif resultado_dict == "FALHA_API":
                    msg = "Erro no servidor de dados: A API retornou um erro interno ao tentar buscar o CNPJ."
                else:
                    msg = f"Ocorreu um erro desconhecido durante a análise: {resultado_dict}"

                messagebox.showerror("Erro na Análise", msg)
                return
            
        except Exception as e:
            # Erros não tratados 
            messagebox.showerror("Erro de Execução", f"Falha inesperada no sistema: {e}")
            self._limpar_resultados() 
            return
        
        self.atualizar_interface_com_dados(resultado_dict)

    def _limpar_resultados(self):
        self.veredicto_var.set("Resultado Final: Aguardando análise...")
        self.veredicto_label.config(foreground='gray')
        self.nome_empresa_var.set("Empresa: N/A")
        
        for widget in [self.justificativa_text, self.fatores_text]:
            widget.config(state=tk.NORMAL)
            widget.delete('1.0', tk.END)
            widget.config(state=tk.DISABLED)

    def _limpar_tudo(self):
        self.cnpj_var.set("")
        self._limpar_resultados()

    def atualizar_interface_com_dados(self, resultado: dict):
        resultado_final_str = resultado.get('verdict', 'N/A')
        nome_empresa = resultado.get('nome', 'N/A')
        justificativa = resultado.get('justification', 'Não especificada.')
        

        fatores_positivos = resultado.get('positive_factors', [])
        pontos_atencao = resultado.get('attention_points', [])
        fatores_negativos = resultado.get('negative_factors', [])


        self.veredicto_var.set(f"RESULTADO: {resultado_final_str}")
        self.nome_empresa_var.set(f"Empresa: {nome_empresa}")
        
        # Estilo do texto resultado
        if resultado_final_str == 'APROVADO':
            cor = "green"
        elif resultado_final_str == 'REJEITADO':
            cor = "red"
        else:
            cor = "orange"
        self.veredicto_label.config(foreground=cor)

        # Atualizar justificativa ---
        self.justificativa_text.config(state=tk.NORMAL)
        self.justificativa_text.delete('1.0', tk.END)
        self.justificativa_text.insert(tk.END, justificativa)
        self.justificativa_text.config(state=tk.DISABLED)

        # Atualizar lista de fatores 
        output_fatores = "---------------------------------------\n"
        output_fatores += "Fatores Positivos:\n"
        output_fatores += "\n".join([f"  ✅ {f}" for f in fatores_positivos if f != 'nenhum ponto positivo identificado'])
        if not [f for f in fatores_positivos if f != 'nenhum ponto positivo identificado']:
             output_fatores += "  Nenhum fator positivo encontrado.\n"
        
        output_fatores += "\n\n---------------------------------------\n"
        output_fatores += "Pontos de Atenção:\n"
        output_fatores += "\n".join([f"  ⚠️ {p}" for p in pontos_atencao if p != 'nenhum ponto de atenção identificado'])
        if not [p for p in pontos_atencao if p != 'nenhum ponto de atenção identificado']:
             output_fatores += "  Nenhum ponto de atenção encontrado.\n"
             
        output_fatores += "\n\n---------------------------------------\n"
        output_fatores += "Fatores Negativos:\n"
        output_fatores += "\n".join([f"  ❌ {n}" for n in fatores_negativos if n != 'nenhum ponto negativo identificado'])
        if not [n for n in fatores_negativos if n != 'nenhum ponto negativo identificado']:
             output_fatores += "  Nenhum fator negativo encontrado.\n"
        
        output_fatores += "\n---------------------------------------\n"

        self.fatores_text.config(state=tk.NORMAL)
        self.fatores_text.delete('1.0', tk.END)
        self.fatores_text.insert(tk.END, output_fatores)
        self.fatores_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = AnaliseCNPJApp()
    app.mainloop()