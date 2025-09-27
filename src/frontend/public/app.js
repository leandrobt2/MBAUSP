document.getElementById('empresaForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        razaoSocial: document.getElementById('razaoSocial').value,
        cnae: document.getElementById('cnae').value,
        cep: document.getElementById('cep').value
    };

    try {
        const response = await fetch('http://localhost:3000/api/empresas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const result = await response.json();
            alert('Cadastro realizado com sucesso! Você receberá um e-mail com o resultado do enquadramento.');
            document.getElementById('empresaForm').reset();
        } else {
            alert('Erro ao cadastrar empresa. Por favor, tente novamente.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao conectar com o servidor. Por favor, tente novamente mais tarde.');
    }
});