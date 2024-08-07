import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const LicitacoesPage = ({ sheetName }) => {
  const [data, setData] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`http://localhost:3001/data/${sheetName}`);
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [sheetName]);

  const renderCellContent = (header, cell) => {
    if (header === 'Acesso') {
      return (
        <a href={cell} target="_blank" rel="noopener noreferrer">
          <button className="link-button">Acessar</button>
        </a>
      );
    } else if (header === 'Objeto' || header === 'Observações') {
      return (
        <div className="wrap-text">
          {cell}
        </div>
      );
    } else {
      return cell;
    }
  };

  return (
    <div className="container">
      <div className="header">
        <nav>
          <ul>
            <li className={router.pathname === '/' ? 'active' : ''}>
              <Link href="/">Dashboard</Link>
            </li>
            <li className={router.pathname === '/a-disputar' ? 'active' : ''}>
              <Link href="/a-disputar">Licitações a Disputar</Link>
            </li>
            <li className={router.pathname === '/a-verificar' ? 'active' : ''}>
              <Link href="/a-verificar">Licitações a Selecionar</Link>
            </li>
            <li className={router.pathname === '/configuracoes' ? 'active' : ''}>
              <Link href="/configuracoes">Configurações</Link>
            </li>
          </ul>
        </nav>
      </div>
      <h1>{sheetName}</h1>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              {data[0] && data[0].map((header, index) => (
                <th key={index}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.slice(1).map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex}>
                    {renderCellContent(data[0][cellIndex], cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <style jsx>{`
        .container {
          padding: 2rem;
          max-width: 100%;
        }
        .header {
          background: #2c3e50;
          padding: 1rem;
          color: #ecf0f1;
          margin-bottom: 1rem;
        }
        .header nav ul {
          list-style: none;
          padding: 0;
        }
        .header nav ul li {
          display: inline;
          margin-right: 1rem;
        }
        .header nav ul li a {
          color: #ecf0f1;
          text-decoration: none;
          font-weight: bold;
        }
        .header nav ul li.active a {
          color: black;
          background-color: white;
          padding: 0.5rem 1rem;
          border-radius: 5px;
        }
        .table-container {
          width: 100%;
          overflow-x: auto; /* Barra de rolagem horizontal */
        }
        table {
          width: 100%;
          border-collapse: collapse;
          table-layout: auto; /* Deixa o navegador decidir a largura */
        }
        th, td {
          border: 1px solid #ddd;
          padding: 8px;
          text-overflow: ellipsis;
          white-space: pre-wrap; /* Permite que o conteúdo quebre em várias linhas */
          word-wrap: break-word; /* Quebra as palavras longas */
        }
        th {
          background-color: #f2f2f2;
          text-align: left;
          position: sticky;
          top: 0;
          z-index: 10; /* Garante que os cabeçalhos fiquem acima */
        }
        .wrap-text {
          white-space: pre-wrap;
          word-wrap: break-word;
        }
        td:nth-child(2) { /* Ajuste a segunda coluna (Objeto) */
          min-width: 300px;
          max-width: 600px;
        }
        td:nth-child(12) { /* Ajuste a décima segunda coluna (Observações) */
          min-width: 300px;
          max-width: 600px;
        }
        tbody tr:nth-child(even) {
          background-color: #f9f9f9;
        }
        .link-button {
          padding: 5px 10px;
          background-color: #3498db;
          color: white;
          border: none;
          cursor: pointer;
        }
        .link-button:hover {
          background-color: #2980b9;
        }
      `}</style>
    </div>
  );
};

export default LicitacoesPage;
