import React from 'react';
import LicitacoesPage from '../components/LicitacoesPage';

const AVerificar = ({ sheetName }) => <LicitacoesPage sheetName={sheetName} />;

export const getServerSideProps = async () => {
  return {
    props: {
      sheetName: 'Licitações a Verificar - Versão 2.0 Sistema',
    },
  };
};

export default AVerificar;
