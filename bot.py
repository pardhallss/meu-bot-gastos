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

@bot.message_handler(commands=["menu"])
def menu(message):
    bot.reply_to(message,
        "📊 *Menu de Controle de Gastos:*\n\n"
        "1️⃣ /adicionar - Adicionar novo gasto\n"
        "2️⃣ /listar - Ver todos os gastos\n"
        "3️⃣ /total - Ver total de gastos\n"
        "4️⃣ /estatisticas - Estatísticas gerais\n"
        "5️⃣ /relatorio - Relatório semanal/mensal\n"
        "6️⃣ /excluir - Excluir um gasto\n"
        "7️⃣ /zerar - Zerar os gastos\n"
        "8️⃣ /saldo - Ver saldo da carteira\n"
        "9️⃣ /carteira - Definir novo saldo\n"
        "🔟 /ajuda - Ajuda com comandos",
        parse_mode="Markdown")

@bot.message_handler(commands=["adicionar"])
def adicionar(message):
    try:
        partes = message.text.split()
        if len(partes) < 3:
            bot.reply_to(message, "Use: /adicionar <valor> <descrição>")
            return
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
    except ValueError:
        bot.reply_to(message, "Use: /adicionar <valor> <descrição>")

@bot.message_handler(commands=["listar"])
def listar_gastos(message):
    dados = ler_arquivo(ARQUIVO_GASTOS)
    if not dados.strip():
        bot.reply_to(message, "Nenhum gasto registrado.")
        return
    resposta = "*🧾 Lista de Gastos:*"
    linhas = dados.strip().split("\n")
    for i, linha in enumerate(linhas, 1):
        resposta += f"{i}. {linha}\n"
    bot.reply_to(message, resposta, parse_mode="Markdown")

@bot.message_handler(commands=["total"])
def total(message):
    dados = ler_arquivo(ARQUIVO_GASTOS)
    total = 0.0
    if dados.strip():
        for linha in dados.strip().split("\n"):
            total += float(linha.split(" - ")[0])
    bot.reply_to(message, f"📈 Total gasto: R$ {total:.2f}")

@bot.message_handler(commands=["estatisticas"])
def estatisticas(message):
    dados = ler_arquivo(ARQUIVO_GASTOS)
    total = 0
    if dados.strip():
        for linha in dados.strip().split("\n"):
            total += float(linha.split(" - ")[0])
    bot.reply_to(message, f"📈 Total gasto: R$ {total:.2f}")

@bot.message_handler(commands=["relatorio"])
def relatorio(message):
    linhas = ler_arquivo(ARQUIVO_GASTOS).strip().split("\n")
    if not linhas or not linhas[0]:
        bot.reply_to(message, "Nenhum gasto registrado para o relatório.")
        return
    resposta = "*📋 Relatório de Gastos:*"
    for i, linha in enumerate(linhas, 1):
        resposta += f"{i}. {linha}\n"
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
        "/adicionar - Adicionar um novo gasto\n"
        "/listar - Listar todos os gastos\n"
        "/total - Ver total de gastos\n"
        "/estatisticas - Ver estatísticas gerais\n"
        "/relatorio - Ver relatório de gastos\n"
        "/excluir - Excluir um gasto\n"
        "/zerar - Zerar todos os gastos\n"
        "/saldo - Ver saldo da carteira\n"
        "/carteira - Definir saldo da carteira")

bot.infinity_polling()

