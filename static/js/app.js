/**
 * Inicialización Alpine.js + helpers globales para la app educativa.
 */

// Store global de Alpine para el theme + modal de imagen
document.addEventListener('alpine:init', () => {
  // Modal global para expandir imágenes a pantalla completa
  Alpine.store('imageModal', {
    open: false,
    src: '',
    alt: '',
    show(src, alt) {
      this.src = src;
      this.alt = alt || '';
      this.open = true;
      document.body.style.overflow = 'hidden';
    },
    close() {
      this.open = false;
      document.body.style.overflow = '';
    },
  });

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

// Modal de imagen GARANTIZADO — crea overlay DOM puro, no depende de Alpine.
// Funciona incluso con HTMX swaps porque es JS vanilla.
window.openImageModal = function(src, alt) {
  console.log('[openImageModal] abriendo:', src ? src.substring(0,50) : 'sin src');

  // Eliminar overlay previo si existe
  const existing = document.getElementById('__img_modal_overlay');
  if (existing) existing.remove();

  // Crear overlay
  const overlay = document.createElement('div');
  overlay.id = '__img_modal_overlay';
  overlay.style.cssText = [
    'position:fixed',
    'inset:0',
    'z-index:999999',
    'background:rgba(0,0,0,0.93)',
    'display:flex',
    'align-items:center',
    'justify-content:center',
    'padding:2rem',
    'cursor:zoom-out',
    'animation:fadeInModal 0.2s ease-out'
  ].join(';');

  // Imagen ampliada — fondo BLANCO para que las gráficas matplotlib con fondo
  // transparente se vean correctamente sobre el overlay oscuro.
  const img = document.createElement('img');
  img.src = src;
  img.alt = alt || '';
  img.style.cssText = 'max-width:95vw; max-height:90vh; object-fit:contain; border-radius:10px; box-shadow:0 30px 80px rgba(0,0,0,0.6); cursor:zoom-out; background-color:#ffffff; padding:16px;';

  // Botón cerrar
  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'Cerrar');
  closeBtn.style.cssText = 'position:absolute; top:20px; right:20px; width:44px; height:44px; border-radius:8px; background:rgba(255,255,255,0.95); border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(0,0,0,0.3);';
  closeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#111" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';

  // Hint inferior
  const hint = document.createElement('div');
  hint.style.cssText = 'position:absolute; bottom:24px; left:50%; transform:translateX(-50%); color:rgba(255,255,255,0.85); font-size:12px; padding:6px 14px; background:rgba(0,0,0,0.5); border-radius:999px; border:1px solid rgba(255,255,255,0.15);';
  hint.textContent = 'Click fuera o ESC para cerrar';

  overlay.appendChild(img);
  overlay.appendChild(closeBtn);
  overlay.appendChild(hint);

  // Inyectar keyframes de animación una vez
  if (!document.getElementById('__img_modal_kf')) {
    const style = document.createElement('style');
    style.id = '__img_modal_kf';
    style.textContent = '@keyframes fadeInModal{from{opacity:0}to{opacity:1}}';
    document.head.appendChild(style);
  }

  // Cerrar al click overlay / botón
  const cerrar = () => {
    overlay.remove();
    document.removeEventListener('keydown', escHandler);
    document.body.style.overflow = '';
  };
  overlay.addEventListener('click', cerrar);
  closeBtn.addEventListener('click', (e) => { e.stopPropagation(); cerrar(); });
  img.addEventListener('click', (e) => e.stopPropagation()); // no cerrar al click en la imagen
  const escHandler = (e) => { if (e.key === 'Escape') cerrar(); };
  document.addEventListener('keydown', escHandler);

  // Bloquear scroll del body
  document.body.style.overflow = 'hidden';

  // Insertar
  document.body.appendChild(overlay);
};

// NOTA: View Transitions API removida intencionalmente.
// Interfería con el procesamiento de OOB swaps de HTMX (hx-swap-oob),
// rompiendo la sincronización del hero/parámetros con el formulario.
// Los swaps de HTMX usan la animación CSS animate-fade-in del propio contenido.

// GUARDIA GLOBAL: prevenir submit nativo en CUALQUIER formulario HTMX.
// Si HTMX no llega a interceptar (porque aún no cargó, o por race conditions),
// el browser haría una navegación nativa al endpoint del form (hx-post),
// mostrando la respuesta cruda como página → "envía a otra vista" bug.
// Esto bloquea ese comportamiento incondicionalmente para forms con hx-post.
document.addEventListener('submit', function(e) {
  var form = e.target;
  if (form && form.tagName === 'FORM' && form.hasAttribute('hx-post')) {
    e.preventDefault();
    // Si HTMX está cargado, dispararlo manualmente; si no, no hacer nada (silencioso)
    if (window.htmx) {
      try { window.htmx.trigger(form, 'submit'); } catch (err) { console.warn('htmx.trigger error:', err); }
    }
  }
}, true); // captura en fase de captura, antes que cualquier otro handler

// GUARDIA ADICIONAL: prevenir Enter en inputs numéricos/text que dispara submit por defecto
document.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && e.target && e.target.tagName === 'INPUT') {
    var type = (e.target.type || '').toLowerCase();
    if (type === 'number' || type === 'text' || type === '') {
      var form = e.target.closest('form');
      if (form && form.hasAttribute('hx-post')) {
        e.preventDefault();
        // Disparar HTMX manualmente para que recalcule
        if (window.htmx) {
          try { window.htmx.trigger(form, 'submit'); } catch (err) {}
        }
      }
    }
  }
}, true);
