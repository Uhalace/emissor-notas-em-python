import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import os

# Função para converter string para float, tratando vírgulas
def parse_float(valor):
    valor = valor.replace(',', '.')
    try:
        return float(valor)
    except Exception:
        return None

# Função para listar notas fiscais já emitidas
def listar_notas_emitidas():
    notas_dir = "notas_emitidas"
    if not os.path.exists(notas_dir):
        os.makedirs(notas_dir)
    arquivos = [f for f in os.listdir(notas_dir) if f.endswith(".txt") or f.endswith(".pdf")]
    if not arquivos:
        messagebox.showinfo("Notas Emitidas", "Nenhuma nota fiscal emitida encontrada.")
        return

    # Permitir ao usuário escolher uma nota para abrir
    nota_escolhida = simpledialog.askstring(
        "Notas Emitidas",
        f"Notas encontradas em '{notas_dir}':\n\n" + "\n".join(f"{i+1}. {arq}" for i, arq in enumerate(arquivos)) + "\n\nDigite o número da nota para abrir:",
        parent=root
    )
    if nota_escolhida is None:
        return
    try:
        idx = int(nota_escolhida) - 1
        if idx < 0 or idx >= len(arquivos):
            raise ValueError
    except Exception:
        messagebox.showwarning("Atenção", "Número inválido.")
        return

    file_path = os.path.join(notas_dir, arquivos[idx])
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            conteudo = f.read()
        messagebox.showinfo("Nota Fiscal", conteudo)
    elif file_path.endswith(".pdf"):
        try:
            if os.name == "nt":
                os.startfile(file_path)
            else:
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo PDF:\n{e}")
    else:
        messagebox.showwarning("Atenção", "Tipo de arquivo não suportado.")
# Atualiza o total exibido
def atualizar_total():
    desconto = parse_float(entry_desconto.get() or "0")
    if desconto is None or desconto < 0 or desconto > 100:
        desconto = 0
    total = sum(p["quantidade"] * p["valor_unitario"] for p in produtos)
    total_com_desconto = total * (1 - desconto / 100)
    label_total.config(text=f"Total: R$ {total_com_desconto:,.2f}".replace('.', ','))
    return total, desconto, total_com_desconto
# Atualizar total ao mudar o desconto
def on_desconto_change(*args):
    atualizar_total()
# Ocultar console no Windows
def hide_console():
    if os.name == "nt":
        import ctypes
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)

# Função para adicionar produto
def adicionar_produto():
    nome = entry_produto.get().strip()
    quantidade = parse_float(entry_quantidade.get())
    valor_unitario = parse_float(entry_valor_unitario.get())
    if not nome or quantidade is None or quantidade <= 0 or valor_unitario is None or valor_unitario < 0:
        messagebox.showwarning("Atenção", "Preencha todos os campos corretamente!")
        return
    produtos.append({
        "nome": nome,
        "quantidade": quantidade,
        "valor_unitario": valor_unitario
    })
    tree_produtos.insert(
        '', tk.END,
        values=(
            nome,
            f"{quantidade:,.2f}".replace('.', ','),
            f"R$ {valor_unitario:,.2f}".replace('.', ','),
            f"R$ {(quantidade*valor_unitario):,.2f}".replace('.', ',')
        )
    )
    entry_produto.delete(0, tk.END)
    entry_quantidade.delete(0, tk.END)
    entry_valor_unitario.delete(0, tk.END)
    atualizar_total()
# Remover produto selecionado
def remover_produto():
    selected = tree_produtos.selection()
    if not selected:
        return
    idx = tree_produtos.index(selected[0])
    del produtos[idx]
    tree_produtos.delete(selected[0])
    atualizar_total()
# Editar produto selecionado
def editar_produto():
    selected = tree_produtos.selection()
    if not selected:
        messagebox.showwarning("Atenção", "Selecione um produto para editar!")
        return
    idx = tree_produtos.index(selected[0])
    produto = produtos[idx]
    novo_nome = simpledialog.askstring("Editar Produto", "Nome do produto:", initialvalue=produto["nome"], parent=root)
    if novo_nome is None or not novo_nome.strip():
        return
    nova_quantidade = simpledialog.askstring("Editar Produto", "Quantidade:", initialvalue=f"{produto['quantidade']:,.2f}".replace('.', ','), parent=root)
    if nova_quantidade is None:
        return
    nova_quantidade = parse_float(nova_quantidade)
    if nova_quantidade is None or nova_quantidade <= 0:
        messagebox.showwarning("Atenção", "Quantidade inválida!")
        return
    novo_valor_unitario = simpledialog.askstring("Editar Produto", "Valor Unitário:", initialvalue=f"{produto['valor_unitario']:,.2f}".replace('.', ','), parent=root)
    if novo_valor_unitario is None:
        return
    novo_valor_unitario = parse_float(novo_valor_unitario)
    if novo_valor_unitario is None or novo_valor_unitario < 0:
        messagebox.showwarning("Atenção", "Valor unitário inválido!")
        return
    produto["nome"] = novo_nome
    produto["quantidade"] = nova_quantidade
    produto["valor_unitario"] = novo_valor_unitario
    tree_produtos.item(selected[0], values=(
        novo_nome,
        f"{nova_quantidade:,.2f}".replace('.', ','),
        f"R$ {novo_valor_unitario:,.2f}".replace('.', ','),
        f"R$ {(nova_quantidade*novo_valor_unitario):,.2f}".replace('.', ',')
    ))
    atualizar_total()
# Gerar texto da nota fiscal
def gerar_texto_nota():
    import datetime
    cliente = entry_cliente.get().strip()
    total, desconto, total_com_desconto = atualizar_total()
    valor_desconto = total * (desconto / 100)
    data_emissao = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    cnpj = "00.000.000/0000-0000" # CNPJ DA EMPRESA QUE ESTÁ EMITINDO A NOTA
    ie = "000.000.000.000" # INSCRIÇÃO ESTADUAL DA EMPRESA
    endereco = "Rua da rua, numero do numero - Centro - Cidade/UF" # ENDEREÇO DA EMPRESA
    telefone = "(00) 00000-0000" # TELEFONE DA EMPRESA
    nota = []
    nota.append("="*60)
    nota.append(" " * 13 + "NOTA FISCAL DE VENDA E CONSUMO")
    nota.append("="*60)
    nota.append(f"Emitente: Galaxy S24") # NOMEDA EMPRESA QUE ESTÁ EMITINDO A NOTA
    nota.append(f"CNPJ: {cnpj}    IE: {ie}") #Dados da empresa da nota fiscal
    nota.append(f"Endereço: {endereco}") #Dados da empresa da nota fiscal
    nota.append(f"Tel: {telefone}") #Dados da empresa da nota fiscal
    nota.append("-"*60)
    nota.append(f"Cliente: {cliente}")
    nota.append(f"Data de Emissão: {data_emissao}")
    nota.append("-"*60)
    nota.append(f"{'Produto':25} {'Qtd':>6} {'V.Unit(R$)':>13} {'Subtotal(R$)':>14}")
    nota.append("-"*60)
    for p in produtos:
        nome = p['nome'][:25]
        qtd = f"{p['quantidade']:,.2f}".replace('.', ',')
        vunit = f"{p['valor_unitario']:,.2f}".replace('.', ',')
        subtotal = f"{(p['quantidade']*p['valor_unitario']):,.2f}".replace('.', ',')
        nota.append(f"{nome:25} {qtd:>6} {vunit:>13} {subtotal:>14}")
    nota.append("-"*60)
    nota.append(f"{'Desconto:':>44} {desconto:5.2f}% (R$ {valor_desconto:,.2f}".replace('.', ',') + ")")
    nota.append(f"{'Total a Pagar:':>44} R$ {total_com_desconto:,.2f}".replace('.', ','))
    nota.append("="*60)
    nota.append("Observação: Documento sem valor fiscal.")
    nota.append("Obrigado pela preferência!")
    nota.append("="*60)
    return "\n".join(nota)
# Emitir nota fiscal (exibir em popup)
def emitir_nota():
    if not entry_cliente.get().strip() or not produtos:
        messagebox.showwarning("Atenção", "Informe o cliente e adicione pelo menos um produto!")
        return
    nota = gerar_texto_nota()
    messagebox.showinfo("Nota Fiscal Emitida", nota)
# Salvar nota fiscal em PDF
def salvar_pdf():
    if not entry_cliente.get().strip() or not produtos:
        messagebox.showwarning("Atenção", "Informe o cliente e adicione pelo menos um produto!")
        return
    try:
        from fpdf import FPDF
    except ImportError:
        messagebox.showerror("Erro", "A biblioteca fpdf não está instalada.\nInstale com: pip install fpdf")
        return
    nota = gerar_texto_nota().split('\n')
    # Salvar automaticamente na pasta notas_emitidas
    notas_dir = "notas_emitidas"
    if not os.path.exists(notas_dir):
        os.makedirs(notas_dir)
    import datetime
    data_emissao = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"nota_fiscal_{data_emissao}.pdf"
    auto_file_path = os.path.join(notas_dir, file_name)
    # Também permitir salvar em local personalizado
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        file_path = auto_file_path  # Se o usuário cancelar, salva automaticamente
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Courier", size=12)
    # Centralizar título
    pdf.set_font("Courier", style='B', size=14)
    pdf.cell(0, 10, "NOTA FISCAL DE VENDA AO CONSUMIDOR", ln=1, align='C')
    pdf.set_font("Courier", size=12)
    for line in nota[2:]:
        if line.startswith("="):
            pdf.set_draw_color(180, 180, 180)
            pdf.cell(0, 1, "", ln=1, border="T")
        else:
            pdf.cell(0, 7, line, ln=1)
    try:
        pdf.output(file_path)
        # Sempre salva uma cópia na pasta notas_emitidas
        if file_path != auto_file_path:
            pdf.output(auto_file_path)
        messagebox.showinfo("Sucesso", f"Nota salva em PDF:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível salvar o PDF:\n{e}")
# Imprimir nota fiscal
def imprimir_nota():
    if not entry_cliente.get().strip() or not produtos:
        messagebox.showwarning("Atenção", "Informe o cliente e adicione pelo menos um produto!")
        return
    nota = gerar_texto_nota()
    temp_file = "nota_fiscal_temp.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(nota)
    try:
        if os.name == "nt":
            os.startfile(temp_file, "print")
        else:
            messagebox.showinfo("Impressão", "Impressão automática só disponível no Windows.\nAbra o arquivo manualmente para imprimir.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao imprimir:\n{e}")
# Ajustar colunas ao redimensionar janela
def on_resize(event):
    width = event.width
    tree_produtos.column("Produto", width=int(width*0.28))
    tree_produtos.column("Quantidade", width=int(width*0.18))
    tree_produtos.column("Valor Unitário", width=int(width*0.22))
    tree_produtos.column("Subtotal", width=int(width*0.22))

#Inicialização da interface
hide_console()
produtos = []
#INTERFACE GRÁFICA
root = tk.Tk()
root.title("Emissão de Nota Fiscal")
root.minsize(850, 480)
root.configure(bg="#f5f5f5")
#ESTILIZAÇAO DA INTERFACE
style = ttk.Style()
style.theme_use('clam')
style.configure("Treeview", background="#fff", foreground="#333", rowheight=28, fieldbackground="#fff", font=('Consolas', 11))
style.configure("Treeview.Heading", font=('Segoe UI', 12, 'bold'), background="#e0e0e0")
style.configure("TButton", font=('Segoe UI', 11), padding=6)
style.configure("TLabel", font=('Segoe UI', 11), background="#f5f5f5")
#LAYOUT DA INTERFACE
frame_top = tk.Frame(root, bg="#f5f5f5")
frame_top.pack(fill="x", padx=20, pady=10)
tk.Label(frame_top, text="Cliente:", bg="#f5f5f5", font=('Segoe UI', 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_cliente = tk.Entry(frame_top, width=35, font=('Segoe UI', 12))
entry_cliente.grid(row=0, column=1, padx=5, pady=5, sticky="w")
# Adicionar produtos
frame_produto = tk.LabelFrame(root, text="Adicionar Produto", bg="#f5f5f5", font=('Segoe UI', 12, 'bold'), padx=10, pady=10)
frame_produto.pack(fill="x", padx=20, pady=10)
tk.Label(frame_produto, text="Produto:", bg="#f5f5f5").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_produto = tk.Entry(frame_produto, width=20, font=('Segoe UI', 11))
entry_produto.grid(row=0, column=1, padx=5, pady=5, sticky="w")
tk.Label(frame_produto, text="Quantidade:", bg="#f5f5f5").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_quantidade = tk.Entry(frame_produto, width=10, font=('Segoe UI', 11))
entry_quantidade.grid(row=0, column=3, padx=5, pady=5, sticky="w")
tk.Label(frame_produto, text="Valor Unitário:", bg="#f5f5f5").grid(row=0, column=4, padx=5, pady=5, sticky="e")
entry_valor_unitario = tk.Entry(frame_produto, width=10, font=('Segoe UI', 11))
entry_valor_unitario.grid(row=0, column=5, padx=5, pady=5, sticky="w")
btn_adicionar = ttk.Button(frame_produto, text="Adicionar Produto", command=adicionar_produto)
btn_adicionar.grid(row=0, column=6, padx=10, pady=5)
# Lista de produtos
frame_lista = tk.Frame(root, bg="#f5f5f5")
frame_lista.pack(fill="both", expand=True, padx=20, pady=10)
tree_produtos = ttk.Treeview(frame_lista, columns=("Produto", "Quantidade", "Valor Unitário", "Subtotal"), show="headings", selectmode="browse")
tree_produtos.heading("Produto", text="Produto")
tree_produtos.heading("Quantidade", text="Quantidade")
tree_produtos.heading("Valor Unitário", text="Valor Unitário")
tree_produtos.heading("Subtotal", text="Subtotal")
tree_produtos.column("Produto", width=220)
tree_produtos.column("Quantidade", width=120, anchor="center")
tree_produtos.column("Valor Unitário", width=140, anchor="center")
tree_produtos.column("Subtotal", width=140, anchor="center")
tree_produtos.pack(side="left", fill="both", expand=True)
scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_produtos.yview)
tree_produtos.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")
# Ações sobre produtos
frame_acoes = tk.Frame(root, bg="#f5f5f5")
frame_acoes.pack(fill="x", padx=20, pady=5)
btn_remover = ttk.Button(frame_acoes, text="Remover Produto Selecionado", command=remover_produto)
btn_remover.pack(side="left", padx=5, ipadx=10)
btn_editar = ttk.Button(frame_acoes, text="Editar Produto Selecionado", command=editar_produto)
btn_editar.pack(side="left", padx=5, ipadx=10)
# Total e desconto
frame_bottom = tk.Frame(root, bg="#f5f5f5")
frame_bottom.pack(fill="x", padx=20, pady=10)
tk.Label(frame_bottom, text="Desconto (%):", bg="#f5f5f5").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_desconto = tk.Entry(frame_bottom, width=10, font=('Segoe UI', 11))
entry_desconto.grid(row=0, column=1, padx=5, pady=5, sticky="w")
label_total = tk.Label(frame_bottom, text="Total: R$ 0,00", font=('Segoe UI', 13, 'bold'), fg="#1976d2", bg="#f5f5f5")
label_total.grid(row=0, column=2, padx=30, pady=5, sticky="w")
entry_desconto_var = tk.StringVar()
entry_desconto.config(textvariable=entry_desconto_var)
entry_desconto_var.trace_add("write", on_desconto_change)
# Botões de ação
frame_botoes = tk.Frame(root, bg="#f5f5f5")
frame_botoes.pack(fill="x", padx=20, pady=15)
btn_emitir = ttk.Button(frame_botoes, text="Emitir Nota Fiscal", command=emitir_nota)
btn_emitir.pack(side="left", padx=10, ipadx=10)
btn_salvar_pdf = ttk.Button(frame_botoes, text="Salvar em PDF", command=salvar_pdf)
btn_salvar_pdf.pack(side="left", padx=10, ipadx=10)
btn_imprimir = ttk.Button(frame_botoes, text="Imprimir Nota Fiscal", command=imprimir_nota)
btn_imprimir.pack(side="left", padx=10, ipadx=10)
btn_listar_notas = ttk.Button(frame_botoes, text="Notas já Emitidas", command=listar_notas_emitidas)
btn_listar_notas.pack(side="left", padx=10, ipadx=10)
# Ajustar colunas ao redimensionar
root.bind("<Configure>", on_resize)
root.mainloop() # Inicia a interface # Inicia a interface
