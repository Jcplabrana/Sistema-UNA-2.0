import Link from 'next/link';

const Navigation = () => {
  return (
    <nav>
      <ul>
        <li>
          <Link href="/" legacyBehavior>
            <a onMouseEnter={() => {}}>Dashboard</a>
          </Link>
        </li>
        <li>
          <Link href="/a-disputar" legacyBehavior>
            <a onMouseEnter={() => {}}>Licitações a Disputar</a>
          </Link>
        </li>
        <li>
          <Link href="/a-verificar" legacyBehavior>
            <a onMouseEnter={() => {}}>Licitações a Selecionar</a>
          </Link>
        </li>
        <li>
          <Link href="/configuracoes" legacyBehavior>
            <a onMouseEnter={() => {}}>Configurações</a>
          </Link>
        </li>
      </ul>
      <style jsx>{`
        nav ul {
          list-style: none;
          padding: 0;
        }
        nav ul li {
          margin-bottom: 1rem;
        }
        nav ul li a {
          color: #ecf0f1;
          text-decoration: none;
          font-weight: bold;
        }
      `}</style>
    </nav>
  );
};

export default Navigation;
