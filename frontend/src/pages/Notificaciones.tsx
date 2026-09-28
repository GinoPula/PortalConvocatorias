import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { NotificationItem } from "../api/types";

export default function Notificaciones() {
  const [lista, setLista] = useState<NotificationItem[] | null>(null);

  useEffect(() => {
    api.get<NotificationItem[]>("/api/postulante/notificaciones").then(setLista);
  }, []);

  if (!lista) return <p className="text-gray-500">Cargando...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-blue-900 mb-6">Notificaciones</h1>
      {lista.length === 0 && <p className="text-gray-400 text-sm">No tienes notificaciones todavia.</p>}
      <div className="grid gap-3">
        {lista.map((n) => (
          <div key={n.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start gap-4">
              <div className="font-semibold text-blue-900">{n.asunto}</div>
              <div className="text-xs text-gray-400 whitespace-nowrap">{new Date(n.creado_en).toLocaleString()}</div>
            </div>
            <p className="text-sm text-gray-700 mt-1">{n.mensaje}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
