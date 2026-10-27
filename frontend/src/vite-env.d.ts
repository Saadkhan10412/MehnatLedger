/// <reference types="vite/client" />

interface ImportMetaEnv {
  /**
   * Base URL for the backend API. Browser-visible and therefore public:
   * never place a secret here.
   */
  readonly VITE_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
