// Thin fetch wrapper around the Flask backend. Same-origin, cookie session.
export class ApiError extends Error {
  constructor(message, status, data) { super(message); this.status = status; this.data = data; }
}

async function request(method, url, body) {
  const res = await fetch(url, {
    method,
    credentials: "same-origin",
    headers: { Accept: "application/json", "X-Requested-With": "fetch", ...(body !== undefined ? { "Content-Type": "application/json" } : {}) },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  let data = null;
  try { data = await res.json(); } catch { /* empty or non-JSON body */ }
  if (!res.ok) {
    if (res.status === 401 && !url.startsWith("/api/auth")) window.dispatchEvent(new Event("em:unauthorized"));
    throw new ApiError((data && (data.error || data.message)) || `Request failed (${res.status})`, res.status, data);
  }
  return data;
}

export const api = {
  get: (url) => request("GET", url),
  post: (url, body = {}) => request("POST", url, body),
  put: (url, body = {}) => request("PUT", url, body),
  del: (url) => request("DELETE", url),
};
