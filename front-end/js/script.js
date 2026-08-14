const API_URL = 'http://127.0.0.1:8000/api';

document.addEventListener('DOMContentLoaded', loadDecisions);

async function loadDecisions() {
    const container = document.getElementById('decisions-container');
    container.innerHTML = '<p class="empty-state">Sincronizando com o agente...</p>';

    try {
        const response = await fetch(`${API_URL}/decisions`);
        const data = await response.json();

        if (data.decisions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>Tudo tranquilo por aqui! ✅</h3>
                    <p>Seu agente está trabalhando em segundo plano. Nenhuma decisão pendente no momento.</p>
                </div>`;
            return;
        }

        container.innerHTML = '';
        data.decisions.forEach(decision => {
            const card = document.createElement('div');
            card.classList.add('card');
            card.innerHTML = `
                <h2>⚠️ ${decision.title}</h2>
                <p>${decision.description}</p>
                <div class="draft-box">
                    <strong>Ação Rascunhada pelo Agente:</strong><br><br>
                    "${decision.draft_action}"
                </div>
                <div class="actions">
                    <button class="btn-approve" onclick="handleAction('${decision.id}', 'approve')">Aprovar Envio</button>
                    <button class="btn-reject" onclick="handleAction('${decision.id}', 'reject')">Ignorar</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        container.innerHTML = `
            <div class="empty-state" style="color: #e74c3c;">
                <h3>Erro de Conexão ❌</h3>
                <p>Não foi possível conectar ao Agente. Verifique se o backend (FastAPI) está rodando no terminal.</p>
            </div>`;
        console.error(error);
    }
}

async function handleAction(id, action) {
    try {
        const response = await fetch(`${API_URL}/decisions/${id}/${action}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        // Simples feedback visual
        alert(data.message);
        
        // Recarrega a lista
        loadDecisions();
    } catch (error) {
        alert('Erro ao processar a ação. Verifique a conexão com o servidor.');
    }
}
