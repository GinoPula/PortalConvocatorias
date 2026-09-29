import { useEffect, useState } from "react";
import { api, ApiError } from "../../api/client";
import type { UsuarioStaff } from "../../api/types";

const ROLES_DISPONIBLES = [
  { valor: "RRHH", etiqueta: "RR.HH. (crea convocatorias y evalua)" },
  { valor: "EVALUADOR", etiqueta: "Evaluador (revisa y puntua postulaciones)" },
  { valor: "SUPERVISOR", etiqueta: "Supervisor (aprueba evaluaciones)" },
  { valor: "AUDITOR", etiqueta: "Auditor (solo lectura)" },
  { valor: "ADMINISTRADOR", etiqueta: "Administrador (acceso total)" },
];

const PAGINA = 20;

export default function AdminUsuarios() {
  const [lista, setLista] = useState<UsuarioStaff[]>([]);
  const [busqueda, setBusqueda] = useState("");
  const [offset, setOffset] = useState(0);
  const [hayMas, setHayMas] = useState(false);
  const [mostrarForm, setMostrarForm] = useState(false);
  const [rolesSeleccionados, setRolesSeleccionados] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  async function cargar(desdeCero: boolean) {
    const nuevoOffset = desdeCero ? 0 : offset;
    const query = new URLSearchParams({ limit: String(PAGINA), offset: String(nuevoOffset) });
    if (busqueda) query.set("q", busqueda);
    const pagina = await api.get<UsuarioStaff[]>(`/api/admin/usuarios?${query}`);
    setLista((prev) => (desdeCero ? pagina : [...prev, ...pagina]));
    setOffset(nuevoOffset + pagina.length);
    setHayMas(pagina.length === PAGINA);
  }

  useEffect(() => {
    cargar(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busqueda]);

  function alternarRol(rol: string) {
    setRolesSeleccionados((prev) => (prev.includes(rol) ? prev.filter((r) => r !== rol) : [...prev, rol]));
  }

  async function crear(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      await api.post("/api/admin/usuarios", {
        email: form.get("email"),
        password: form.get("password"),
        roles: rolesSeleccionados,
      });
      setMostrarForm(false);
      setRolesSeleccionados([]);
      cargar(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al crear usuario");
    }
  }

  async function alternarActivo(u: UsuarioStaff) {
    await api.post(`/api/admin/usuarios/${u.id}/${u.activo ? "desactivar" : "activar"}`);
    cargar(true);
  }

  async function resetearPassword(u: UsuarioStaff) {
    if (!confirm(`Generar una contrasena temporal nueva para ${u.email}? La contrasena actual dejara de funcionar.`)) return;
    setMensaje("");
    try {
      const r = await api.post<{ password_temporal: string }>(`/api/admin/usuarios/${u.id}/resetear-password`);
      setMensaje(`Contrasena temporal para ${u.email}: ${r.password_temporal} (compartela por un canal seguro; no se volvera a mostrar)`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al resetear la contrasena");
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-900">Usuarios del sistema</h1>
        <button onClick={() => setMostrarForm(!mostrarForm)} className="bg-blue-700 text-white px-4 py-2 rounded">
          {mostrarForm ? "Cancelar" : "+ Nuevo usuario"}
        </button>
      </div>

      {mensaje && (
        <div className="bg-amber-50 border border-amber-300 text-amber-900 rounded p-3 text-sm mb-4 flex justify-between items-start gap-4">
          <span>{mensaje}</span>
          <button onClick={() => setMensaje("")} className="text-amber-700 hover:underline shrink-0">
            Cerrar
          </button>
        </div>
      )}

      {mostrarForm && (
        <form onSubmit={crear} className="bg-white border border-gray-200 rounded-lg p-5 mb-6 grid gap-3">
          {error && <div className="text-red-600 text-sm">{error}</div>}

          <input name="email" type="email" placeholder="Correo institucional" className="border border-gray-300 rounded px-3 py-2" required />
          <input
            name="password"
            type="password"
            placeholder="Contrasena temporal (min. 8 caracteres, letras y numeros)"
            className="border border-gray-300 rounded px-3 py-2"
            required
          />

          <div>
            <div className="text-sm font-medium mb-2">Roles</div>
            <div className="grid gap-1">
              {ROLES_DISPONIBLES.map((r) => (
                <label key={r.valor} className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={rolesSeleccionados.includes(r.valor)} onChange={() => alternarRol(r.valor)} />
                  {r.etiqueta}
                </label>
              ))}
            </div>
          </div>

          <button className="bg-blue-700 text-white rounded py-2">Crear usuario</button>
        </form>
      )}

      <input
        value={busqueda}
        onChange={(e) => setBusqueda(e.target.value)}
        placeholder="Buscar por correo..."
        className="border border-gray-300 rounded px-3 py-2 mb-4 w-full max-w-sm"
      />

      <div className="grid gap-3">
        {lista.map((u) => (
          <div key={u.id} className="bg-white border border-gray-200 rounded-lg p-4 flex items-center justify-between">
            <div>
              <div className="font-semibold">{u.email}</div>
              <div className="text-sm text-gray-500">
                {u.roles.join(", ")} &middot;{" "}
                <span className={u.activo ? "text-green-700" : "text-red-700"}>{u.activo ? "Activo" : "Desactivado"}</span>
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => resetearPassword(u)} className="text-xs px-3 py-1.5 rounded bg-blue-50 text-blue-700">
                Restablecer contrasena
              </button>
              <button
                onClick={() => alternarActivo(u)}
                className={`text-xs px-3 py-1.5 rounded ${u.activo ? "bg-red-50 text-red-700" : "bg-green-50 text-green-700"}`}
              >
                {u.activo ? "Desactivar" : "Activar"}
              </button>
            </div>
          </div>
        ))}
        {lista.length === 0 && <p className="text-gray-400 text-sm">No hay usuarios de staff creados todavia.</p>}
      </div>

      {hayMas && (
        <button onClick={() => cargar(false)} className="mt-4 text-sm bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded">
          Cargar mas
        </button>
      )}
    </div>
  );
}
