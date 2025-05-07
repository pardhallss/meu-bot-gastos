import telebot
import os
import datetime

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
    dados = ler_arquivo(ARQUIVO_GASTOS)
    data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    novo_gasto = f"{valor} - {descricao} - {usuario} - {data}\n"
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
        "1️⃣ Enviar gasto (Exemplo: 50 cinema)\n"
        "2️⃣ /relatorio_semanal - Relatório de gastos semanal\n"
        "3️⃣ /relatorio_mensal - Relatório de gastos mensal\n"
        "4️⃣ /excluir - Excluir um gasto específico\n"
        "5️⃣ /zerar - Zerar os gastos\n"
        "6️⃣ /saldo - Ver saldo da carteira\n"
        "7️⃣ /carteira - Definir novo saldo\n"
        "8️⃣ /ajuda - Ajuda com comandos",
        parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def processar_gasto(message):
    try:
        partes = message.text.split()
        if len(partes) < 2:
            return
        valor = float(partes[0])
        descricao = " ".join(partes[1:])
        saldo_atual = calcular_saldo()
        if valor > saldo_atual:
            bot.reply_to(message, "❌ Saldo insuficiente.")
            return
        novo_saldo = saldo_atual - valor
        atualizar_saldo(novo_saldo)
        adicionar_gasto(valor, descricao, message.from_user.first_name)
        bot.reply_to(message, f"Gasto de R$ {valor:.2f} registrado: {descricao}")
    except ValueError:
        pass  # Ignora qualquer mensagem que não tenha o formato correto de valor + descrição

@bot.message_handler(commands=["relatorio_semanal"])
def relatorio_semanal(message):
    dados = ler_arquivo(ARQUIVO_GASTOS).strip().split("\n")
    semana_atual = datetime.datetime.now().isocalendar()[1]
    gastos_semanal = []
    for linha in dados:
        data_gasto = linha.split(" - ")[3]
        data_gasto = datetime.datetime.strptime(data_gasto, "%Y-%m-%d %H:%M:%S")
        if data_gasto.isocalendar()[1] == semana_atual:
            gastos_semanal.append(linha)
    if not gastos_semanal:
        bot.reply_to(message, "Nenhum gasto registrado nesta semana.")
        return
    resposta = "*📊 Relatório de Gastos Semanal:*"
    for i, gasto in enumerate(gastos_semanal, 1):
        resposta += f"{i}. {gasto}\n"
    bot.reply_to(message, resposta, parse_mode="Markdown")

@bot.message_handler(commands=["relatorio_mensal"])
def relatorio_mensal(message):
    dados = ler_arquivo(ARQUIVO_GASTOS).strip().split("\n")
    mes_atual = datetime.datetime.now().month
    gastos_mensal = []
    for linha in dados:
        data_gasto = linha.split(" - ")[3]
        data_gasto = datetime.datetime.strptime(data_gasto, "%Y-%m-%d %H:%M:%S")
        if data_gasto.month == mes_atual:
            gastos_mensal.append(linha)
    if not gastos_mensal:
        bot.reply_to(message, "Nenhum gasto registrado neste mês.")
        return
    resposta = "*📊 Relatório de Gastos Mensal:*"
    for i, gasto in enumerate(gastos_mensal, 1):
        resposta += f"{i}. {gasto}\n"
    bot.reply_to(message, resposta, parse_mode="Markdown")

@bot.message_handler(commands=["excluir"])
def excluir_gasto(message):
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
        bot.reply_to(message, "Use: /excluir <número válido>")

@bot.message_handler(commands=["zerar"])
def zerar_gastos(message):
    escrever_arquivo(ARQUIVO_GASTOS, "")
    bot.reply_to(message, "✅ Todos os gastos foram zerados.")

@bot.message_handler(commands=["saldo"])
def saldo(message):
    saldo_atual = calcular_saldo()
    bot.reply_to(message, f"💰 Saldo atual: R$ {saldo_atual:.2f}")

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

@bot.message_handler(commands=["ajuda"])
def ajuda(message):
    bot.reply_to(message,
        "Comandos disponíveis:\n"
        "/menu - Exibir menu de comandos\n"
        "Enviar gasto - Exemplo: 50 cinema\n"
        "/relatorio_semanal - Relatório de gastos semanal\n"
        "/relatorio_mensal - Relatório de gastos mensal\n"
        "/excluir - Excluir um gasto específico\n"
        "/zerar - Zerar todos os gastos\n"
        "/saldo - Ver saldo da carteira\n"
        "/carteira - Definir saldo da carteira")

bot.infinity_polling()
