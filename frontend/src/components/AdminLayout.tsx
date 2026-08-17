import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AdminLayout() {
  const { usuario, logout } = useAuth();
  return (
    <div className="min-h-screen flex">
      <aside className="w-56 bg-[#0C447C] text-blue-100 flex flex-col">
        <div className="p-4 border-b border-blue-900 bg-white">
          <img src="/logo-mvcs.png" alt="MVCS" className="h-7" />
        </div>
        <nav className="flex-1 flex flex-col p-3 gap-1 text-sm">
          <Link to="/admin" className="px-3 py-2 rounded hover:bg-blue-900">
            Dashboard
          </Link>
          <Link to="/admin/convocatorias" className="px-3 py-2 rounded hover:bg-blue-900">
            Convocatorias
          </Link>
          <Link to="/admin/postulaciones" className="px-3 py-2 rounded hover:bg-blue-900">
            Postulaciones
          </Link>
          <Link to="/" className="px-3 py-2 rounded hover:bg-blue-900 mt-4 text-blue-300">
            &larr; Volver al portal publico
          </Link>
        </nav>
        <div className="p-3 border-t border-blue-900 text-xs">
          <div className="mb-2">{usuario?.email}</div>
          <div className="mb-2 text-blue-400">{usuario?.roles.join(", ")}</div>
          <button onClick={() => logout()} className="text-blue-300 hover:underline">
            Cerrar sesion
          </button>
        </div>
      </aside>
      <main className="flex-1 p-8 bg-gray-50">
        <Outlet />
      </main>
    </div>
  );
}
