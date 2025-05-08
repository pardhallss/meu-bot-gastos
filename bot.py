import telebot
import os
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

ARQUIVO_GASTOS = "gastos.txt"
ARQUIVO_SALDO = "saldo.txt"

def ler_arquivo(nome_arquivo):
    if not os.path.exists(nome_arquivo):
        return ""
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        return f.read()

def escrever_arquivo(nome_arquivo, conteudo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)

def adicionar_gasto(valor, descricao, usuario):
    dados = ler_arquivo(ARQUIVO_GASTOS)
    novo_gasto = f"{valor} - {descricao} - {usuario}\n"
    escrever_arquivo(ARQUIVO_GASTOS, dados + novo_gasto)

def calcular_saldo():
    saldo = ler_arquivo(ARQUIVO_SALDO)
    if not saldo:
        return 0.0
    return float(saldo)

def atualizar_saldo(novo_saldo):
    escrever_arquivo(ARQUIVO_SALDO, str(novo_saldo))

@bot.message_handler(commands=["menu"])
def menu(message):
    bot.reply_to(message,
        "📊 *Menu de Controle de Gastos:*\n\n"
        "1️⃣ Enviar gasto (Exemplo: 50 mercado)\n"
        "2️⃣ /relatoriosemanal - Relatório semanal\n"
        "3️⃣ /relatoriomensal - Relatório mensal\n"
        "4️⃣ /excluir - Excluir um gasto\n"
        "5️⃣ /zerar - Zerar gastos\n"
        "6️⃣ /saldo - Ver saldo\n"
        "7️⃣ /carteira - Adicionar saldo\n"
        "8️⃣ /ajuda - Ajuda com comandos",
        parse_mode="Markdown")

@bot.message_handler(commands=["carteira"])
def carteira(message):
    try:
        partes = message.text.split()
        if len(partes) < 2:
            bot.reply_to(message, "Use: /carteira <valor>")
            return
        valor = float(partes[1])
        atualizar_saldo(valor)
        bot.reply_to(message, f"💰 Saldo da carteira definido como: R$ {valor:.2f}")
    except ValueError:
        bot.reply_to(message, "Use: /carteira <valor>")

@bot.message_handler(commands=["saldo"])
def saldo(message):
    saldo_atual = calcular_saldo()
    bot.reply_to(message, f"💰 Saldo atual: R$ {saldo_atual:.2f}")

@bot.message_handler(commands=["zerar"])
def zerar(message):
    escrever_arquivo(ARQUIVO_GASTOS, "")
    bot.reply_to(message, "✅ Todos os gastos foram zerados.")

@bot.message_handler(commands=["excluir"])
def excluir(message):
    try:
        partes = message.text.split()
        if len(partes) < 2:
            bot.reply_to(message, "Use: /excluir <número>")
            return
        numero = int(partes[1]) - 1
        linhas = ler_arquivo(ARQUIVO_GASTOS).strip().split("\n")
        if 0 <= numero < len(linhas):
            gasto = linhas.pop(numero)
            escrever_arquivo(ARQUIVO_GASTOS, "\n".join(linhas) + "\n")
            bot.reply_to(message, f"Gasto excluído: {gasto}")
        else:
            bot.reply_to(message, "Número inválido.")
    except (ValueError, IndexError):
        bot.reply_to(message, "Use: /excluir <número>")

@bot.message_handler(commands=["relatoriomensal", "relatoriosemanal"])
def relatorios(message):
    dados = ler_arquivo(ARQUIVO_GASTOS)
    if not dados.strip():
        bot.reply_to(message, "Nenhum gasto registrado.")
        return
    resposta = "*📋 Relatório de Gastos:*"
    for i, linha in enumerate(dados.strip().split("\n"), 1):
        resposta += f"\n{i}. {linha}"
    bot.reply_to(message, resposta, parse_mode="Markdown")

@bot.message_handler(commands=["ajuda"])
def ajuda(message):
    menu(message)

@bot.message_handler(func=lambda msg: True)
def gastos_rapidos(message):
    try:
        partes = message.text.split()
        if len(partes) < 2:
            return
        valor = float(partes[0])
        descricao = " ".join(partes[1:])
        saldo = calcular_saldo()
        if valor > saldo:
            bot.reply_to(message, "❌ Saldo insuficiente.")
            return
        adicionar_gasto(valor, descricao, message.from_user.first_name)
        atualizar_saldo(saldo - valor)
        bot.reply_to(message, f"✅ Gasto registrado: R$ {valor:.2f} com {descricao}")
    except ValueError:
        pass

# --- Flask + Webhook config para Render gratuito ---
@app.route(f"/{TOKEN}", methods=["POST"])
def receber():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/", methods=["GET"])
def verificar():
    return "Bot está rodando!", 200

# Start do Webhook
if __name__ == "__main__":
    import logging
    from threading import Thread

    url_base = os.getenv("RENDER_EXTERNAL_URL")  # Render define essa variável automaticamente
    if url_base:
        webhook_url = f"{url_base}/{TOKEN}"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
