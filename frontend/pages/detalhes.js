import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';

const Detalhes = () => {
  const router = useRouter();
  const { data } = router.query;
  const [licitacao, setLicitacao] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:3001/data/A Disputar');
        const { data } = response.data;
        const found = data.find(row => row[0] === data);
        setLicitacao(found);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    if (data) {
      fetchData();
    }
  }, [data]);

  if (!licitacao) {
    return <p>Carregando...</p>;
  }

  return (
    <div className="container">
      <h1>Detalhes da Licitação</h1>
      <p>Data Abertura: {licitacao[0]}</p>
      <p>Orgão Licitante: {licitacao[1]}</p>
      <p>Objeto: {licitacao[2]}</p>
      <p>Valor do Contrato: {licitacao[3]}</p>
      <p>Cidade: {licitacao[4]}</p>
      <p>Link para Download: <a href={licitacao[5]} target="_blank">Download</a></p>
      <p>Link Edital PDF: <a href={licitacao[6]} target="_blank">Edital PDF</a></p>
      <style jsx>{`
        .container {
          padding: 2rem;
        }
      `}</style>
    </div>
  );
};

export default Detalhes;
