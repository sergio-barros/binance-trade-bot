# Binance Trade Bot

🚀 Um bot de trade automatizado para a Binance usando Python, integração via API, e estratégias de médias móveis com controle de preço médio, Take Profit e Stop Loss.

---

## 📋 Funcionalidades

- Compra e venda automática baseada em cruzamento de médias móveis.
- Controle de **Take Profit** (lucro) e **Stop Loss** (proteção contra perdas).
- Verificação automática de saldo disponível.
- Registro de todas as operações em arquivo CSV (`trades_history.csv`).
- Resumo diário enviado automaticamente via **Telegram**.
- Operações a cada 15 minutos (ou customizável).
- Configurações flexíveis via arquivo `.env`.

---

## ⚙️ Tecnologias utilizadas

- **Python 3.10+**
- **Binance API** (`python-binance`)
- **Dotenv** para configuração via `.env`
- **Schedule** para agendamento de execuções
- **Telegram Bot API** para alertas

---

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/binance-trade-bot.git
cd binance-trade-bot
```

2. Crie o ambiente virtual e instale dependências:
```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

3. Crie o seu arquivo .env baseado no modelo .env.example.

4. Execute o bot:
```bash
python main.py
```

📊 Estrutura de pastas
binance-trade-bot/
├── trading/
│   ├── executor.py
│   ├── simple_strategy.py
├── services/
│   ├── binance_client.py
│   ├── data_fetcher.py
│   ├── telegram_alert.py
├── config.py
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
└── trades_history.csv (gerado automaticamente)

🛡️ Avisos importantes
Nunca compartilhe seu arquivo .env!

Faça testes iniciais em ambiente de simulação (testnet).

Lembre-se que este projeto é apenas para fins educacionais.

📚 Contribuições
Pull Requests são bem-vindos! 🚀

📜 Licença
Distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

✨ Desenvolvido por
Sergio Fabiano Martins de Barros