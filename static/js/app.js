/**
 * Inicialización Alpine.js + helpers globales para la app educativa.
 */

// Store global de Alpine para el theme
document.addEventListener('alpine:init', () => {
  Alpine.store('theme', {
    init() {
      // Detectar preferencia: localStorage > system preference > light
      const saved = localStorage.getItem('theme');
      if (saved) {
        this.current = saved;
      } else {
        this.current = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      this.apply();

      // Escuchar cambios del sistema
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
          this.current = e.matches ? 'dark' : 'light';
          this.apply();
        }
      });
    },
    current: 'light',
    toggle() {
      this.current = this.current === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', this.current);
      this.apply();
    },
    apply() {
      if (this.current === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },
  });
});

// Helper: View Transitions API para cambio entre módulos (con fallback)
document.addEventListener('htmx:beforeSwap', (e) => {
  if (document.startViewTransition && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    e.preventDefault();
    document.startViewTransition(() => {
      e.detail.target.innerHTML = e.detail.serverResponse;
    });
  }
});
