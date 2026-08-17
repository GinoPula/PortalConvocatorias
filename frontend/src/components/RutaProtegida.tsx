import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RutaProtegida({ rolesPermitidos, children }: { rolesPermitidos: string[]; children: ReactNode }) {
  const { usuario, cargando } = useAuth();
  if (cargando) return <p className="text-gray-500">Cargando...</p>;
  if (!usuario) return <Navigate to="/login" replace />;
  if (!usuario.roles.some((r) => rolesPermitidos.includes(r))) {
    return <p className="text-red-600">No tienes permiso para ver esta pagina.</p>;
  }
  return <>{children}</>;
}
