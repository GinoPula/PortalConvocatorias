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

export default function AdminUsuarios() {
  const [lista, setLista] = useState<UsuarioStaff[]>([]);
  const [mostrarForm, setMostrarForm] = useState(false);
  const [rolesSeleccionados, setRolesSeleccionados] = useState<string[]>([]);
  const [error, setError] = useState("");

  async function cargar() {
    setLista(await api.get("/api/admin/usuarios"));
  }

  useEffect(() => {
    cargar();
  }, []);

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
      cargar();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Error al crear usuario");
    }
  }

  async function alternarActivo(u: UsuarioStaff) {
    await api.post(`/api/admin/usuarios/${u.id}/${u.activo ? "desactivar" : "activar"}`);
    cargar();
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-900">Usuarios del sistema</h1>
        <button onClick={() => setMostrarForm(!mostrarForm)} className="bg-blue-700 text-white px-4 py-2 rounded">
          {mostrarForm ? "Cancelar" : "+ Nuevo usuario"}
        </button>
      </div>

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
            <button
              onClick={() => alternarActivo(u)}
              className={`text-xs px-3 py-1.5 rounded ${u.activo ? "bg-red-50 text-red-700" : "bg-green-50 text-green-700"}`}
            >
              {u.activo ? "Desactivar" : "Activar"}
            </button>
          </div>
        ))}
        {lista.length === 0 && <p className="text-gray-400 text-sm">No hay usuarios de staff creados todavia.</p>}
      </div>
    </div>
  );
}
