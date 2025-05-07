
import telebot
import os

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
    novo_gasto = f"{valor} - {descricao} - {usuario}\n"
    escrever_arquivo(ARQUIVO_GASTOS, dados + novo_gasto)

def calcular_saldo():
    saldo = ler_arquivo(ARQUIVO_SALDO)
    if not saldo:
        return 0.0
    return float(saldo)

def atualizar_saldo(novo_saldo):
    escrever_arquivo(ARQUIVO_SALDO, str(novo_saldo))

@bot.message_handler(commands=["start", "menu"])
def menu(message):
    texto = (
        "📊 *Menu de Controle de Gastos:*

"
        "/gastar <valor> <descrição>
"
        "/saldo - Ver saldo atual
"
        "/definir_saldo <valor>
"
        "/gastos - Ver gastos
"
        "/estatisticas
"
        "/relatorio_semanal
"
        "/relatorio_mensal
"
        "/zerar_semanal
"
        "/zerar_mensal
"
        "/excluir <número>"
    )
    bot.reply_to(message, texto, parse_mode="Markdown")

@bot.message_handler(commands=["definir_saldo"])
def definir_saldo(message):
    try:
        valor = float(message.text.split()[1])
        atualizar_saldo(valor)
        bot.reply_to(message, f"💰 Saldo definido como R$ {valor:.2f}")
    except:
        bot.reply_to(message, "Use: /definir_saldo <valor>")

@bot.message_handler(commands=["saldo"])
def saldo(message):
    saldo_atual = calcular_saldo()
    bot.reply_to(message, f"💰 Saldo atual: R$ {saldo_atual:.2f}")

@bot.message_handler(commands=["gastar"])
def gastar(message):
    try:
        partes = message.text.split()
        valor = float(partes[1])
        descricao = " ".join(partes[2:])
        saldo_atual = calcular_saldo()
        if valor > saldo_atual:
            bot.reply_to(message, "❌ Saldo insuficiente.")
            return
        novo_saldo = saldo_atual - valor
        atualizar_saldo(novo_saldo)
        adicionar_gasto(valor, descricao, message.from_user.first_name)
        bot.reply_to(message, f"Gasto de R$ {valor:.2f} registrado: {descricao}")
    except:
        bot.reply_to(message, "Use: /gastar <valor> <descrição>")

@bot.message_handler(commands=["gastos"])
def listar_gastos(message):
    dados = ler_arquivo(ARQUIVO_GASTOS)
    if not dados.strip():
        bot.reply_to(message, "Nenhum gasto registrado.")
        return
    resposta = "*🧾 Lista de Gastos:*

"
    linhas = dados.strip().split("\n")
    for i, linha in enumerate(linhas, 1):
        resposta += f"{i}. {linha}\n"
    bot.reply_to(message, resposta, parse_mode="Markdown")

@bot.message_handler(commands=["excluir"])
def excluir_gasto(message):
    try:
        numero = int(message.text.split()[1]) - 1
        linhas = ler_arquivo(ARQUIVO_GASTOS).strip().split("\n")
        if 0 <= numero < len(linhas):
            gasto = linhas.pop(numero)
            escrever_arquivo(ARQUIVO_GASTOS, "\n".join(linhas) + "\n")
            bot.reply_to(message, f"Gasto excluído: {gasto}")
        else:
            bot.reply_to(message, "Número inválido.")
    except:
        bot.reply_to(message, "Use: /excluir <número>")

@bot.message_handler(commands=["estatisticas"])
def estatisticas(message):
    linhas = ler_arquivo(ARQUIVO_GASTOS).strip().split("\n")
    total = 0
    for linha in linhas:
        if linha:
            total += float(linha.split(" - ")[0])
    bot.reply_to(message, f"📈 Total gasto: R$ {total:.2f}")

@bot.message_handler(commands=["relatorio_semanal", "relatorio_mensal"])
def relatorio(message):
    tipo = "semanal" if "semanal" in message.text else "mensal"
    linhas = ler_arquivo(ARQUIVO_GASTOS).strip().split("\n")
    if not linhas or not linhas[0]:
        bot.reply_to(message, f"Nenhum gasto para o relatório {tipo}.")
        return
    resposta = f"*📋 Relatório {tipo.capitalize()}:*

"
    for i, linha in enumerate(linhas, 1):
        resposta += f"{i}. {linha}\n"
    bot.reply_to(message, resposta, parse_mode="Markdown")

@bot.message_handler(commands=["zerar_semanal", "zerar_mensal"])
def zerar_gastos(message):
    escrever_arquivo(ARQUIVO_GASTOS, "")
    bot.reply_to(message, "✅ Gastos zerados.")

bot.polling()
