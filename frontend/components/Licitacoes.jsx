export default function Licitacoes({ licitacoes }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {licitacoes.map((licitacao, index) => (
        <div key={index} className="p-4 bg-gray-100 rounded-lg shadow-md">
          <p>{licitacao[0]}</p>
          <p>{licitacao[1]}</p>
          <p>{licitacao[2]}</p>
        </div>
      ))}
    </div>
  );
}
