import telebot
import os
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

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
    data = datetime.now().strftime("%Y-%m-%d")
    novo_gasto = f"{valor:.2f} - {descricao} - {usuario} - {data}\n"
    dados = ler_arquivo(ARQUIVO_GASTOS)
    escrever_arquivo(ARQUIVO_GASTOS, dados + novo_gasto)

def calcular_saldo():
    saldo = ler_arquivo(ARQUIVO_SALDO)
    if not saldo:
        return 0.0
    try:
        return float(saldo)
    except ValueError:
        return 0.0

def atualizar_saldo(novo_saldo):
    escrever_arquivo(ARQUIVO_SALDO, str(novo_saldo))

@bot.message_handler(commands=["menu"])
def menu(message):
    texto = (
        "📊 *Menu de Controle de Gastos:*\n\n"
        "1️⃣ Enviar gasto (Exemplo: `50 cinema`)\n"
        "2️⃣ /relatorio_semanal - Relatório semanal\n"
        "3️⃣ /relatorio_mensal - Relatório mensal\n"
        "4️⃣ /excluir <número> - Excluir gasto específico\n"
        "5️⃣ /zerar - Zerar os gastos\n"
        "6️⃣ /saldo - Ver saldo atual\n"
        "7️⃣ /carteira <valor> - Definir novo saldo\n"
        "8️⃣ /ajuda - Ajuda com comandos"
    )
    bot.reply_to(message, texto, parse_mode="Markdown")

@bot.message_handler(commands=["carteira"])
def carteira(message):
    try:
        partes = message.text.split()
        if len(partes) < 2:
            bot.reply_to(message, "Use: /carteira <valor>")
            return
        valor = float(partes[1])
        atualizar_saldo(valor)
        bot.reply_to(message, f"💰 Saldo definido como: R$ {valor:.2f}")
    except:
        bot.reply_to(message, "Erro: valor inválido. Exemplo correto: /carteira 100")

@bot.message_handler(commands=["saldo"])
def saldo(message):
    saldo = calcular_saldo()
    bot.reply_to(message, f"💰 Saldo atual: R$ {saldo:.2f}")

@bot.message_handler(commands=["relatorio_semanal", "relatorio_mensal"])
def relatorio(message):
    linhas = ler_arquivo(ARQUIVO_GASTOS).strip().split("\n")
    if not linhas or linhas == ['']:
        bot.reply_to(message, "Nenhum gasto registrado.")
        return
    resposta = "*📋 Relatório de Gastos:*\n"
    for i, linha in enumerate(linhas, 1):
        resposta += f"{i}. {linha}\n"
    bot.reply_to(message, resposta, parse_mode="Markdown")

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
            gasto_removido = linhas.pop(numero)
            escrever_arquivo(ARQUIVO_GASTOS, "\n".join(linhas) + "\n")
            bot.reply_to(message, f"Gasto excluído: {gasto_removido}")
        else:
            bot.reply_to(message, "Número inválido.")
    except:
        bot.reply_to(message, "Erro: Use /excluir <número válido>")

@bot.message_handler(commands=["ajuda"])
def ajuda(message):
    bot.reply_to(message,
        "📌 *Ajuda de Comandos:*\n\n"
        "`50 mercado` — Adiciona gasto\n"
        "`/carteira 100` — Define saldo\n"
        "`/saldo` — Mostra saldo\n"
        "`/zerar` — Limpa todos os gastos\n"
        "`/excluir 2` — Exclui gasto 2\n"
        "`/relatorio_mensal` — Relatório mensal\n"
        "`/menu` — Mostra o menu",
        parse_mode="Markdown")

@bot.message_handler(func=lambda msg: True)
def registrar_gasto_automatico(message):
    texto = message.text.strip()

    # Ignorar se começar com "/"
    if texto.startswith("/"):
        return

    partes = texto.split()
    if len(partes) < 2:
        return

    try:
        valor = float(partes[0])
        descricao = " ".join(partes[1:])
        saldo_atual = calcular_saldo()
        if valor > saldo_atual:
            bot.reply_to(message, "❌ Saldo insuficiente.")
            return
        novo_saldo = saldo_atual - valor
        atualizar_saldo(novo_saldo)
        adicionar_gasto(valor, descricao, message.from_user.first_name)
        bot.reply_to(message, f"✅ Gasto registrado: R$ {valor:.2f} em '{descricao}'\n💰 Novo saldo: R$ {novo_saldo:.2f}")
    except:
        return  # ignora se não for um valor válido

bot.infinity_polling()

