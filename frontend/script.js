document.addEventListener('DOMContentLoaded', (event) => {
    const dateElement = document.getElementById('currentDate');
    const today = new Date();
    dateElement.textContent = today.toLocaleDateString('pt-BR');
  });
  