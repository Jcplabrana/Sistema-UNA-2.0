import React from 'react';
import LicitacoesPage from '../components/LicitacoesPage';

const ADisputar = ({ sheetName }) => <LicitacoesPage sheetName={sheetName} />;

export const getServerSideProps = async () => {
  return {
    props: {
      sheetName: 'A Disputar',
    },
  };
};

export default ADisputar;
