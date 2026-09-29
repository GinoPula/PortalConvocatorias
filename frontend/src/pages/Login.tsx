import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import { obtenerTokenRecaptcha } from "../api/recaptcha";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setCargando(true);
    try {
      const recaptchaToken = await obtenerTokenRecaptcha("login");
      await login(email, password, recaptchaToken);
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : err instanceof Error ? err.message : "Error de conexion");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="max-w-sm mx-auto bg-white border border-gray-200 rounded-lg p-8">
      <h1 className="text-xl font-bold text-blue-900 mb-6">Iniciar sesion</h1>
      {error && <div className="text-red-600 text-sm mb-4">{error}</div>}
      <form onSubmit={onSubmit} className="flex flex-col gap-3">
        <input
          type="email"
          placeholder="Correo electronico"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
          required
        />
        <input
          type="password"
          placeholder="Contrasena"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
          required
        />
        <button disabled={cargando} type="submit" className="bg-blue-700 text-white rounded py-2 font-medium mt-2 disabled:opacity-50">
          {cargando ? "Verificando..." : "Ingresar"}
        </button>
        <p className="text-xs text-gray-400 text-center">
          Este sitio esta protegido por reCAPTCHA y aplican la{" "}
          <a href="https://policies.google.com/privacy" target="_blank" rel="noreferrer" className="underline">
            Politica de Privacidad
          </a>{" "}
          y los{" "}
          <a href="https://policies.google.com/terms" target="_blank" rel="noreferrer" className="underline">
            Terminos de Servicio
          </a>{" "}
          de Google.
        </p>
      </form>
    </div>
  );
}
