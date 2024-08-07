import React from "react";
import Link from "next/link";

const Sidebar = () => {
  return (
    <aside className="bg-gray-800 text-white w-64 min-h-screen p-4">
      <nav>
        <ul>
          <li className="mb-2">
            <Link href="/">
              <span className="hover:text-gray-300">Página Inicial</span>
            </Link>
          </li>
          <li className="mb-2">
            <Link href="/licitation-details">
              <span className="hover:text-gray-300">Detalhes da Licitação</span>
            </Link>
          </li>
          <li className="mb-2">
            <Link href="/config">
              <span className="hover:text-gray-300">Configurações</span>
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
