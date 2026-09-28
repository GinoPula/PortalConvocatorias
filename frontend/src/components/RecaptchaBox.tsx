import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import { RECAPTCHA_SITE_KEY } from "../api/client";

export interface RecaptchaHandle {
  reset: () => void;
}

interface Props {
  onToken: (token: string) => void;
}

// Casilla "No soy un robot" de Google reCAPTCHA v2. El script se carga en index.html;
// aqui solo se renderiza el widget cuando ese script ya esta listo (puede tardar
// unos milisegundos mas que React) y se avisa al padre con el token via onToken.
const RecaptchaBox = forwardRef<RecaptchaHandle, Props>(function RecaptchaBox({ onToken }, ref) {
  const contenedorRef = useRef<HTMLDivElement>(null);
  const widgetId = useRef<number | null>(null);

  useImperativeHandle(ref, () => ({
    reset() {
      if (widgetId.current !== null) window.grecaptcha?.reset(widgetId.current);
    },
  }));

  useEffect(() => {
    let cancelado = false;

    function intentarRenderizar() {
      if (cancelado || widgetId.current !== null || !contenedorRef.current) return;
      const g = window.grecaptcha;
      if (!g || !g.render) {
        setTimeout(intentarRenderizar, 200);
        return;
      }
      widgetId.current = g.render(contenedorRef.current, { sitekey: RECAPTCHA_SITE_KEY, callback: onToken });
    }

    intentarRenderizar();
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!RECAPTCHA_SITE_KEY) {
    return <p className="text-xs text-red-600">Falta configurar la clave de reCAPTCHA (RECAPTCHA_SITE_KEY).</p>;
  }

  return <div ref={contenedorRef} />;
});

export default RecaptchaBox;
