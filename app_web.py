from flask import Flask, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ================= BANCO DE DADOS =================
def inicializar_banco():
    conn = sqlite3.connect("entregas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def adicionar_entrega(desc, valor):
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = sqlite3.connect("entregas.db")
    conn.cursor().execute("INSERT INTO entregas VALUES (NULL, ?, ?, ?)", (data, desc, valor))
    conn.commit()
    conn.close()

def adicionar_gasto(desc, valor):
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = sqlite3.connect("entregas.db")
    conn.cursor().execute("INSERT INTO gastos VALUES (NULL, ?, ?, ?)", (data, desc, valor))
    conn.commit()
    conn.close()

def listar_entregas(data_inicio=None, data_fim=None):
    conn = sqlite3.connect("entregas.db")
    cursor = conn.cursor()
    if data_inicio and data_fim:
        cursor.execute("""
            SELECT * FROM entregas 
            WHERE SUBSTR(data, 1, 10) BETWEEN ? AND ?
            ORDER BY id DESC
        """, (data_inicio, data_fim))
    else:
        cursor.execute("SELECT * FROM entregas ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados

def listar_gastos(data_inicio=None, data_fim=None):
    conn = sqlite3.connect("entregas.db")
    cursor = conn.cursor()
    if data_inicio and data_fim:
        cursor.execute("""
            SELECT * FROM gastos 
            WHERE SUBSTR(data, 1, 10) BETWEEN ? AND ?
            ORDER BY id DESC
        """, (data_inicio, data_fim))
    else:
        cursor.execute("SELECT * FROM gastos ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados

def obter_totais(data_inicio=None, data_fim=None):
    e = listar_entregas(data_inicio, data_fim)
    g = listar_gastos(data_inicio, data_fim)
    total_e = sum(x[3] for x in e) if e else 0
    total_g = sum(x[3] for x in g) if g else 0
    return total_e, total_g

# ================= TEMPLATE BASE =================
def gerar_html(conteudo):
    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controle de Entregas</title>
    <style>
        * {{ box-sizing: border-box; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
        body {{ background: #f5f5f5; padding: 20px; max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        .menu {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 30px; justify-content: center; }}
        .menu a {{ padding: 12px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; transition: 0.3s; }}
        .btn-verde {{ background: #27ae60; color: white; }}
        .btn-verde:hover {{ background: #219653; }}
        .btn-vermelho {{ background: #e74c3c; color: white; }}
        .btn-vermelho:hover {{ background: #c0392b; }}
        .btn-azul {{ background: #3498db; color: white; }}
        .btn-azul:hover {{ background: #2980b9; }}
        .btn-cinza {{ background: #95a5a6; color: white; }}
        .btn-cinza:hover {{ background: #7f8c8d; }}
        .card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        h2 {{ color: #2c3e50; margin-bottom: 20px; text-align: center; }}
        input {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; }}
        button {{ padding: 12px 25px; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; width: 100%; }}
        .msg {{ padding: 10px; border-radius: 6px; margin: 10px 0; text-align: center; font-weight: bold; }}
        .sucesso {{ background: #d4edda; color: #155724; }}
        .erro {{ background: #f8d7da; color: #721c24; }}
        .lista {{ margin-top: 15px; }}
        .item {{ padding: 12px; border-bottom: 1px solid #eee; }}
        .item:last-child {{ border-bottom: none; }}
        .total {{ margin-top: 15px; font-size: 18px; font-weight: bold; text-align: right; padding: 10px; background: #f0f0f0; border-radius: 6px; }}
        .voltar {{ display: inline-block; margin-top: 20px; color: #3498db; text-decoration: none; }}
        .voltar:hover {{ text-decoration: underline; }}
        .linha {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .linha input {{ flex: 1; min-width: 150px; }}
        .btn-filtrar {{ background: #3498db; color: white; border: none; padding: 12px; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }}
        .btn-tudo {{ background: #95a5a6; color: white; text-decoration: none; display: inline-block; text-align: center; padding: 12px; border-radius: 6px; font-weight: bold; }}
        .saldo-positivo {{ color: #27ae60; font-size: 22px; font-weight: bold; }}
        .saldo-negativo {{ color: #e74c3c; font-size: 22px; font-weight: bold; }}
        .saldo-zero {{ color: #f39c12; font-size: 22px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>🚚 Controle de Entregas</h1>
    {conteudo}
</body>
</html>"""

# ================= ROTAS =================
@app.route('/')
def inicio():
    conteudo = """
    <div class="menu">
        <a href="/cadastrar/entrega" class="btn-verde">✅ Cadastrar Entrega</a>
        <a href="/cadastrar/gasto" class="btn-vermelho">💸 Cadastrar Gasto</a>
        <a href="/historico/entregas" class="btn-azul">📋 Histórico Entregas</a>
        <a href="/historico/gastos" class="btn-azul">📋 Histórico Gastos</a>
        <a href="/resumo" class="btn-cinza">📊 Resumo Geral</a>
    </div>
    """
    return gerar_html(conteudo)

@app.route('/cadastrar/entrega', methods=['GET', 'POST'])
def cad_entrega():
    msg = ''
    if request.method == 'POST':
        desc = request.form.get('descricao', '').strip() or 'Entrega'
        valor = request.form.get('valor', '').strip()
        if valor:
            adicionar_entrega(desc, float(valor))
            msg = '<div class="msg sucesso">✅ Salvo com sucesso!</div>'
        else:
            msg = '<div class="msg erro">⚠️ Digite o valor!</div>'
    
    conteudo = f"""
    <div class="card">
        <h2>Cadastrar Entrega</h2>
        {msg}
        <form method="post">
            <input type="text" name="descricao" placeholder="Descrição (ex: Rua A, Bairro)">
            <input type="number" step="0.01" name="valor" placeholder="Valor R$" required>
            <button type="submit" class="btn-verde">💾 Salvar</button>
        </form>
        <a href="/" class="voltar">⬅️ Voltar ao Menu</a>
    </div>
    """
    return gerar_html(conteudo)

@app.route('/cadastrar/gasto', methods=['GET', 'POST'])
def cad_gasto():
    msg = ''
    if request.method == 'POST':
        desc = request.form.get('descricao', '').strip() or 'Gasto'
        valor = request.form.get('valor', '').strip()
        if valor:
            adicionar_gasto(desc, float(valor))
            msg = '<div class="msg sucesso">✅ Salvo com sucesso!</div>'
        else:
            msg = '<div class="msg erro">⚠️ Digite o valor!</div>'
    
    conteudo = f"""
    <div class="card">
        <h2>Cadastrar Gasto</h2>
        {msg}
        <form method="post">
            <input type="text" name="descricao" placeholder="Descrição (ex: Combustível, Almoço)">
            <input type="number" step="0.01" name="valor" placeholder="Valor R$" required>
            <button type="submit" class="btn-vermelho">💾 Salvar</button>
        </form>
        <a href="/" class="voltar">⬅️ Voltar ao Menu</a>
    </div>
    """
    return gerar_html(conteudo)

@app.route('/historico/entregas')
def his_entregas():
    dados = listar_entregas()
    total = sum(x[3] for x in dados) if dados else 0
    
    itens = ''
    if dados:
        for d in dados:
            itens += f'<div class="item"><strong>{d[1]}</strong><br>{d[2]} — R$ {d[3]:.2f}</div>'
        itens += f'<div class="total">💰 Total: R$ {total:.2f}</div>'
    else:
        itens = '<p style="text-align:center; color:#7f8c8d;">Nenhuma entrega cadastrada</p>'
    
    conteudo = f"""
    <div class="card">
        <h2>Histórico de Entregas</h2>
        <div class="lista">{itens}</div>
        <a href="/" class="voltar">⬅️ Voltar ao Menu</a>
    </div>
    """
    return gerar_html(conteudo)

@app.route('/historico/gastos')
def his_gastos():
    dados = listar_gastos()
    total = sum(x[3] for x in dados) if dados else 0
    
    itens = ''
    if dados:
        for d in dados:
            itens += f'<div class="item"><strong>{d[1]}</strong><br>{d[2]} — R$ {d[3]:.2f}</div>'
        itens += f'<div class="total">💸 Total: R$ {total:.2f}</div>'
    else:
        itens = '<p style="text-align:center; color:#7f8c8d;">Nenhum gasto cadastrado</p>'
    
    conteudo = f"""
    <div class="card">
        <h2>Histórico de Gastos</h2>
        <div class="lista">{itens}</div>
        <a href="/" class="voltar">⬅️ Voltar ao Menu</a>
    </div>
    """
    return gerar_html(conteudo)

@app.route('/resumo', methods=['GET', 'POST'])
def resumo():
    di = df = periodo = ''
    te = tg = saldo = 0
    
    if request.method == 'POST':
        di = request.form.get('data_inicio', '').strip()
        df = request.form.get('data_fim', '').strip()
        if di and df:
            te, tg = obter_totais(di, df)
            periodo = f'{di} até {df}'
        else:
            te, tg = obter_totais()
            periodo = 'Todo o histórico'
    else:
        te, tg = obter_totais()
        periodo = 'Todo o histórico'
    
    saldo = te - tg
    
    if saldo > 0:
        classe_saldo = 'saldo-positivo'
    elif saldo < 0:
        classe_saldo = 'saldo-negativo'
    else:
        classe_saldo = 'saldo-zero'
    
    conteudo = f"""
    <div class="card">
        <h2>Resumo Geral</h2>
        <form method="post">
            <p style="margin:10px 0; font-weight:bold;">Filtrar por período (DD/MM/AAAA):</p>
            <div class="linha">
                <input type="text" name="data_inicio" placeholder="Ex: 01/10/2026" value="{di}">
                <input type="text" name="data_fim" placeholder="Ex: 31/10/2026" value="{df}">
            </div>
            <div style="display:flex; gap:10px; margin-top:15px;">
                <button type="submit" class="btn-filtrar" style="flex:1;">🔍 Filtrar</button>
                <a href="/resumo" class="btn-tudo" style="flex:1;">Mostrar Tudo</a>
            </div>
        </form>
        <p style="margin:20px 0; font-weight:bold; font-size:16px;">Período: {periodo}</p>
        <div style="font-size:18px; margin:15px 0; padding:10px; background:#e8f5e9; border-radius:6px;">
            💰 Total Entregas: <strong style="color:#27ae60;">R$ {te:.2f}</strong>
        </div>
        <div style="font-size:18px; margin:15px 0; padding:10px; background:#ffebee; border-radius:6px;">
            💸 Total Gastos: <strong style="color:#e74c3c;">R$ {tg:.2f}</strong>
        </div>
        <div style="font-size:22px; margin-top:20px; padding:20px; background:#f0f0f0; border-radius:6px; text-align:center;">
            ⚖️ Saldo: <span class="{classe_saldo}">R$ {saldo:.2f}</span>
        </div>
        <a href="/" class="voltar">⬅️ Voltar ao Menu</a>
    </div>
    """
    return gerar_html(conteudo)

# Inicializar e rodar
inicializar_banco()
if __name__ == '__main__':
    print("🚀 Servidor iniciado!")
    print("📋 Acesse no navegador: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)