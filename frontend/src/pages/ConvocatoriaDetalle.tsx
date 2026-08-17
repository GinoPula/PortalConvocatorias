import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api, ApiError } from "../api/client";
import type { Convocatoria, ValidacionPrevia } from "../api/types";
import { useAuth } from "../context/AuthContext";

export default function ConvocatoriaDetalle() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [conv, setConv] = useState<Convocatoria | null>(null);
  const [validaciones, setValidaciones] = useState<Record<number, ValidacionPrevia>>({});
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    api.get<Convocatoria>(`/api/convocatorias/${id}`).then(setConv);
  }, [id]);

  const esPostulante = usuario?.roles.includes("POSTULANTE");

  async function validar(positionId: number) {
    const v = await api.get<ValidacionPrevia>(`/api/postulante/postulaciones/validar/${positionId}`);
    setValidaciones((prev) => ({ ...prev, [positionId]: v }));
  }

  async function postular(positionId: number) {
    setMensaje("");
    const acepta = confirm(
      "Declaro bajo juramento que la informacion proporcionada es verdadera y que los documentos adjuntos corresponden a mi informacion personal. ¿Confirmar postulacion?"
    );
    if (!acepta) return;
    try {
      const p = await api.post<{ codigo_constancia: string }>("/api/postulante/postulaciones", {
        position_id: positionId,
        declaracion_jurada_aceptada: true,
      });
      setMensaje(`Postulacion registrada. Codigo de constancia: ${p.codigo_constancia}`);
      setTimeout(() => navigate("/mis-postulaciones"), 1500);
    } catch (err) {
      setMensaje(err instanceof ApiError ? String(err.detail) : "Error al postular");
    }
  }

  if (!conv) return <p className="text-gray-500">Cargando...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-blue-900">{conv.nombre}</h1>
      <p className="text-sm text-gray-500 mb-4">
        {conv.codigo} &middot; {conv.regimen === "LOCADOR" ? "Locador" : conv.regimen === "OTROS" ? "Otros" : "CAS"} &middot;{" "}
        {conv.dependencia}
        {conv.es_en_sede && conv.sede ? ` · ${conv.sede}` : " · Remoto"}
      </p>

      {conv.descripcion && (
        <div className="mb-4">
          <h2 className="text-sm font-semibold text-blue-900 mb-1">Acerca del puesto</h2>
          <p className="text-gray-700 whitespace-pre-line">{conv.descripcion}</p>
        </div>
      )}
      {conv.requisitos_texto && (
        <div className="mb-4">
          <h2 className="text-sm font-semibold text-blue-900 mb-1">Requisitos</h2>
          <p className="text-gray-700 whitespace-pre-line">{conv.requisitos_texto}</p>
        </div>
      )}
      {conv.deseable_texto && (
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-blue-900 mb-1">Deseable (Habilidades Tecnicas)</h2>
          <p className="text-gray-700 whitespace-pre-line">{conv.deseable_texto}</p>
        </div>
      )}

      <h2 className="text-lg font-semibold text-blue-900 mb-3">Plazas</h2>
      <div className="grid gap-4">
        {conv.plazas.map((plaza) => {
          const v = validaciones[plaza.id];
          return (
            <div key={plaza.id} className="border border-gray-200 rounded-lg p-4 bg-white">
              <div className="font-semibold">{plaza.cargo}</div>
              <div className="text-sm text-gray-500 mb-3">
                {plaza.codigo} &middot; {plaza.lugar} &middot; {plaza.numero_plazas} plaza(s)
                {plaza.remuneracion ? ` · S/ ${plaza.remuneracion}` : ""}
              </div>

              <div className="text-sm mb-3">
                <strong>Requisitos:</strong>
                <ul className="list-disc list-inside text-gray-600">
                  {plaza.requisitos.map((r) => (
                    <li key={r.id}>
                      {r.tipo}: {r.valor} {r.obligatorio ? "" : "(opcional)"}
                    </li>
                  ))}
                </ul>
              </div>

              {esPostulante ? (
                <div className="flex flex-col gap-2">
                  {!v && (
                    <button onClick={() => validar(plaza.id)} className="bg-gray-100 text-gray-800 px-4 py-2 rounded self-start">
                      Verificar si cumplo los requisitos
                    </button>
                  )}
                  {v && (
                    <div className="text-sm border border-gray-200 rounded p-3">
                      {v.requisitos.map((r) => (
                        <div key={r.requirement_id} className={r.cumple ? "text-green-700" : "text-red-700"}>
                          {r.cumple ? "✓" : "✗"} {r.tipo}: {r.valor_requerido} &mdash; {r.motivo}
                        </div>
                      ))}
                      {!v.puede_postular && <div className="text-red-700 font-medium mt-2">{v.motivo_bloqueo}</div>}
                      {v.puede_postular && (
                        <button onClick={() => postular(plaza.id)} className="bg-blue-700 text-white px-4 py-2 rounded mt-3">
                          Postular a esta plaza
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <Link to="/login" className="text-blue-700 text-sm hover:underline">
                  Inicia sesion como postulante para postular
                </Link>
              )}
            </div>
          );
        })}
      </div>
      {mensaje && <p className="mt-4 text-blue-800 font-medium">{mensaje}</p>}
    </div>
  );
}
