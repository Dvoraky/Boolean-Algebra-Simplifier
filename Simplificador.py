import tkinter as tk
from tkinter import font
from pyeda.inter import expr, exprvar
import re

def translate_to_pyeda(user_expr: str) -> str:
    """
    Traduz uma expressão booleana do usuário para um formato compatível com a pyeda.
    """
    if not user_expr:
        return ""
    
    s = user_expr.strip()

    #Converter constantes negadas diretamente para 0 e 1.
    for _ in range(5): 
        s = s.replace(r'\overline{1}', '0'); s = s.replace(r'\overline{0}', '1')
        s = re.sub(r'\\overline\{\s*1\s*\}', '0', s); s = re.sub(r'\\overline\{\s*0\s*\}', '1', s)
        s = s.replace('!1', '0'); s = s.replace('!0', '1')
        s = s.replace('~1', '0'); s = s.replace('~0', '1')
        s = s.replace('!(1)', '0'); s = s.replace('!(0)', '1')
        s = s.replace('~(1)', '0'); s = s.replace('~(0)', '1')

    #Lidar com negações em variáveis e expressões.
    s = re.sub(r'\\overline\s*([a-zA-Z0-9]+)', r'~(\1)', s)
    while r'\overline{' in s:
        s = re.sub(r'\\overline\{([^}]+)\}', r'~ (\1)', s)
    s = s.replace('!', '~')

    #Padronizar operadores e inserir ANDs implícitos.
    s = f" {s} "
    s = re.sub(r'\s+AND\s+', ' & ', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+OR\s+', ' | ', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+XOR\s+', ' ^ ', s, flags=re.IGNORECASE)
    s = s.replace('.', ' & ')
    s = s.replace('+', ' | ')
    s = re.sub(r'([a-zA-Z0-9\)])\s*([a-zA-Z0-9\(~])', r'\1 & \2', s)
    
    return s.strip()

def formatar_por_texto(expr_obj) -> str:
    """
    Formata o objeto de expressão simplificado.
    """
    s = str(expr_obj)
    if s in ['0', '1']: return s

    def processar_and(match):
        args_str = match.group(1)
        literais = sorted([arg.strip() for arg in args_str.split(',')])
        return "".join(literais)

    while 'And(' in s:
        s = re.sub(r'And\(([^()]+)\)', processar_and, s)

    if s.startswith('Or('):
        conteudo = s[3:-1]
        termos = [termo.strip() for termo in conteudo.split(',')]
        s = " + ".join(termos)
        
    return s

def polir_resultado(dnf_string: str) -> str:
    """
    Serve para refinar o resultado final da expressão simplificada
    """
    if not dnf_string or dnf_string in ["0", "1"]:
        return dnf_string
    
    termos = set(dnf_string.split(' + '))

    while True:
        simplificou_passagem_atual = False
        
        # --- Regra 1: Absorção (X + XY = X) ---
        termos_para_remover = set()
        lista_ordenada = sorted(list(termos), key=len)
        
        for i in range(len(lista_ordenada)):
            for j in range(i + 1, len(lista_ordenada)):
                t1 = lista_ordenada[i]
                t2 = lista_ordenada[j]
                
                literais_t1 = set(re.findall(r'~?\w', t1))
                literais_t2 = set(re.findall(r'~?\w', t2))
                
                if literais_t1.issubset(literais_t2):
                    if t2 not in termos_para_remover:
                        termos_para_remover.add(t2)
                        simplificou_passagem_atual = True

        if simplificou_passagem_atual:
            termos -= termos_para_remover
            continue

        # --- Regra 2: Adjacência (XY + X~Y = X) ---
        termos_processados = set()
        for t1 in lista_ordenada:
            for t2 in lista_ordenada:
                if t1 == t2 or frozenset([t1, t2]) in termos_processados:
                    continue
                
                literais_t1 = set(re.findall(r'~?\w', t1))
                literais_t2 = set(re.findall(r'~?\w', t2))
                diff = literais_t1.symmetric_difference(literais_t2)
                
                if len(diff) == 2:
                    l1, l2 = list(diff)
                    l_negado = f"~{l1}" if not l1.startswith('~') else l1[1:]
                    if l_negado == l2:
                        termo_comum = "".join(sorted(list(literais_t1.intersection(literais_t2))))
                        if not termo_comum: continue
                        termos_para_remover.update([t1, t2])
                        termos.add(termo_comum) # Adiciona diretamente para a próxima iteração
                        simplificou_passagem_atual = True
                
                termos_processados.add(frozenset([t1, t2]))
        
        if simplificou_passagem_atual:
            termos -= termos_para_remover
            continue

        # --- Regra 3: Adjacência (X + X'Y = X + Y e X' + XY = X' + Y) ---
        termos_para_adicionar = set()
        for t_x_cand in lista_ordenada:
            if len(re.findall(r'~?\w', t_x_cand)) == 1: # t_x_cand é um literal X ou X'
                t_x_comp = f"~{t_x_cand}" if not t_x_cand.startswith('~') else t_x_cand[1:]
                
                for t_xy_cand in lista_ordenada:
                    if t_x_comp in t_xy_cand: # Encontrou um par (X, X'Y) ou (X', XY)
                        t_y = "".join(sorted(re.findall(r'~?\w', t_xy_cand.replace(t_x_comp, ""))))
                        if t_y == "": continue
                        
                        termos_para_remover.add(t_xy_cand)
                        termos_para_adicionar.add(t_y)
                        simplificou_passagem_atual = True

        if simplificou_passagem_atual:
            termos = (termos - termos_para_remover) | termos_para_adicionar
            continue
        
        break

    if not termos: return "0"
    return " + ".join(sorted(list(termos)))


def simplify_logic():
    original_expression = entry_expression.get()
    label_simplified_val.config(text="")
    label_error.config(text="")

    if not original_expression:
        label_error.config(text="Erro: O campo de expressão está vazio.")
        return

    try:
        translated_expression = translate_to_pyeda(original_expression)
        
        if not translated_expression:
            label_simplified_val.config(text="0")
            return

        var_names = sorted(list(set(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', translated_expression))))
        pyeda_keywords = {'Or', 'And', 'Not', 'Xor', 'Equal', 'Implies'}
        var_names = [v for v in var_names if v not in pyeda_keywords]
        
        if not var_names:
            result = eval(translated_expression.replace('&', ' and ').replace('|', ' or '))
            label_simplified_val.config(text=str(int(result)))
            return

        for var in var_names:
            globals()[var] = exprvar(var)

        pyeda_expr = eval(translated_expression)
        
        simplified_expr = pyeda_expr.to_dnf()

        formatted_result = formatar_por_texto(simplified_expr)

        polished_result = polir_resultado(formatted_result)

        label_simplified_val.config(text=polished_result)

    except Exception as e:
        error_message = f"Erro ao processar a expressão: {e}"
        label_error.config(text=error_message)


window = tk.Tk()
window.title("Simplificador de Expressões Booleanas")
window.geometry("600x250")
window.configure(padx=15, pady=15)

default_font = font.Font(family="Helvetica", size=10)
bold_font = font.Font(family="Helvetica", size=11, weight="bold")
result_font = font.Font(family="Courier New", size=14)

input_frame = tk.Frame(window)
input_frame.pack(fill='x', pady=(0, 10))

label_expression = tk.Label(input_frame, text="Digite a Expressão:", font=default_font)
label_expression.pack(side='left', padx=(0, 10))

entry_expression = tk.Entry(input_frame, font=result_font, width=50)
entry_expression.pack(side='left', fill='x', expand=True)

btn_simplify = tk.Button(window, text="Simplificar", command=simplify_logic, font=bold_font, bg="#d0e0ff")
btn_simplify.pack(pady=10, fill='x')

results_frame = tk.LabelFrame(window, text="Resultado Simplificado", padx=10, pady=10)
results_frame.pack(fill='both', expand=True)

label_simplified_val = tk.Label(results_frame, text="", font=result_font, wraplength=500, justify='center', fg="green")
label_simplified_val.pack(pady=10, expand=True)

label_error = tk.Label(window, text="", font=default_font, fg="red")
label_error.pack(pady=(10, 0))

window.mainloop()