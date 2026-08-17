import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { ConvocatoriaListItem } from "../api/types";

const BADGE: Record<string, string> = {
  PUBLICADA: "bg-blue-100 text-blue-800",
  ABIERTA: "bg-green-100 text-green-800",
  CERRADA: "bg-gray-200 text-gray-700",
  EN_EVALUACION: "bg-amber-100 text-amber-800",
  FINALIZADA: "bg-gray-200 text-gray-700",
};

export default function Convocatorias() {
  const [convocatorias, setConvocatorias] = useState<ConvocatoriaListItem[]>([]);
  const [q, setQ] = useState("");
  const [cargando, setCargando] = useState(true);

  async function cargar() {
    setCargando(true);
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    const data = await api.get<ConvocatoriaListItem[]>("/api/convocatorias?" + params.toString());
    setConvocatorias(data);
    setCargando(false);
  }

  useEffect(() => {
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <div
        className="relative rounded-lg overflow-hidden mb-8 -mx-6 sm:mx-0"
        style={{
          backgroundImage: "linear-gradient(rgba(12,68,124,0.75), rgba(12,68,124,0.85)), url('/portada.webp')",
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        <div className="px-8 py-12">
          <h1 className="text-3xl font-bold text-white mb-2">Convocatorias laborales</h1>
          <p className="text-blue-100 max-w-xl">
            Portal de convocatorias del Ministerio de Vivienda, Construccion y Saneamiento.
          </p>
        </div>
      </div>

      <div className="flex gap-2 mb-6">
        <input
          placeholder="Buscar por nombre o codigo..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyUp={(e) => e.key === "Enter" && cargar()}
          className="border border-gray-300 rounded px-3 py-2 flex-1"
        />
        <button onClick={cargar} className="bg-blue-700 text-white px-4 rounded">
          Buscar
        </button>
      </div>

      {cargando ? (
        <p className="text-gray-500">Cargando...</p>
      ) : convocatorias.length === 0 ? (
        <p className="text-gray-500">No hay convocatorias publicadas por el momento.</p>
      ) : (
        <div className="grid gap-3">
          {convocatorias.map((c) => (
            <Link
              key={c.id}
              to={`/convocatorias/${c.id}`}
              className="border border-gray-200 rounded-lg p-4 bg-white hover:border-blue-400 flex items-center justify-between"
            >
              <div>
                <div className="font-semibold text-blue-900">{c.nombre}</div>
                <div className="text-sm text-gray-500">
                  {c.codigo} &middot; {c.regimen} &middot; {c.sede}
                </div>
              </div>
              <span className={`text-xs font-bold px-3 py-1 rounded-full ${BADGE[c.estado] || "bg-gray-100"}`}>
                {c.estado}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
