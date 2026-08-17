import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Registro() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({
    tipo_documento: "DNI",
    numero_documento: "",
    nombres: "",
    apellidos: "",
    email: "",
    telefono: "",
    password: "",
    confirmar_password: "",
    acepta_terminos: false,
  });
  const [error, setError] = useState("");

  function campo<K extends keyof typeof form>(clave: K, valor: (typeof form)[K]) {
    setForm((f) => ({ ...f, [clave]: valor }));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/api/auth/register", form);
      await login(form.email, form.password);
      navigate("/perfil");
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Error de conexion");
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white border border-gray-200 rounded-lg p-8">
      <h1 className="text-xl font-bold text-blue-900 mb-6">Crear cuenta de postulante</h1>
      {error && <div className="text-red-600 text-sm mb-4">{error}</div>}
      <form onSubmit={onSubmit} className="flex flex-col gap-3">
        <div className="flex gap-2">
          <select
            value={form.tipo_documento}
            onChange={(e) => campo("tipo_documento", e.target.value)}
            className="border border-gray-300 rounded px-3 py-2"
          >
            <option value="DNI">DNI</option>
            <option value="CE">Carne de Extranjeria</option>
          </select>
          <input
            placeholder="Numero de documento"
            value={form.numero_documento}
            onChange={(e) => campo("numero_documento", e.target.value)}
            className="border border-gray-300 rounded px-3 py-2 flex-1"
            required
          />
        </div>
        <input
          placeholder="Nombres"
          value={form.nombres}
          onChange={(e) => campo("nombres", e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
          required
        />
        <input
          placeholder="Apellidos"
          value={form.apellidos}
          onChange={(e) => campo("apellidos", e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
          required
        />
        <input
          type="email"
          placeholder="Correo electronico"
          value={form.email}
          onChange={(e) => campo("email", e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
          required
        />
        <input
          placeholder="Telefono"
          value={form.telefono}
          onChange={(e) => campo("telefono", e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
        />
        <input
          type="password"
          placeholder="Contrasena (min. 8 caracteres, letras y numeros)"
          value={form.password}
          onChange={(e) => campo("password", e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
          required
        />
        <input
          type="password"
          placeholder="Confirmar contrasena"
          value={form.confirmar_password}
          onChange={(e) => campo("confirmar_password", e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
          required
        />
        <label className="flex items-start gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            checked={form.acepta_terminos}
            onChange={(e) => campo("acepta_terminos", e.target.checked)}
            className="mt-1"
          />
          Acepto los terminos y condiciones y la declaracion de privacidad
        </label>
        <button type="submit" className="bg-blue-700 text-white rounded py-2 font-medium mt-2">
          Crear cuenta
        </button>
      </form>
    </div>
  );
}
