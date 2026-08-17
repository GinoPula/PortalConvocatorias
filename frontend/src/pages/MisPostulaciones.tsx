import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Postulacion } from "../api/types";

const BADGE: Record<string, string> = {
  RECIBIDA: "bg-blue-100 text-blue-800",
  EN_EVALUACION: "bg-amber-100 text-amber-800",
  APTA: "bg-green-100 text-green-800",
  NO_APTA: "bg-red-100 text-red-800",
  ENTREVISTA: "bg-purple-100 text-purple-800",
  SELECCIONADA: "bg-green-200 text-green-900",
  NO_SELECCIONADA: "bg-gray-200 text-gray-700",
  RETIRADA: "bg-gray-200 text-gray-700",
};

export default function MisPostulaciones() {
  const [postulaciones, setPostulaciones] = useState<Postulacion[]>([]);

  useEffect(() => {
    api.get<Postulacion[]>("/api/postulante/postulaciones").then(setPostulaciones);
  }, []);

  async function retirar(id: number) {
    if (!confirm("¿Retirar esta postulacion?")) return;
    await api.post(`/api/postulante/postulaciones/${id}/retirar`);
    api.get<Postulacion[]>("/api/postulante/postulaciones").then(setPostulaciones);
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-blue-900 mb-6">Mis postulaciones</h1>
      {postulaciones.length === 0 ? (
        <p className="text-gray-500">Aun no tienes postulaciones registradas.</p>
      ) : (
        <div className="grid gap-3">
          {postulaciones.map((p) => (
            <div key={p.id} className="border border-gray-200 rounded-lg p-4 bg-white flex items-center justify-between">
              <div>
                <div className="font-medium">Constancia: {p.codigo_constancia}</div>
                <div className="text-sm text-gray-500">Registrada el {new Date(p.creado_en).toLocaleString()}</div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-xs font-bold px-3 py-1 rounded-full ${BADGE[p.estado] || "bg-gray-100"}`}>{p.estado}</span>
                {p.estado === "RECIBIDA" && (
                  <button onClick={() => retirar(p.id)} className="text-red-600 text-sm hover:underline">
                    Retirar
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
