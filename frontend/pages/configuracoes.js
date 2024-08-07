import React, { useState } from 'react';
import Link from 'next/link';

const Configuracoes = () => {
  const [directoryPath, setDirectoryPath] = useState('');
  const [downloadFolder, setDownloadFolder] = useState('');
  const [message, setMessage] = useState('');

  const handleDirectoryChange = (event) => {
    if (event.target.files.length > 0) {
      const filePath = event.target.files[0].webkitRelativePath;
      const directory = filePath.substring(0, filePath.indexOf('/'));
      setDirectoryPath(directory);
    }
  };

  const handleDownloadFolderChange = (event) => {
    if (event.target.files.length > 0) {
      const filePath = event.target.files[0].webkitRelativePath;
      const folder = filePath.substring(0, filePath.indexOf('/'));
      setDownloadFolder(folder);
    }
  };

  const handleRunScript = async () => {
    try {
      const response = await fetch('http://localhost:3001/run-python', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ directoryPath, downloadFolder })
      });

      if (response.ok) {
        const data = await response.text();
        setMessage(data);
      } else {
        const errorText = await response.text();
        setMessage(`Erro ao executar o script: ${errorText}`);
      }
    } catch (error) {
      setMessage(`Erro ao executar o script: ${error.message}`);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <nav>
          <ul>
            <li><Link href="/">Dashboard</Link></li>
            <li><Link href="/a-disputar">Licitações a Disputar</Link></li>
            <li><Link href="/a-verificar">Licitações a Selecionar</Link></li>
            <li><Link href="/configuracoes">Configurações</Link></li>
          </ul>
        </nav>
      </div>
      <div className="content">
        <h1>Configurações</h1>
        <div>
          <label>
            Caminho do Diretório:
            <input 
              type="file" 
              webkitdirectory="true"
              directory="true"
              onChange={handleDirectoryChange} 
            />
          </label>
        </div>
        <div>
          <label>
            Pasta de Download:
            <input 
              type="file" 
              webkitdirectory="true"
              directory="true"
              onChange={handleDownloadFolderChange} 
            />
          </label>
        </div>
        <button onClick={handleRunScript}>Executar Script</button>
        {message && <p>{message}</p>}
      </div>
      <style jsx>{`
        .container {
          display: flex;
          flex-direction: column;
          height: 100vh;
        }
        .header {
          background: #2c3e50;
          padding: 1rem;
          color: #ecf0f1;
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
        .content {
          flex-grow: 1;
          padding: 2rem;
        }
        .content label {
          display: block;
          margin-bottom: 1rem;
        }
        .content input {
          width: 100%;
          padding: 0.5rem;
          margin-bottom: 1rem;
        }
        .content button {
          padding: 0.5rem 1rem;
          background-color: #2980b9;
          color: white;
          border: none;
          cursor: pointer;
        }
        .content button:hover {
          background-color: #3498db;
        }
        .content p {
          margin-top: 1rem;
          color: #e74c3c;
        }
      `}</style>
    </div>
  );
};

export default Configuracoes;
