import uvicorn
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =====================================================================
# 1. LÓGICA DO AGENTE (Simulando Strands Agents SDK e AWS AgentCore)
# =====================================================================

def analisar_fatura_mock(fatura_id: str, valor_atual: float, valor_medio_historico: float) -> Dict:
    """Tool: Analisa uma fatura recebida contra o histórico."""
    diferenca = valor_atual - valor_medio_historico
    if diferenca > 10.0:
        return {
            "status": "ANOMALIA_DETECTADA",
            "diferenca": diferenca,
            "acao_recomendada": "CONTESTAR_COBRANCA"
        }
    return {"status": "OK", "acao_recomendada": "AGENDAR_PAGAMENTO"}

def gerar_rascunho_contestacao_mock(fornecedor: str, valor_extra: float) -> str:
    """Tool: Gera um texto formal para contestação."""
    return f"Solicito o estorno de R$ {valor_extra:.2f} referente ao serviço cobrado indevidamente na fatura da {fornecedor}."


# =====================================================================
# 2. LÓGICA DA API / SERVIDOR BACKEND
# =====================================================================

app = FastAPI()

# Permite que o frontend (HTML/JS local) faça requisições para essa API sem bloqueios
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# "Banco de dados" simulado para as decisões pausadas esperando a aprovação humana
pending_decisions = [
    {
        "id": "1",
        "title": "Aumento na Conta de Internet",
        "description": "Sua fatura da provedora FibraMax veio R$ 40,00 acima do histórico. Detectei um 'Pacote Premium' não solicitado que foi adicionado.",
        "draft_action": "Solicito o cancelamento imediato e estorno de R$ 40,00 referente ao 'Pacote Premium' cobrado indevidamente na fatura do mês atual.",
        "status": "pending"
    }
]

@app.get("/api/decisions")
def get_decisions():
    """Retorna as decisões que precisam de atenção humana."""
    return {"decisions": [d for d in pending_decisions if d["status"] == "pending"]}

@app.post("/api/decisions/{decision_id}/approve")
def approve_decision(decision_id: str):
    """O usuário aprovou a ação sugerida pelo agente."""
    for d in pending_decisions:
        if d["id"] == decision_id:
            d["status"] = "approved"
            return {"message": "Ação executada com sucesso! O e-mail de contestação foi enviado pelo agente em segundo plano."}
    return {"error": "Decisão não encontrada"}

@app.post("/api/decisions/{decision_id}/reject")
def reject_decision(decision_id: str):
    """O usuário rejeitou a ação sugerida pelo agente."""
    for d in pending_decisions:
        if d["id"] == decision_id:
            d["status"] = "rejected"
            return {"message": "Ação ignorada. O agente agendará o pagamento normalmente."}
    return {"error": "Decisão não encontrada"}


# =====================================================================
# 3. INICIADOR DO SERVIDOR (Para rodar direto com `python main.py`)
# =====================================================================
if __name__ == "__main__":
    print("Iniciando o servidor do SmartGuardian na porta 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
