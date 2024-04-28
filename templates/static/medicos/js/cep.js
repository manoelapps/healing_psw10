const inputCep = document.getElementById('cep');

inputCep.addEventListener('blur', (e) => {
    e.preventDefault();

    let cep = inputCep.value;

    if(cep != '') {

        if(isValidCEP(cep)) {

            const options = {
                method: 'GET',
                mode: 'cors',
                cache: 'default'
            }

            fetch(`https://viacep.com.br/ws/${cep}/json/`, options)
            .then(response => {
                response.json()
                .then(data => {
                    if('erro' in data) {
                        alert('\nCEP não localizado !');
                        limpa_formulario_cep();
                    } else {
                        for(const field in data) {
                            let fld = field
                            if(field == 'localidade') {
                                fld = 'cidade'
                            }
                            if(field != 'cep') {
                                if(document.querySelector("input[name='"+fld+"']")) {
                                    document.querySelector("input[name='"+fld+"']").value = data[field];
                                }
                            }
                        }
                    }
                });
            })
            .catch(e => console.log('Erro: ' + e.message))
        }
        else {
            alert('Formato de CEP inválido');
            limpa_formulario_cep();
        }
    }
    else {
        limpa_formulario_cep();
    };
});

function limpa_formulario_cep() {
    document.querySelector("input[name='logradouro']").value = '';
    document.querySelector("input[name='bairro']").value = '';
    document.querySelector("input[name='cidade']").value = '';
    document.querySelector("input[name='uf']").value = '';
}

function isValidCEP(str) {
    let regex = /^\d{5}-?\d{3}$/
    return regex.test(str);
}

