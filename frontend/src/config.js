// The backend always runs on port 8000. Derive the host from the page's
// own hostname (rather than hardcoding "localhost") so this also works
// when the frontend is loaded via a LAN IP from another device — on
// that device "localhost" would point to itself, not this machine.
export const API_BASE = `http://${window.location.hostname}:8000`
