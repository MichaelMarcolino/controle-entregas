from flask import Flask, request, redirect, url_for
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)

# ================= CONEXÃO BANCO SUPABASE =================
def conectar_banco():
    conn_str = "postgresql://postgres:NF5yvdlJqna0gidO@db.ghqulurcxvsncmvtbrzt.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

# ================= INICIALIZAR TABELAS =================
def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            id SERIAL PRIMARY KEY,
            data TEXT NOT NULL,
            descricao TEXT,
            valor NUMERIC(10,2) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id SERIAL PRIMARY KEY,
            data TEXT NOT NULL,
            descricao TEXT,
            valor NUMERIC(10,2) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ================= FUNÇÕES =================
def adicionar_entrega(desc, valor):
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO entregas (data, descricao, valor) VALUES (%s, %s, %s)", (data, desc, valor))
    conn.commit()
    conn.close()

def excluir_entrega(registro_id):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entregas WHERE id = %s", (registro_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False

def adicionar_gasto(desc, valor):
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos (data, descricao, valor) VALUES (%s, %s, %s)", (data, desc, valor))
    conn.commit()
    conn.close()

def excluir_gasto(registro_id):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gastos WHERE id = %s", (registro_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False

def listar_entregas(data_inicio=None, data_fim=None):
    conn = conectar_banco()
    cursor = conn.cursor()
    if data_inicio and data_fim:
        cursor.execute("""
            SELECT * FROM entregas 
            WHERE SUBSTR(data, 1, 10) BETWEEN %s AND %s
            ORDER BY id DESC
        """, (data_inicio, data_fim))
    else:
        cursor.execute("SELECT * FROM entregas ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados

def listar_gastos(data_inicio=None, data_fim=None):
    conn = conectar_banco()
    cursor = conn.cursor()
    if data_inicio and data_fim:
        cursor.execute("""
            SELECT * FROM gastos 
            WHERE SUBSTR(data, 1, 10) BETWEEN %s AND %s
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
    total_e = sum(float(x[3]) for x in e) if e else 0
    total_g = sum(float(x[3]) for x in g) if g else 0
    return total_e, total_g

# ================= TEMPLATE =================
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
        body {{ background: #f5f5f5; padding: 20px; max-width: 500px; margin: 0 auto; }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        .menu {{ display: flex; flex-direction: column; gap: 12px; margin-bottom: 30px; }}
        .menu a {{ padding: 15px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 17px; text-align: center; }}
        .btn-verde {{ background: #27ae60; color: white; }}
        .btn-vermelho {{ background: #e74c3c; color: white; }}
        .btn-azul {{ background: #3498db; color: white; }}
        .btn-cinza {{ background: #95a5a6; color: white; }}
        .card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h2 {{ color: #2c3e50; margin-bottom: 20px; text-align: center; }}
        input {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; }}
        button {{ padding: 12px 25px; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; width: 100%; }}
        .msg {{ padding: 12px; border-radius: 6px; margin: 10px 0; text-align: center; font-weight: bold; }}
        .sucesso {{ background: #d4edda; color: #155724; }}
        .erro {{ background: #f8d7da; color: #721c24; }}
        .lista {{ margin-top: 15px; }}
        .item {{ padding: 15px 12px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }}
        .item-data {{ font-size: 13px; color: #7f8c8d; }}
        .item-desc {{ font-weight: bold; color: #2c3e50; }}
        .item-valor {{ color: #27ae60; font-weight: bold; margin-top: 4px; }}
        .btn-excluir {{ background: #e74c3c; color: white; border: none; padding: 8px 12px; border-radius: 6px; font-size: 14px; cursor: pointer; width: auto; text-decoration: none; }}
        .total {{ margin-top: 15px; font-size: 18px; font-weight: bold; text-align: right; padding: 12px; background: #f0f0f0; border-radius: 6px; }}
        .voltar {{ display: inline-block; margin-top: 20px; color: #3498db; text-decoration: none; }}
        .linha {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .linha input {{ flex: 1; min-width: 140px; }}
        .btn-filtrar {{ background: #3498db; color: white; border: none; padding: 12px; border-radius: 6px; font-size: 16px; font-weight: bold; }}
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
        <h2>Cadastrar Entrega</h2>{msg}
        <form method="post">
            <input type="text" name="descricao" placeholder="Descrição">
            <input type="number" step="0.01" name="valor" placeholder="Valor R$" required>
            <button type="submit" class="btn-verde">💾 Salvar</button>
        </form>
        <a href="/" class="voltar">⬅️ Voltar</a>
    </div>"""
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
        <h2>Cadastrar Gasto</h2>{msg}
        <form method="post">
            <input type="text" name="descricao" placeholder="Descrição">
            <input type="number" step="0.01" name="valor" placeholder="Valor R$" required>
            <button type="submit" class="btn-vermelho">💾 Salvar</button>
        </form>
        <a href="/" class="voltar">⬅️ Voltar</a>
    </div>"""
    return gerar_html(conteudo)

@app.route('/excluir/entrega/<int:registro_id>')
def rota_excluir_entrega(registro_id):
    excluir_entrega(registro_id)
    return redirect('/historico/entregas')

@app.route('/excluir/gasto/<int:registro_id>')
def rota_excluir_gasto(registro_id):
    excluir_gasto(registro_id)
    return redirect('/historico/gastos')

@app.route('/historico/entregas')
def his_entregas():
    dados = listar_entregas()
    total = sum(float(x[3]) for x in dados) if dados else 0
    itens = ''
    if dados:
        for d in dados:
            itens += f'''
            <div class="item">
                <div>
                    <div class="item-data">{d[1]}</div>
                    <div class="item-desc">{d[2]}</div>
                    <div class="item-valor">R$ {float(d[3]):.2f}</div>
                </div>
                <a href="/excluir/entrega/{d[0]}" class="btn-excluir" onclick="return confirm('Tem certeza?')">🗑️ Excluir</a>
            </div>'''
        itens += f'<div class="total">💰 Total: R$ {total:.2f}</div>'
    else:
        itens = '<p style="text-align:center; color:#7f8c8d; padding:20px;">Nenhuma entrega cadastrada</p>'
    conteudo = f'<div class="card"><h2>Histórico de Entregas</h2><div class="lista">{itens}</div><a href="/" class="voltar">⬅️ Voltar</a></div>'
    return gerar_html(conteudo)

@app.route('/historico/gastos')
def his_gastos():
    dados = listar_gastos()
    total = sum(float(x[3]) for x in dados) if dados else 0
    itens = ''
    if dados:
        for d in dados:
            itens += f'''
            <div class="item">
                <div>
                    <div class="item-data">{d[1]}</div>
                    <div class="item-desc">{d[2]}</div>
                    <div class="item-valor" style="color:#e74c3c;">R$ {float(d[3]):.2f}</div>
                </div>
                <a href="/excluir/gasto/{d[0]}" class="btn-excluir" onclick="return confirm('Tem certeza?')">🗑️ Excluir</a>
            </div>'''
        itens += f'<div class="total">💸 Total: R$ {total:.2f}</div>'
    else:
        itens = '<p style="text-align:center; color:#7f8c8d; padding:20px;">Nenhum gasto cadastrado</p>'
    conteudo = f'<div class="card"><h2>Histórico de Gastos</h2><div class="lista">{itens}</div><a href="/" class="voltar">⬅️ Voltar</a></div>'
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
    classe_saldo = 'saldo-positivo' if saldo > 0 else ('saldo-negativo' if saldo < 0 else 'saldo-zero')
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
        <p style="margin:20px 0; font-weight:bold;">Período: {periodo}</p>
        <div style="font-size:18px; margin:15px 0; padding:12px; background:#e8f5e9; border-radius:6px;">
            💰 Total Entregas: <strong style="color:#27ae60;">R$ {te:.2f}</strong>
        </div>
        <div style="font-size:18px; margin:15px 0; padding:12px; background:#ffebee; border-radius:6px;">
            💸 Total Gastos: <strong style="color:#e74c3c;">R$ {tg:.2f}</strong>
        </div>
        <div style="font-size:22px; margin-top:20px; padding:20px; background:#f0f0f0; border-radius:6px; text-align:center;">
            ⚖️ Saldo: <span class="{classe_saldo}">R$ {saldo:.2f}</span>
        </div>
        <a href="/" class="voltar">⬅️ Voltar</a>
    </div>"""
    return gerar_html(conteudo)

# Inicializar banco
inicializar_banco()

app = app
