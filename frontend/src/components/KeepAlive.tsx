"use client";
import { useEffect } from "react";

/**
 * Pings the backend /health every 10 minutes to prevent Render free-tier sleep.
 * Also pings immediately on mount to wake the server if it's asleep.
 */
export default function KeepAlive() {
  useEffect(() => {
    const ping = () => fetch("/api/../health").catch(() => {});
    ping(); // immediate wake-up ping
    const id = setInterval(ping, 10 * 60 * 1000); // every 10 min
    return () => clearInterval(id);
  }, []);
  return null;
}
