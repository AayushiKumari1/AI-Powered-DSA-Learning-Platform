import { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

// Connects to the Flask-SocketIO server (same origin; proxied by Vite in dev).
export function useSocket(joinEvent, joinPayload, handlers) {
  const [connected, setConnected] = useState(false);
  const ref = useRef(handlers);
  ref.current = handlers;
  const key = JSON.stringify(joinPayload);
  useEffect(() => {
    if (!joinEvent) return;
    const s = io({ path: "/socket.io", transports: ["websocket", "polling"] });
    s.on("connect", () => { setConnected(true); s.emit(joinEvent, joinPayload); });
    s.on("disconnect", () => setConnected(false));
    Object.keys(ref.current || {}).forEach((ev) => s.on(ev, (p) => ref.current[ev]?.(p)));
    return () => s.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [joinEvent, key]);
  return connected;
}
