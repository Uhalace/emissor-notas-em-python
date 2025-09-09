# Emissor de Notas em Python

Aplicativo desktop desenvolvido em Python com interface gráfica para emissão de notas fiscais de venda ao consumidor. Ideal para uso educacional ou controle interno de vendas. Permite cadastro de produtos, cálculo de desconto, emissão e exportação de nota em PDF, além de impressão e gerenciamento de notas emitidas.

---

##  Funcionalidades principais

- **Cadastro de cliente e produtos**
- **Edição e remoção** de itens da nota
- **Cálculo automático** do total com aplicação de desconto (em percentual)
- **Geração de nota fiscal** na interface gráfica (popup)
- **Exportação da nota** em:  
  - Arquivo `.pdf` (formatado com FPDF)  
  - Arquivo `.txt` (mais simples)
- **Impressão direta** da nota (funciona automaticamente no Windows)
- **Armazenamento** automático de todas as notas em pasta `notas_emitidas/`
- **Listagem interativa** para abrir notas emitidas (arquivo de texto ou PDF)

---

##  Tecnologias utilizadas

- **Python 3.8+**
- **Tkinter** – biblioteca padrão para interface gráfica  
- **FPDF** – para geração de arquivos PDF (`pip install fpdf`)

---

##  Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/uhalace/emissor-notas-em-python.git
   cd emissor-notas-em-python
