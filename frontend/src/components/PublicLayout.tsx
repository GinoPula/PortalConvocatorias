import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function PublicLayout() {
  const { usuario, logout } = useAuth();
  const esPostulante = usuario?.roles.includes("POSTULANTE");
  const esStaff = usuario?.roles.some((r) => r !== "POSTULANTE");

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center gap-6">
          <Link to="/" className="flex items-center shrink-0">
            <img src="/logo-mvcs.png" alt="Ministerio de Vivienda, Construccion y Saneamiento" className="h-9" />
          </Link>
          <nav className="flex-1 flex gap-5 text-sm text-gray-600">
            <Link to="/">Convocatorias</Link>
            {esPostulante && (
              <>
                <Link to="/perfil">Mi perfil</Link>
                <Link to="/mis-postulaciones">Mis postulaciones</Link>
              </>
            )}
            {esStaff && <Link to="/admin">Panel administrativo</Link>}
          </nav>
          {usuario ? (
            <div className="flex items-center gap-3 text-sm">
              <span className="text-gray-500">{usuario.email}</span>
              <button onClick={() => logout()} className="text-blue-700 hover:underline">
                Cerrar sesion
              </button>
            </div>
          ) : (
            <div className="flex gap-3 text-sm">
              <Link to="/login" className="text-blue-700 hover:underline">
                Iniciar sesion
              </Link>
              <Link to="/registro" className="bg-blue-700 text-white px-3 py-1.5 rounded">
                Registrarme
              </Link>
            </div>
          )}
        </div>
      </header>
      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8">
        <Outlet />
      </main>
      <footer className="bg-[#0C447C] text-blue-100 text-sm py-6 text-center border-t-4" style={{ borderImage: "linear-gradient(90deg,#D91023,#F5B041,#27AE60,#185FA5) 1" }}>
        Ministerio de Vivienda, Construccion y Saneamiento
      </footer>
    </div>
  );
}
