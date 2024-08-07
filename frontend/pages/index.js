import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Link from 'next/link';

const Dashboard = () => {
  const [licitacoes, setLicitacoes] = useState([]);
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:3001/data/A Disputar');
        const data = response.data.slice(1); // Remove header row
        console.log('Dados recebidos da API:', data);

        const filteredData = data.filter(licitacao => {
          const [dia, mes, ano] = licitacao[0].split('/');
          const licitacaoDate = new Date(`${ano}-${mes}-${dia}T${licitacao[7]}:00`); // Ajuste aqui se necessário
          const now = new Date();
          const isFuture = licitacaoDate > now;
          const isTodayBeforeSixPM = licitacaoDate.toDateString() === now.toDateString() && now.getHours() < 18;
          return isFuture || isTodayBeforeSixPM;
        });

        console.log('Dados filtrados:', filteredData);
        setLicitacoes(filteredData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');
      const date = now.toLocaleDateString('pt-BR');
      setCurrentTime(`${date} ${hours}:${minutes}:${seconds}`);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <div className="sidebar">
        <nav>
          <ul>
            <li><Link href="/" legacyBehavior><a>Dashboard</a></Link></li>
            <li><Link href="/a-disputar" legacyBehavior><a>Licitações a Disputar</a></Link></li>
            <li><Link href="/a-verificar" legacyBehavior><a>Licitações a Selecionar</a></Link></li>
            <li><Link href="/configuracoes" legacyBehavior><a>Configurações</a></Link></li>
          </ul>
        </nav>
      </div>
      <div className="content">
        <div className="header">
          <h1>Bem-vindo ao Sistema UNA de Licitações</h1>
          <div className="clock">
            {currentTime}
          </div>
        </div>
        <h2>Próximas Licitações</h2>
        <div className="grid">
          {licitacoes.map((licitacao, index) => (
            <div key={index} className="card">
              <p className="date"><strong>Data de Abertura:</strong> {licitacao[0]}</p>
              <p className="hour"><strong>Prazo de Abertura (Hora):</strong> {licitacao[7]}</p>
              <p className="organization"><strong>Órgão Licitante:</strong> {licitacao[6]}</p>
              <p className="location"><strong>Cidade:</strong> {licitacao[8]}</p>
              <p className="value"><strong>Valor:</strong> R$ {licitacao[4]}</p>
              <Link href={`/detalhes/${index}`} legacyBehavior>
                <a>Ver Detalhes</a>
              </Link>
            </div>
          ))}
        </div>
      </div>
      <style jsx>{`
        .container {
          display: flex;
          height: 100vh;
        }
        .sidebar {
          width: 250px;
          background: #2c3e50;
          padding: 1rem;
          color: #ecf0f1;
        }
        .sidebar nav ul {
          list-style: none;
          padding: 0;
        }
        .sidebar nav ul li {
          margin-bottom: 1rem;
        }
        .sidebar nav ul li a {
          color: #ecf0f1;
          text-decoration: none;
          font-weight: bold;
        }
        .content {
          flex-grow: 1;
          padding: 2rem;
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .clock {
          font-size: 1.5rem;
          font-weight: bold;
          color: #000;
        }
        .content h1 {
          margin-bottom: 1rem;
          color: #2c3e50;
        }
        .content h2 {
          margin-bottom: 1rem;
          color: #2c3e50;
        }
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1rem;
        }
        .card {
          background: #fff;
          padding: 1rem;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .date, .hour, .organization, .location, .value {
          margin-bottom: 0.5rem;
        }
        .date {
          font-size: 1.2rem;
          font-weight: bold;
        }
        .title {
          font-size: 1rem;
          margin: 0.5rem 0;
        }
        .location {
          font-size: 0.9rem;
          color: #7f8c8d;
        }
        .value {
          font-size: 1rem;
          color: #2c3e50;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
