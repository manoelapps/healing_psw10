const inputDtInicial = document.querySelector("input[name='dt-inicial']");

inputDtInicial.addEventListener('change', (e) => {

    const urlParams = new URLSearchParams(window.location.search);

    urlParams.set('dt-inicial', inputDtInicial.value);
    window.location.search = urlParams;
});
