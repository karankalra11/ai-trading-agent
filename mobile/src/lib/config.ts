/**
 * Point this at your Render backend URL once deployed.
 * For local dev: http://localhost:8000
 * For Render: https://trading-signal-agent-api.onrender.com
 */
export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";
