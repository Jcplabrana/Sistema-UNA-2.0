import Head from 'next/head';
import Layout from '../components/Layout';
import Licitacoes from '../components/Licitacoes';

export default function Home() {
  return (
    <Layout>
      <Head>
        <title>Sistema UNA de Licitações</title>
      </Head>
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold my-4">Próximas Licitações</h1>
        <Licitacoes sheetName="Próximas Licitações" />
      </div>
    </Layout>
  );
}
