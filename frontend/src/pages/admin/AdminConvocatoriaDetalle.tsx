import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../../api/client";
import type { Convocatoria } from "../../api/types";

export default function AdminConvocatoriaDetalle() {
  const { id } = useParams();
  const [conv, setConv] = useState<Convocatoria | null>(null);

  async function cargar() {
    setConv(await api.get<Convocatoria>(`/api/admin/convocatorias/${id}`));
  }

  useEffect(() => {
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function agregarPlaza(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    await api.post(`/api/admin/convocatorias/${id}/plazas`, {
      codigo: form.get("codigo"),
      cargo: form.get("cargo"),
      numero_plazas: Number(form.get("numero_plazas")),
      lugar: form.get("lugar"),
      tipo_contrato: form.get("tipo_contrato"),
      jornada: "",
      requisitos: [],
    });
    location.reload();
  }

  async function agregarCriterio(positionId: number, e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    await api.post(`/api/admin/plazas/${positionId}/criterios`, {
      nombre: form.get("nombre"),
      puntaje_maximo: Number(form.get("puntaje_maximo")),
    });
    e.currentTarget.reset();
    alert("Criterio agregado");
  }

  if (!conv) return <p className="text-gray-500">Cargando...</p>;

  return (
    <div>
      <Link to="/admin/convocatorias" className="text-blue-700 text-sm hover:underline">
        &larr; Convocatorias
      </Link>
      <h1 className="text-2xl font-bold text-blue-900 mt-2 mb-1">{conv.nombre}</h1>
      <p className="text-sm text-gray-500 mb-6">
        {conv.codigo} &middot; Estado: <strong>{conv.estado}</strong>
      </p>

      <div className="grid gap-4 mb-6">
        {conv.plazas.map((plaza) => (
          <div key={plaza.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="font-semibold">{plaza.cargo} ({plaza.codigo})</div>
            <div className="text-sm text-gray-500 mb-3">
              {plaza.lugar} &middot; {plaza.numero_plazas} plaza(s)
            </div>
            <div className="text-sm mb-3">
              Requisitos: {plaza.requisitos.map((r) => `${r.tipo}=${r.valor}`).join(", ") || "sin requisitos"}
            </div>
            <form onSubmit={(e) => agregarCriterio(plaza.id, e)} className="flex gap-2 items-center text-sm">
              <input name="nombre" placeholder="Criterio de puntaje (ej. Entrevista)" className="border border-gray-300 rounded px-2 py-1" required />
              <input name="puntaje_maximo" type="number" placeholder="Puntaje maximo" className="border border-gray-300 rounded px-2 py-1 w-32" required />
              <button className="bg-blue-100 text-blue-800 rounded px-3 py-1">Agregar criterio</button>
            </form>
          </div>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="font-semibold text-blue-900 mb-3">Agregar plaza</h2>
        <form onSubmit={agregarPlaza} className="grid grid-cols-2 gap-3">
          <input name="codigo" placeholder="Codigo de plaza" className="border border-gray-300 rounded px-3 py-2" required />
          <input name="cargo" placeholder="Cargo" className="border border-gray-300 rounded px-3 py-2" required />
          <input name="numero_plazas" type="number" defaultValue={1} placeholder="N. de plazas" className="border border-gray-300 rounded px-3 py-2" />
          <input name="lugar" placeholder="Lugar" className="border border-gray-300 rounded px-3 py-2" />
          <input name="tipo_contrato" placeholder="Tipo de contrato" className="border border-gray-300 rounded px-3 py-2 col-span-2" />
          <button className="bg-blue-700 text-white rounded py-2 col-span-2">Agregar plaza</button>
        </form>
        <p className="text-xs text-gray-400 mt-2">
          Nota: la carga de requisitos por plaza vía la API ya esta disponible (POST /plazas con
          requisitos[]); el formulario detallado de requisitos por plaza queda para una iteracion
          siguiente de esta pantalla.
        </p>
      </div>
    </div>
  );
}
