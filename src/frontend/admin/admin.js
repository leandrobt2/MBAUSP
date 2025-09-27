async function loadEnquadramentos() {
    try {
        const response = await fetch('http://localhost:3000/api/enquadramentos/pendentes', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const enquadramentos = await response.json();
            const container = document.getElementById('enquadramentosList');
            container.innerHTML = '';

            enquadramentos.forEach(item => {
                const element = document.createElement('div');
                element.className = 'list-group-item';
                element.innerHTML = `
                    <h5>${item.razaoSocial}</h5>
                    <p>CNAE: ${item.cnae}</p>
                    <p>Sugestão do ML: ${item.sugestaoSindicato}</p>
                    <button class="btn btn-success me-2" onclick="aprovar(${item.id})">Aprovar</button>
                    <button class="btn btn-warning" onclick="corrigir(${item.id})">Corrigir</button>
                `;
                container.appendChild(element);
            });
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar enquadramentos pendentes.');
    }
}

async function aprovar(id) {
    try {
        const response = await fetch(`http://localhost:3000/api/enquadramentos/${id}/aprovar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            alert('Enquadramento aprovado com sucesso!');
            loadEnquadramentos();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao aprovar enquadramento.');
    }
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', loadEnquadramentos);